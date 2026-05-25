""" 
validator.py
------------------------- 
Orchestrates the validation logic using Great Expectations based on the rules defined in the configuration.

Design Notes:
- gx.get_context(mode="ephemeral") is used to create an in-memory Great Expectations context without the need for a full project setup, 
keeping the framework lightweight and focused on validation logic.
- ''ValidationResult'' is a typed dataclass - not a raw 'dict' 
Downstream classes (ResultProcessor,ExecutionSummary) can rely on a consistent structure for validation results,
improving code readability and maintainability.
- validate() does NOT write any files - that is writers job.
"""

from dataclasses import dataclass,field
from typing import Any,Dict,List
import great_expectations as gx
import pandas as pd

from src.core.expectation_factory import ExpectationFactory
from src.utils.config_loader import ValidationRule
from src.utils.logger import get_logger
from src.utils.decorators import log_execution

logger = get_logger(__name__)

@dataclass
class CheckResult:
    """" Represents the result of a single validation check. """
    check_type : str
    column : str
    passed : bool
    failed_row_count : int
    failed_indices : List[int] = field(default_factory=list)

@dataclass
class ValidationResult:
    """ Represents the overall result of validating a DataFrame against multiple rules. """
    total_rows: int
    check_results: List[CheckResult] = field(default_factory=list)
    
    @property
    def failed_indices(self) -> List[int]:
        """ Aggregates failed indices from all check results. """
        indices:set = set()
        for check in self.check_results:
            if not check.passed:
                indices.update(check.failed_indices)
        return sorted(indices)  # Return unique indices
    
    @property
    def total_checks(self) -> int:
        """ Returns the total number of validation checks performed. """
        return len(self.check_results)
    
    @property
    def passed_checks(self) -> int:
        """ Returns the number of checks that passed. """
        return sum(1 for check in self.check_results if check.passed)
    
    @property
    def failed_checks(self) -> int:
        """ Returns the number of checks that failed. """
        return self.total_checks - self.passed_checks

class DataValidator:
    """ A class responsible for validating data using Great Expectations based on provided configurations. """
    
    def __init__(self) -> None:
        self._factory = ExpectationFactory()
        
    @log_execution
    def validate(self, df: pd.DataFrame, rules: List[ValidationRule]) -> ValidationResult:
        """ 
        Executes validation rules against input dataframe using Great Expectations.
        
        Args:
            df (pd.DataFrame): Input DataFrame to be validated.
            rules (list[ValidationResult]): List of validation rules from configuration, 
            where each rule is a dictionary containing "type" and "column".
        
        Returns:
            ValidationResult: An object containing the validation results and summary statistics.
        """
        
        logger.info("Starting data validation...")

        # 1: Run GE for not_null and unique (returns row-level indices)
        ge_check_results = self._run_ge_checks(df, rules)

        # 2: Run Pandas dtype checks row-by-row
        dtype_check_results = self._run_dtype_checks(df, rules)

        all_check_results = ge_check_results + dtype_check_results

        result = ValidationResult(total_rows=len(df), check_results=all_check_results)
        logger.info(
            f"Validation completed - {result.passed_checks}/{result.total_checks} checks passed, "
            f"{len(result.failed_indices)} rows flagged."
        )
        return result

    def _run_ge_checks(
        self, df: pd.DataFrame, rules: List[ValidationRule]
    ) -> List[CheckResult]:
        """
        Runs not_null and unique checks through GE with result_format=COMPLETE
        so that unexpected_index_list is populated with exact row indices.
        """
        # Filter to only the check types GE handles with row-level indices
        ge_rules = [r for r in rules if r.type in ("not_null", "unique")]
        if not ge_rules:
            return []

        context = gx.get_context(mode="ephemeral")
        suite = self._factory.build_suite(suite_name="dq_suite_ge", rules=ge_rules)
        context.suites.add(suite)

        datasource = context.data_sources.add_pandas(name="pandas_ds")
        asset = datasource.add_dataframe_asset(name="input_asset")
        batch_def = asset.add_batch_definition_whole_dataframe(name="full_batch")

        validation_def = context.validation_definitions.add(
            gx.ValidationDefinition(
                name="dq_validation",
                data=batch_def,
                suite=suite,
            )
        )

        raw_result = validation_def.run(batch_parameters={"dataframe": df},result_format="COMPLETE",)
        return self._parse_ge_results(raw_result)

    def _parse_ge_results(self, raw_result: Any) -> List[CheckResult]:
        """Converts raw GE result into a list of typed CheckResult objects."""
        check_results: List[CheckResult] = []
        for exp_result in raw_result.results:
            cfg = exp_result.expectation_config
            col = getattr(cfg, "column", None) or cfg.kwargs.get("column", "unknown")
            failed_indices = exp_result.result.get("unexpected_index_list", []) or []
            check_results.append(CheckResult(
                check_type=cfg.type,
                column=col,
                passed=exp_result.success,
                failed_row_count=len(failed_indices),
                failed_indices=list(failed_indices),
            ))
        return check_results

    def _run_dtype_checks(
        self, df: pd.DataFrame, rules: List[ValidationRule]
    ) -> List[CheckResult]:
        """
        Runs dtype checks via Pandas coercion rather than GE column-dtype comparison.
        """
        dtype_rules = [r for r in rules if r.type == "datatype"]
        if not dtype_rules:
            return []

        check_results: List[CheckResult] = []

        for rule in dtype_rules:
            col = rule.column
            expected = (rule.expected_type or "").upper()

            if col not in df.columns:
                logger.warning(f"Column '{col}' not found in DataFrame - skipping dtype check.")
                continue

            failed_mask = self._get_dtype_failure_mask(df[col], expected)
            failed_indices = df[failed_mask].index.tolist()
            passed = len(failed_indices) == 0

            check_results.append(CheckResult(
                check_type="expect_column_values_to_be_of_type",
                column=col,
                passed=passed,
                failed_row_count=len(failed_indices),
                failed_indices=failed_indices,
            ))

            logger.debug(
                f"  dtype check [{col}] expected={expected} "
                f"- {len(failed_indices)} failing rows"
            )

        return check_results

    def _get_dtype_failure_mask(self, series: pd.Series, expected_type: str) -> pd.Series:
        """
        Returns a boolean mask - True where the value does NOT match expected_type.
        Skips null values (they are caught by not_null checks separately).
        """
        non_null = series.notna()

        if expected_type in ("INTEGER", "FLOAT"):
            coerced = pd.to_numeric(series, errors="coerce")
            # A cell fails if: it was not null AND coercion produced NaN
            return non_null & coerced.isna()

        elif expected_type == "STRING":
            # Every non-null value is a valid string - no rows fail
            return pd.Series(False, index=series.index)

        elif expected_type == "BOOLEAN":
            valid_bools = {"true", "false", "1", "0", "yes", "no"}
            return non_null & ~series.astype(str).str.lower().isin(valid_bools)

        elif expected_type == "DATE":
            coerced = pd.to_datetime(series, errors="coerce")
            return non_null & coerced.isna()

        else:
            logger.warning(f"Unknown expected_type '{expected_type}' - skipping mask.")
            return pd.Series(False, index=series.index)
