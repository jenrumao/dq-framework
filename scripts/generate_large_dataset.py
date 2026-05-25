import sys

from faker import Faker
import pandas as pd
import random
from pathlib import Path

fake = Faker()

OUTPUT_FILE= Path("data/raw/generated_airline_employee_data.csv")

DEPARTMENTS = [
    "HR",
    "Engineering",
    "Cabin Crew",
    "Pilots",
    "Ground Staff",
    "Customer Service",
]

def generate_large_dataset(total_records: int = 10000) -> pd.DataFrame:

    """ 
    Generates a large synthetic dataset of airline employee records with various data quality issues for testing the data quality framework.
    The generates dataset contains : Valid records, Null values, Duplicate records, Invalid data types for salary and age, Invalid joining dates.
    
    Args:
        total_records (int): The total number of records to generate in the dataset. Default is 10,000.
        
    Returns:
        pd.DataFrame: A DataFrame containing the generated dataset with injected data quality issues.
    """

    records = []

    # Generate synthetic employee records
    
    for emp_id in range(1001, 1001 + total_records):

        record = {
            "employee_id": emp_id,
            "employee_name": fake.name(),
            "department": random.choice(DEPARTMENTS),
            "salary": random.randint(30000, 120000),
            "age": random.randint(22, 65),
            "email": fake.email(),
            "joining_date": fake.date_between(start_date="-10y", end_date="today"),
        }
        records.append(record)

    df = pd.DataFrame(records)

    ## Inject Nulls

    null_indices = random.sample(range(total_records), min(100, total_records))  # Randomly select 100 indices to be null

    for idx in null_indices:
        column = random.choice(
            ["employee_name", "department", "email"]
        )  # Randomly select a column to be null

        df.loc[idx, column] = None  # Set the selected column to null for the selected index

    ## Inject duplicate records

    duplicate_indices = random.sample(range(total_records), min(50, total_records))  # Randomly select 50 indices to be duplicated

    for idx in duplicate_indices:
        duplicate_from = random.randint(
            0, total_records - 1
        )  # Randomly select an index to duplicate from
        df.loc[idx, "employee_id"] = df.loc[
            duplicate_from, "employee_id"
        ]  # Duplicate the employee_id for the selected index

    ## Inject invalid salary dtypes

    salary_error_indices = random.sample(range(total_records), min(30, total_records))  # Randomly select 30 indices to have invalid salary dtypes

    for idx in salary_error_indices:
        df.loc[idx, "salary"] = (
            fake.word()
        )  # Set the salary to a random word (invalid dtype)


    ## Inject invalid age dtypes

    age_error_indices = random.sample(range(total_records), min(30, total_records))  # Randomly select 30 indices to have invalid age dtypes

    for idx in age_error_indices:
        df.loc[idx, "age"] = fake.word()  # Set the age to a random word (invalid dtype)

    ## Inject invalid joining dates

    date_error_indices = random.sample(range(total_records), min(20, total_records))  # Randomly select 20 indices to have invalid joining dates

    for idx in date_error_indices:
        df.loc[idx, "joining_date"] = (
            fake.word()
        )  # Set the joining date to a random word (invalid dtype)


    OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(OUTPUT_FILE, index=False)

    print(f"Generated dataset with {total_records} records at {OUTPUT_FILE}")
    print(
        f"Injected {len(null_indices)} null values, {len(duplicate_indices)} duplicate records, {len(salary_error_indices)} invalid salary dtypes, {len(age_error_indices)} invalid age dtypes, and {len(date_error_indices)} invalid joining dates."
    )


if __name__ == "__main__":
    
    total_records = 10000  # Default number of records

    if len(sys.argv) > 1:
        try:
            total_records = int(sys.argv[1])
        except ValueError:
            print("Invalid input for total records. Using default value of 10000.")

    generate_large_dataset(total_records)