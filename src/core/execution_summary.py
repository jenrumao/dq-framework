""" 
execution_summary.py
--------------------------
Generates,prints and writes a structured exection summary report.
"""
from src.core.validator import ValidationResult
from src.utils.logger import get_logger
from datetime import datetime

import json
from pathlib import Path

logger = get_logger(__name__)

_REPORT_DIR = Path("reports")

class ExecutionSummary:
    """
    Generates execution summary for monitoring purposes. 
    """
    
    def generate(self,total_records: int,valid_records: int,invalid_records: int,validation_results: ValidationResult) -> dict:
        """ 
        Generates an execution summary report based on the provided metrics and validation results.
        
        Args:
            total_records (int): Total number of records processed.
            valid_records (int): Number of valid records.
            invalid_records (int): Number of invalid records.
            validation_results (ValidationResult): Typed result from DataValidator
        Returns:
            dict: A dictionary containing the execution summary report.
        """
        try:
            logger.info("Generating execution summary report...")

            summary = self._build_summary(total_records,valid_records,invalid_records,validation_results)
            self._print_summary(summary,validation_results)
            self._write_report(summary)
            logger.info("Execution summary report generated successfully.")
            return summary
        except Exception as e:
            logger.error(f"Error generating execution summary report: {e}")
            raise

    def _build_summary(self,total_records: int,valid_records: int,invalid_records: int,validation_results: ValidationResult) -> dict:
        pass_pct = round((valid_records/total_records *100),1) if total_records else 0
        
        return {
            "execution_timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "total_records": total_records,
            "valid_records": valid_records,
            "invalid_records": invalid_records,
            "pass_rate_pct": pass_pct,
            "total_checks": validation_results.total_checks,
            "passed_checks": validation_results.passed_checks,
            "failed_checks": validation_results.failed_checks,
            "check_details": [
                {
                    "check_type": cr.check_type,
                    "column": cr.column,
                    "passed": cr.passed,
                    "failed_row_count": cr.failed_row_count,
                }
                for cr in validation_results.check_results
            ],
        }

    def _print_summary(self, summary: dict, vr: ValidationResult) -> None:
        status = "PASSED" if summary["failed_checks"] == 0 else "FAILED"
        sep = "=" * 62

        print(f"\n{sep}")
        print(f"  DATA QUALITY EXECUTION SUMMARY")
        print(sep)
        print(f"  Timestamp   : {summary['execution_timestamp']}")
        print(f"  Status      : {status}")
        print(f"  Total rows  : {summary['total_records']:>8,}")
        print(f"  Valid rows  : {summary['valid_records']:>8,}  ({summary['pass_rate_pct']}%)")
        print(f"  Invalid rows: {summary['invalid_records']:>8,}")
        print(f"\n  Checks: {summary['passed_checks']} passed / {summary['failed_checks']} failed")
        print(f"  {'-' * 56}")
        for cr in vr.check_results:
            icon = "PASS" if cr.passed else f"FAIL ({cr.failed_row_count} rows)"
            print(f"  {'[OK]' if cr.passed else '[!!]'}  {cr.check_type:<42} [{cr.column}]  {icon}")
        print(f"{sep}\n")


    def _write_report(self, summary: dict) -> None:
        _REPORT_DIR.mkdir(parents=True, exist_ok=True)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        report_path = _REPORT_DIR / f"execution_summary_{timestamp}.json"

        try:
            with open(report_path, "w", encoding="utf-8") as f:
                json.dump(summary, f, indent=2)
            logger.info(f"Report written - {report_path}")
        except OSError as exc:
            logger.error(f"Failed to write report: {exc}")
            raise