""" 
expectation_factory.py
----------------------
Creates GE validation rules

Design notes:
- ExpectationFactory builds an ExpectationSuite from a list of ValidationRule objects . It owns all GE knowledge .
- Dtype validation is handled here , the dtype_map translates human-readable config types to the pandas dtype string that GE understands 
"""

from typing import Dict,List

import great_expectations as gx
from great_expectations import ExpectationSuite

from src.utils.config_loader import ValidationRule
from src.utils.logger import get_logger

logger = get_logger(__name__)

# maps YAML config dtype strings -> pandas dtype strings recognised by GE
DTYPE_MAP: Dict[str,str] = {
    "INTEGER" : "int64",
    "FLOAT" : "float64",
    "STRING" : "object",
    "BOOLEAN": "bool",
    "DATE" : "datetime64[ns]"
}

class ExpectationFactory:
    """ 
    Factory class to apply Great Expectations validations based on configuration rules. 
    """
    
    def __init__(self) -> None:
        self._builders = {
            "not_null": self._build_not_null,
            "unique": self._build_unique,
            "datatype": self._build_datatype,
        }
        
    def build_suite(self, suite_name:str,rules:List[ValidationRule]) -> ExpectationSuite:
        """ 
        Builds a ExpectationSuite from a list of validation rules
        
        Args:
            suite_name: A unique name for the suite (used by GE context).
            rules: List of ValidationRule dataclass instances.

        Returns:
            ExpectationSuite: Ready to be registered with a GE context.

        Raises:
            ValueError: If a rule references an unsupported validation type.
        """
        
        suite = gx.ExpectationSuite(name=suite_name)
        
        for rule in rules:
            builder = self._builders.get(rule.type)
            if builder is None:
                raise ValueError(f"Unsupported validation type: '{rule.type}' ."
                                 f"Suported types: {list(self._builders.keys())}")
            expectation = builder(rule)
            suite.add_expectation(expectation)
            logger.debug(f" + {rule.type} check on column ' {rule.column}'")
            
        logger.info(f"Built suite '{suite_name}' - {len(suite.expectations)} expectations"
                    f"across {len(rules)} rules.")
        
        return suite
    
    def _build_not_null(self,rule:ValidationRule):
        return gx.expectations.ExpectColumnValuesToNotBeNull(column=rule.column)
    
    def _build_unique(self,rule:ValidationRule):
        return gx.expectations.ExpectColumnValuesToBeUnique(column=rule.column)
    
    def _build_datatype(self,rule:ValidationRule):
        if rule.expected_type is None:
            raise ValueError(
                f"Validation rule for column '{rule.column}' has type 'datatype' but 'expected_type' is not set in config"
            )
        pandas_type = DTYPE_MAP.get(rule.expected_type.upper())
        if pandas_type is None:
            raise ValueError(f"Unknown expected_type '{rule.expected_type}' for column '{rule.column}'. Supported : {list(DTYPE_MAP.keys())}")
        return gx.expectations.ExpectColumnValuesToBeOfType(column=rule.column,type_=pandas_type)
    