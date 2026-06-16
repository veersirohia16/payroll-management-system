from payslip_generator_v2 import generate_payslip
import sqlite3
import pandas as pd

conn = sqlite3.connect("../payroll.db")

df = pd.read_sql_query(
    "SELECT employee_code FROM employees",
    conn
)

conn.close()

for code in df["employee_code"]:

    try:
        generate_payslip(code)
        print(f"Done : {code}")

    except Exception as e:
        print(f"Error : {code}")
        print(e)

print("All Payslips Generated")