""" 
writer.py
-------------------------
Handles writing processed Dataframes to CSV output files.
"""

from pathlib import Path

import pandas as pd

from src.utils.logger import get_logger
from src.utils.decorators import log_execution

logger = get_logger(__name__)


class CSVWriter:
    """ A writer for handling CSV file operations. """

    @log_execution
    def write_valid_records(self, df: pd.DataFrame, output_path: str) -> None:
        """ 
        Writes valid records to a CSV file.
        Args:
            df (pd.DataFrame): DataFrame containing valid records.
            output_path (str): Path to the output CSV file for valid records.
        """
        
        self._write_csv(df, output_path, "valid")

    @log_execution
    def write_invalid_records(self, df: pd.DataFrame, output_path: str) -> None:
        """ 
        Writes invalid(failed) records to a CSV file.
        Rows will include a ''failure_reason'' column indicating which validation(s) failed for each record.
        
        Args:
            df (pd.DataFrame): DataFrame containing invalid records.
            output_path (str): Path to the output CSV file for invalid records.
        """

        self._write_csv(df, output_path, "invalid")

    def _write_csv(self, df: pd.DataFrame, output_path: str, record_type: str) -> None:
        """ 
        Helper method to write DataFrame to CSV file with logging and error handling.
        
        Args:
            df (pd.DataFrame): DataFrame to be written to CSV.
            output_path (str): Path to the output CSV file.
            record_type (str): Type of records being written (e.g., "valid" or "invalid") for logging purposes.
        """
        logger.info(f"Writing {len(df)} {record_type} records to {output_path}...")
        try:
            output_dir = Path(output_path).parent
            output_dir.mkdir(parents=True, exist_ok=True)
            df.to_csv(output_path, index=False)
            logger.info(f"Successfully wrote {len(df)} {record_type} records to {output_path}.")
        except Exception as e:
            logger.error(f"Error writing {record_type} records to CSV: {e}")
            raise
