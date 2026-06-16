import sqlite3
import pandas as pd

conn = sqlite3.connect("../payroll.db")

employee_code = "CSRPL0030"

query = """
SELECT *
FROM employees
WHERE employee_code = ?
"""

df = pd.read_sql_query(
    query,
    conn,
    params=(employee_code,)
)

conn.close()

print(df[[
    "employee_name",
    "designation",
    "basic",
    "employee_pf",
    "net_take_home",
    "ctc"
]])