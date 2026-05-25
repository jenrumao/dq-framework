# Data Quality Framework

A basic data quality framework implemented in Python with Pandas and Great Expectations.

The framework performs validation on input datasets with configurable rules and outputs the valid/invalid records separately.

---

## Features

- Metadata-driven validation rules using YAML files
- Great Expectations support
- Schema, null, range, regex, uniqueness validation
- Output separate files for valid and invalid records
- Validation summaries
- Logging and runtime information

---

## Project Structure
```yaml
src/
├── core/ # Validation functionality
├── io/ # Input/output helpers
├── utils/ # Configuration/logging support
├── reporting/ # Validation summary reports
├── expectations/ # Mappings to great_expectations
└── config/ # Configuration for validations
```
---

## How It Works

1. Load dataset
2. Load validation rules from YAML
3. Run validations using Great Expectations
4. Split valid and invalid records
5. Generate validation summary report

## Running The project

Install dependencies:
pip install -r requirements.txt

Run:
python main.py

## Example Validation Rules

```yaml
columns:
  employee_id:
    nullable: false
    unique: true

  salary:
    min_value: 0
```

## Output:

The framework generates:

- Valid records CSV
- InValid records CSV
- Validation report
- Execution logs
