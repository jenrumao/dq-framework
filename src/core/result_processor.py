"""
result_processor.py
-------------------
Splits a DataFrame into valid / invalid subsets based on ValidationResult,
and enriches failed rows with human-readable failure reasons.

Design notes:
- ResultProcessor does NOT re-implement validation logic. It consumes the ValidationResult produced by DataValidator - which already contains
  the exact set of failed row indices per check. 
- A row may fail MULTIPLE checks (e.g. null AND wrong dtype). The failure_reason column captures ALL violations for a row, joined by
  " | ", so downstream teams can remediate accurately.
- valid_df deliberately does NOT include the failure_reason column , it should be indistinguishable from the original clean data.
"""

from collections import defaultdict
from typing import Dict, List, Tuple

import pandas as pd

from src.core.validator import ValidationResult, CheckResult
from src.utils.decorators import log_execution
from src.utils.logger import get_logger

logger = get_logger(__name__)


class ResultProcessor:
    """
    Separates a DataFrame into valid and invalid records based on a ValidationResult, and annotates each failed row with the reason(s) for failure.
    """

    @log_execution
    def process_results(
        self,
        df: pd.DataFrame,
        validation_result: ValidationResult,
    ) -> Tuple[pd.DataFrame, pd.DataFrame]:
        """
        Splits df into valid and invalid DataFrames.

        Args:
            df: Original input DataFrame.
            validation_result: Typed result from DataValidator.validate().

        Returns:
            Tuple of (valid_df, invalid_df).
            invalid_df contains an extra failure_reason column.
        """
        logger.info("Separating valid and invalid records...")

        # Aggregate all failure reasons per row index
        # A single row can fail multiple checks - capture all of them.
        failure_reasons: Dict[int, List[str]] = defaultdict(list)

        for check in validation_result.check_results:
            if not check.passed:
                reason = f"{check.check_type}({check.column})"
                for idx in check.failed_indices:
                    failure_reasons[idx].append(reason)

        failed_indices = sorted(failure_reasons.keys())

        invalid_df = df.loc[failed_indices].copy()
        invalid_df["failure_reason"] = invalid_df.index.map(lambda idx: " | ".join(failure_reasons[idx]))
        valid_df = df.drop(index=failed_indices)
        logger.info(f"Split complete - "f"{len(valid_df):,} valid rows, {len(invalid_df):,} invalid rows.")
        return valid_df, invalid_df
