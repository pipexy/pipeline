#!/usr/bin/env python3
# examples/sql_adapter_example.py

from adapters.sql_adapter import SQLAdapter
import os
import sqlite3


# Helper function to create a sample database
def create_sample_database():
    db_path = "examples/data/sample.db"
    os.makedirs(os.path.dirname(db_path), exist_ok=True)

    # Create a new SQLite database
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Create tables
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS departments (
        id INTEGER PRIMARY KEY,
        name TEXT NOT NULL
    )
    ''')

    cursor.execute('''
    CREATE TABLE IF NOT EXISTS employees (
        id INTEGER PRIMARY KEY,
        first_name TEXT NOT NULL,
        last_name TEXT NOT NULL,
        email TEXT UNIQUE,
        hire_date TEXT,
        department_id INTEGER,
        salary REAL,
        FOREIGN KEY (department_id) REFERENCES departments (id)
    )
    ''')

    # Insert sample data for departments
    departments = [
        (1, "Engineering"),
        (2, "Marketing"),
        (3, "Finance"),
        (4, "Human Resources")
    ]

    cursor.executemany("INSERT OR REPLACE INTO departments VALUES (?, ?)", departments)

    # Insert sample data for employees
    employees = [
        (1, "John", "Smith", "john.smith@example.com", "2020-01-15", 1, 85000),
        (2, "Sarah", "Johnson", "sarah.j@example.com", "2019-05-20", 1, 92000),
        (3, "Michael", "Williams", "m.williams@example.com", "2021-02-10", 2, 78000),
        (4, "Emily", "Brown", "emily.brown@example.com", "2018-11-05", 3, 110000),
        (5, "David", "Jones", "david.jones@example.com", "2022-03-18", 1, 75000),
        (6, "Jessica", "Miller", "jessica.m@example.com", "2020-09-22", 4, 82000),
        (7, "Robert", "Davis", "robert.davis@example.com", "2017-07-30", 3, 125000),
        (8, "Jennifer", "Wilson", "j.wilson@example.com", "2021-11-15", 2, 76000)
    ]

    cursor.executemany('''
    INSERT OR REPLACE INTO employees 
    VALUES (?, ?, ?, ?, ?, ?, ?)
    ''', employees)

    # Commit and close
    conn.commit()
    conn.close()

    print(f"Sample database created at {db_path}")
    return db_path


# Example 1: Basic SQL query
def basic_query_example():
    print("\n--- SQL Adapter Example 1: Basic query ---")

    # Create sample database
    db_path = create_sample_database()

    # Initialize adapter
    adapter = SQLAdapter({})
    adapter.connection_string(f"sqlite:///{db_path}")

    # Run a simple query
    query = "SELECT * FROM employees ORDER BY last_name"
    adapter.query(query)

    result = adapter.execute()
    print(f"Query result (all employees ordered by last_name):\n{result}")


# Example 2: Parameterized query
def parameterized_query_example():
    print("\n--- SQL Adapter Example 2: Parameterized query ---")

    # Initialize adapter
    db_path = "examples/data/sample.db"  # Reuse the database from example 1
    adapter = SQLAdapter({})
    adapter.connection_string(f"sqlite:///{db_path}")

    # Parameterized query
    query = """
    SELECT e.id, e.first_name, e.last_name, d.name as department, e.salary
    FROM employees e
    JOIN departments d ON e.department_id = d.id
    WHERE e.department_id = :dept_id AND e.salary > :min_salary
    ORDER BY e.salary DESC
    """

    # Set parameters
    params = {
        "dept_id": 1,  # Engineering department
        "min_salary": 80000
    }

    adapter.query(query)
    adapter.parameters(params)

    result = adapter.execute()
    print(f"Parameterized query result (Engineering employees with salary > 80000):\n{result}")


# Example 3: Multiple operations in a transaction
def transaction_example():
    print("\n--- SQL Adapter Example 3: Transaction with multiple operations ---")

    # Initialize adapter
    db_path = "examples/data/sample.db"  # Reuse the database from example 1
    adapter = SQLAdapter({})
    adapter.connection_string(f"sqlite:///{db_path}")

    # Start a transaction
    adapter.begin_transaction()

    # Update salaries with a 10% raise for the Engineering department
    update_query = """
    UPDATE employees
    SET salary = salary * 1.1
    WHERE department_id = 1
    """

    adapter.query(update_query)
    adapter.execute()

    # Insert a new employee
    insert_query = """
    INSERT INTO employees (first_name, last_name, email, hire_date, department_id, salary)
    VALUES (:first_name, :last_name, :email, :hire_date, :department_id, :salary)
    """

    insert_params = {
        "first_name": "Alex",
        "last_name": "Thompson",
        "email": "alex.t@example.com",
        "hire_date": "2023-06-15",
        "department_id": 1,
        "salary": 88000
    }

    adapter.query(insert_query)
    adapter.parameters(insert_params)
    adapter.execute()

    # Commit the transaction
    adapter.commit_transaction()

    # Query to see the results
    result_query = """
    SELECT e.id, e.first_name, e.last_name, d.name as department, e.salary
    FROM employees e
    JOIN departments d ON e.department_id = d.id
    WHERE e.department_id = 1
    ORDER BY e.id
    """

    adapter.query(result_query)
    result = adapter.execute()
    print(f"Engineering department after transaction (with raises and new employee):\n{result}")


if __name__ == "__main__":
    print("Running SQLAdapter examples:")
    basic_query_example()
    parameterized_query_example()
    transaction_example()