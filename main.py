""" 
    Entry point for the data quality framework.
    
    Workflow : 
    1. Load configuration from YAML file.
    2. Read input dataset using CSVReader.
    3. Run data quality validations using DataValidator.
    4. Process validation results to separate valid and invalid records using ResultProcessor.
    5. Write valid and invalid records to separate CSV files using CSVWriter.
    6. Generate and log execution summary report using ExecutionSummary.
    
    Design notes: 
    - main() is deliberately thin to wire components together and handles top-level error propogation. 
    No business logic lives here .
    - Non-zero exit code (sys.exit(1)) on unandled exceptions ensures CI/CD pipelines can detect failures and trigger alerts.
    - Extensive logging at each step provides visibility into the execution flow and aids in debugging and monitoring
"""

import sys
from src.utils.logger import get_logger
from src.utils.config_loader import load_config

from src.io.reader import CSVReader
from src.io.writer import CSVWriter

from src.core.validator import DataValidator
from src.core.result_processor import ResultProcessor
from src.core.execution_summary import ExecutionSummary

logger = get_logger(__name__)

CONFIG_PATH = "config/validation_config.yaml"

def main() -> None:
    """ 
    Runs validation checks using Great Expectations.
    Raises system exit with code 1 on unhandled failures.
    """
    
    try:
        logger.info("=" * 60)
        logger.info("  DQ Framework - Starting")
        logger.info("=" * 60)

        # 1. Load config
        config = load_config(CONFIG_PATH)

        # 2. Read
        reader = CSVReader()
        df = reader.read(config.input_file)

        # 3. Validate
        validator = DataValidator()
        validation_results = validator.validate(df, config.validations)

        # 4. Split
        processor = ResultProcessor()
        valid_df, invalid_df = processor.process_results(df, validation_results)

        # 5. Write
        writer = CSVWriter()
        writer.write_valid_records(valid_df, config.output_valid_file)
        writer.write_invalid_records(invalid_df, config.output_invalid_file)

        # 6. Report
        summary_generator = ExecutionSummary()
        summary = summary_generator.generate(
            total_records=len(df),
            valid_records=len(valid_df),
            invalid_records=len(invalid_df),
            validation_results=validation_results,
        )

        logger.info(f"Execution Summary: {summary}")
        logger.info("Data quality framework execution completed.")
    
    except FileNotFoundError as fnf_error:
        logger.error(f"File not found: {fnf_error}")
        sys.exit(1)
    except Exception as e:    
        logger.error(f"An error occurred during framework execution: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
