import sqlite3
import pandas as pd
import os

from reportlab.platypus import (
    SimpleDocTemplate,
    Table,
    TableStyle,
    Paragraph,
    Spacer,
    Image
)

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.lib.styles import getSampleStyleSheet
from num2words import num2words


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
        print("Employee Not Found")
        return

    os.makedirs("../generated_payslips", exist_ok=True)

    pdf_path = f"../generated_payslips/{employee_code}.pdf"

    pdf = SimpleDocTemplate(
        pdf_path,
        pagesize=A4,
        topMargin=18 * mm,
        bottomMargin=18 * mm,
        leftMargin=18 * mm,
        rightMargin=18 * mm
    )

    styles = getSampleStyleSheet()

    title_style = styles["Normal"].clone("title")
    title_style.fontName = "Helvetica-Bold"
    title_style.fontSize = 16
    title_style.leading = 19

    sub_style = styles["Normal"].clone("sub")
    sub_style.fontName = "Helvetica-Bold"
    sub_style.fontSize = 9
    sub_style.leading = 12

    addr_style = styles["Normal"].clone("addr")
    addr_style.fontSize = 8.5
    addr_style.leading = 12

    small_style = styles["Normal"].clone("small")
    small_style.fontSize = 8.5
    small_style.leading = 11

    elements = []

    # ==========================
    # HEADER
    # ==========================

    logo = Image(
        "company_logo.png",
        width=55,
        height=55
    )

    header_left = Paragraph(
        """
        <b>CS RETAIL PVT. LTD.</b><br/>
        <b>Unit Of CS GROUP</b><br/>
        Head Office: 100/6 Alipore Road | Kolkata 700 027 | Ph: 033 2448 3027<br/>
        Regd Office: CS Towers | 3A Camac Street | Kolkata 700 016
        """,
        addr_style
    )

    header_data = [[header_left, logo]]

    header_table = Table(
        header_data,
        colWidths=[440, 60]
    )

    header_table.setStyle(
        TableStyle([
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('TOPPADDING', (0, 0), (-1, -1), 0),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 0),
            ('LEFTPADDING', (0, 0), (0, 0), 0),
        ])
    )

    elements.append(header_table)
    elements.append(Spacer(1, 6))

    # ==========================
    # EMPLOYEE DETAILS
    # ==========================

    emp_data = [
        ["EMPLOYEE NAME:", emp["employee_name"]],
        ["EMPLOYEE CODE:", emp["employee_code"]],
        ["DESIGNATION:", emp["designation"]],
        ["DATE OF JOINING:", str(emp["date_of_joining"])[:10]],
        ["PAYABLE MONTH:", emp["month"]],
        ["TOTAL WORKING DAYS:", int(emp["att"]) + int(emp["off_day"])],
        ["TOTAL PAYABLE DAYS:", int(emp["att"])],
        ["OFF DAY PAY OUT:", int(emp["off_day"])],
        ["PLACE OF POSTING:", emp["location"]],
        ["STATES:", emp["state"]],
        ["OUTLET:", emp["outlet"]],
        ["BANK ACCOUNT NO:", str(emp["account_number"])],
        ["MODE OF TRANSFER:", emp["mode_of_payment"]],
        ["UAN NO:", str(emp["uan_no"])],
        ["PF NO:", str(emp["pf_no"])],
        ["ESIC NO:", str(emp["esic_no"])]
    ]

    employee_table = Table(
        emp_data,
        colWidths=[140, 360]
    )

    employee_table.setStyle(
        TableStyle([
            ('BOX', (0, 0), (-1, -1), 1, colors.black),
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 8.5),
            ('TOPPADDING', (0, 0), (-1, -1), 1.5),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 1.5),
            ('LEFTPADDING', (0, 0), (-1, -1), 4),
        ])
    )

    elements.append(employee_table)
    elements.append(Spacer(1, 8))

    # ==========================
    # EARNINGS TABLE (with double AMOUNT columns like sample)
    # ==========================

    off_day_payout_amount = float(emp["off_day"]) * (float(emp["basic"]) / 26) \
        if "off_day" in emp and emp["off_day"] not in (None, "") else 0

    salary_data = [
        ["PARTICULARS", "AMOUNT", "AMOUNT"],
        ["BASIC", emp["basic"], emp["basic"]],
        ["HOUSE RENT ALLOWANCE", emp["house_rent_allowance"], emp["house_rent_allowance"]],
        ["CONVEYANCE ALLOWANCE", emp["conveyance"], emp["conveyance"]],
        ["FOOD ALLOWANCE", emp["food_allowance"], emp["food_allowance"]],
        ["BONUS", emp["bonus"], emp["bonus"]],
        ["OFF DAY PAY OUT", 0, round(off_day_payout_amount)],
        ["INCENTIVE", 0, 0]
    ]

    salary_table = Table(
        salary_data,
        colWidths=[280, 110, 110]
    )

    salary_table.setStyle(
        TableStyle([
            ('BOX', (0, 0), (-1, -1), 1, colors.black),
            ('INNERGRID', (0, 0), (-1, -1), 0.5, colors.black),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
            ('ALIGN', (1, 1), (-1, -1), 'CENTER'),
            ('FONTSIZE', (0, 0), (-1, -1), 8.5),
            ('TOPPADDING', (0, 0), (-1, -1), 1.5),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 1.5),
            ('LEFTPADDING', (0, 0), (0, -1), 4),
        ])
    )

    elements.append(salary_table)

    # ==========================
    # GROSS SALARY
    # ==========================

    gross_salary = (
        float(emp["basic"])
        + float(emp["house_rent_allowance"])
        + float(emp["conveyance"])
        + float(emp["food_allowance"])
        + float(emp["bonus"])
        + off_day_payout_amount
    )

    gross_table = Table(
        [
            ["ACTUAL GROSS SALARY", "", round(gross_salary)]
        ],
        colWidths=[280, 110, 110]
    )

    gross_table.setStyle(
        TableStyle([
            ('BOX', (0, 0), (-1, -1), 1, colors.black),
            ('LINEAFTER', (0, 0), (0, 0), 1, colors.black),
            ('FONTNAME', (0, 0), (-1, -1), 'Helvetica-Bold'),
            ('ALIGN', (2, 0), (2, 0), 'CENTER'),
            ('FONTSIZE', (0, 0), (-1, -1), 8.5),
            ('TOPPADDING', (0, 0), (-1, -1), 1.5),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 1.5),
            ('LEFTPADDING', (0, 0), (0, 0), 4),
        ])
    )

    elements.append(gross_table)
    elements.append(Spacer(1, 8))

    # ==========================
    # DEDUCTIONS TABLE
    # ==========================

    deduction_data = [
        ["DEDUCTIONS:", ""],
        ["EMPLOYEE PF", emp["employee_pf"]],
        ["EMPLOYEE ESIC", emp["employee_esic"]],
        ["PROFESSIONAL TAX", emp["p_tax"]],
        ["TDS", 0],
        ["ADVANCE SALARY", 0]
    ]

    deduction_table = Table(
        deduction_data,
        colWidths=[280, 220]
    )

    deduction_table.setStyle(
        TableStyle([
            ('BOX', (0, 0), (-1, -1), 1, colors.black),
            ('LINEBELOW', (0, 0), (-1, 0), 1, colors.black),
            ('LINEAFTER', (0, 1), (0, -1), 1, colors.black),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('ALIGN', (1, 1), (1, -1), 'CENTER'),
            ('FONTSIZE', (0, 0), (-1, -1), 8.5),
            ('TOPPADDING', (0, 0), (-1, -1), 1.5),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 1.5),
            ('LEFTPADDING', (0, 0), (0, -1), 4),
        ])
    )

    elements.append(deduction_table)

    # ==========================
    # TOTAL DEDUCTION
    # ==========================

    total_deduction = (
        float(emp["employee_pf"])
        + float(emp["employee_esic"])
        + float(emp["p_tax"])
    )

    total_deduction_table = Table(
        [
            ["TOTAL DEDUCTION", round(total_deduction)]
        ],
        colWidths=[280, 220]
    )

    total_deduction_table.setStyle(
        TableStyle([
            ('BOX', (0, 0), (-1, -1), 1, colors.black),
            ('LINEAFTER', (0, 0), (0, 0), 1, colors.black),
            ('FONTNAME', (0, 0), (-1, -1), 'Helvetica-Bold'),
            ('ALIGN', (1, 0), (1, 0), 'CENTER'),
            ('FONTSIZE', (0, 0), (-1, -1), 8.5),
            ('TOPPADDING', (0, 0), (-1, -1), 1.5),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 1.5),
            ('LEFTPADDING', (0, 0), (0, 0), 4),
        ])
    )

    elements.append(total_deduction_table)

    # ==========================
    # NET SALARY
    # ==========================

    net_table = Table(
        [
            ["NET TAKE HOME SALARY", emp["net_take_home"]]
        ],
        colWidths=[280, 220]
    )

    net_table.setStyle(
        TableStyle([
            ('BOX', (0, 0), (-1, -1), 1, colors.black),
            ('LINEAFTER', (0, 0), (0, 0), 1, colors.black),
            ('FONTNAME', (0, 0), (-1, -1), 'Helvetica-Bold'),
            ('ALIGN', (1, 0), (1, 0), 'CENTER'),
            ('BACKGROUND', (0, 0), (-1, -1), colors.lightgrey),
            ('FONTSIZE', (0, 0), (-1, -1), 9),
            ('TOPPADDING', (0, 0), (-1, -1), 1.5),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 1.5),
            ('LEFTPADDING', (0, 0), (0, 0), 4),
        ])
    )

    elements.append(net_table)

    # ==========================
    # AMOUNT IN WORDS
    # ==========================

    salary_words = num2words(int(emp["net_take_home"])).title()

    words_table = Table(
        [
            [Paragraph("Amount in Words:-", small_style)],
            [Paragraph(f"Rupees {salary_words} Only", small_style)]
        ],
        colWidths=[500]
    )

    words_table.setStyle(
        TableStyle([
            ('BOX', (0, 0), (-1, -1), 1, colors.black),
            ('TOPPADDING', (0, 0), (-1, -1), 1.5),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 1.5),
            ('LEFTPADDING', (0, 0), (-1, -1), 4),
        ])
    )

    elements.append(words_table)

    # ==========================
    # FOOTER
    # ==========================

    elements.append(Spacer(1, 10))
    elements.append(
        Paragraph(
            "**This is system generated Pay slip and doesn't require any signature.",
            small_style
        )
    )

    pdf.build(elements)

    print("Payslip Generated:", pdf_path)


if __name__ == "__main__":
    employee_code = input("Enter Employee Code: ")
    generate_payslip(employee_code)