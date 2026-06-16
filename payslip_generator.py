import sqlite3
import pandas as pd
import os

from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer
)

from reportlab.lib.styles import getSampleStyleSheet


def get_employee(employee_code):

    conn = sqlite3.connect("../payroll.db")

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

    if df.empty:
        return None

    return df.iloc[0]


def generate_payslip(employee_code):

    emp = get_employee(employee_code)

    if emp is None:
        print("Employee not found")
        return

    os.makedirs("../generated_payslips", exist_ok=True)

    pdf_path = f"../generated_payslips/{employee_code}.pdf"

    pdf = SimpleDocTemplate(pdf_path)

    styles = getSampleStyleSheet()

    content = []

    content.append(
        Paragraph("CS Retail", styles["Title"])
    )

    content.append(Spacer(1, 12))

    content.append(
        Paragraph("Employee Payslip", styles["Heading2"])
    )

    content.append(Spacer(1, 12))

    content.append(
        Paragraph(
            f"Employee Name: {emp['employee_name']}",
            styles["Normal"]
        )
    )

    content.append(
        Paragraph(
            f"Employee Code: {emp['employee_code']}",
            styles["Normal"]
        )
    )

    content.append(
        Paragraph(
            f"Designation: {emp['designation']}",
            styles["Normal"]
        )
    )

    content.append(
        Paragraph(
            f"Location: {emp['location']}",
            styles["Normal"]
        )
    )

    content.append(
        Paragraph(
            f"Basic Salary: ₹{emp['basic']}",
            styles["Normal"]
        )
    )

    content.append(
        Paragraph(
            f"Employee PF: ₹{emp['employee_pf']}",
            styles["Normal"]
        )
    )

    content.append(
        Paragraph(
            f"Net Salary: ₹{emp['net_take_home']}",
            styles["Normal"]
        )
    )

    content.append(
        Paragraph(
            f"CTC: ₹{emp['ctc']}",
            styles["Normal"]
        )
    )

    pdf.build(content)

    print(f"Payslip Generated: {pdf_path}")


print("Script Started")
employee_code = input("Enter Employee Code: ")
generate_payslip(employee_code)