""" 
reader.py
-------------------------
Handles reading input CSV files into DataFrames.
"""
from pathlib import Path
import pandas as pd

from src.utils.logger import get_logger
from src.utils.decorators import log_execution

logger = get_logger(__name__)

class CSVReader:
    """ A reader for handling CSV file operations. """
    
    @log_execution
    def read(self, file_path: str) -> pd.DataFrame:
        """ 
        Reads a CSV file and returns it as a pandas DataFrame.
        
        Args:
            file_path (str): Path to the CSV file.
            
        Returns:
            pd.DataFrame: DataFrame containing the CSV data.
            
        Raises:
            FileNotFoundError: If the specified CSV file does not exist.
        """
        
        path = Path(file_path)
        if not path.is_file():
            logger.error(f"CSV file not found at {file_path}")
            raise FileNotFoundError(f"CSV file not found at {file_path}")
        
        logger.info(f"Reading CSV file from {file_path}...")
        df = pd.read_csv(file_path)
        logger.info(f"Successfully read {len(df)} records from {file_path}.")
        return df