""" 
config_loader.py
-------------------------
Loads YAML validation configuration
"""
from dataclasses import dataclass,field
from pathlib import Path
from typing import List, Optional

import yaml

from src.utils.logger import get_logger
from src.utils.decorators import log_execution

logger = get_logger(__name__)

@dataclass
class ValidationRule:
    """ Represents a single validation rule from the configuration. """
    type: str
    column: str
    expected_type: Optional[str] = None  # Only used for datatype validation
    
@dataclass
class AppConfig:
    """ Represents the application configuration loaded from YAML. """
    input_file: str
    output_valid_file: str
    output_invalid_file: str
    validations: List[ValidationRule] = field(default_factory=list)

@log_execution
def load_config(config_path: str) -> AppConfig:
    """ 
    Loads YAML configuration file and returns it as an AppConfig instance.
    
    Args:
        config_path (str): Path to the YAML configuration file.
    Returns:
        AppConfig: Configuration parameters loaded from the YAML file.
        
    Raises:
        FileNotFoundError: If the configuration file does not exist.
        KeyError: If required configuration keys are missing.
    """
    path = Path(config_path)
    if not path.exists():
        logger.error(f"Configuration file not found at {config_path}")
        raise FileNotFoundError(f"Configuration file not found at {config_path}")
    
    logger.info(f"Loading configuration from {config_path}...")
    with open(config_path, "r") as file:
            config : dict = yaml.safe_load(file)
            
    rules = [ValidationRule(type=rule["type"], column=rule["column"], expected_type=rule.get("expected_type")) 
             for rule in config.get("validations", [])]
    
    config = AppConfig(
        input_file=config["input_file"],
        output_valid_file=config["output_valid_file"],
        output_invalid_file=config["output_invalid_file"],
        validations=rules
    )
    
    logger.info(f"Configuration loaded successfully. {len(rules)} validation rules found.")
    return config
