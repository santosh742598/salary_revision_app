from reportlab.lib import colors
from reportlab.lib.pagesizes import A2
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.units import inch
import pandas as pd
import os

from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont



# Register font
pdfmetrics.registerFont(TTFont('DejaVu', os.path.join("fonts", "DejaVuSans.ttf")))



# Get base styles
styles = getSampleStyleSheet()

# Define custom style using DejaVu font
normal_dejavu = ParagraphStyle(
    name="NormalDejaVu",
    parent=styles["Normal"],
    fontName="DejaVu",
    fontSize=10,
)



def format_currency(value):
    try:
        return f"₹{int(value):,}"
    except:
        return value


def generate_individual_pdf(df: pd.DataFrame, sap_no: str, fitment_pct: float, oa_pct: float, summary_df: pd.DataFrame, output_path: str = None) -> str:
    if output_path is None:
        output_dir = "generated_pdfs"
        os.makedirs(output_dir, exist_ok=True)
        output_path = os.path.join(output_dir, f"draft_3rd_prc_revision_{sap_no}.pdf")

    emp_info = df.iloc[0]
    sap_no = emp_info.get("Employee No", "N/A")
    name = emp_info.get("Name", "N/A")
    status = emp_info.get("Status", "N/A")

    total_with_hra = format_currency(df["Delta With HRA"].sum())
    total_without_hra = format_currency(df["Delta Without HRA"].sum())

    rename_map = {
        "Employee No": "Emp No",
        "Pay Scale Group": "Group",
        "Other Allowance percentage": "OA %",
        "Other Allowance": "OA",
        "HRA percentage": "HRA %",
    }
    df = df.rename(columns=rename_map)

    df = df.applymap(lambda x: str(x)[:15])
    df = df.drop(columns=["Emp No", "Name", "Status"], errors="ignore")

    doc = SimpleDocTemplate(output_path, pagesize=A2, title=f"Draft 3rd PRC revision in respect of {name}, SAP No. {sap_no}")
    styles = getSampleStyleSheet()
    elements = []

    elements.append(Paragraph(f"<b>Draft 3rd PRC revision in respect of {name}, SAP No. {sap_no}</b>", styles["Title"]))
    elements.append(Spacer(1, 0.2 * inch))
    elements.append(Paragraph(f"<b>Status:</b> {status}", styles["Normal"]))
    elements.append(Paragraph(f"<b>Fitment %:</b> {fitment_pct}%", styles["Normal"]))
    elements.append(Paragraph(f"<b>OA %:</b> {oa_pct}%", styles["Normal"]))
    elements.append(Spacer(1, 0.2 * inch))

    elements.append(Paragraph(f"<b>Total Delta With HRA:</b> {total_with_hra}", normal_dejavu))
    elements.append(Paragraph(f"<b>Total Delta Without HRA:</b> {total_without_hra}", normal_dejavu))


    elements.append(Spacer(1, 0.2 * inch))


    # Summary section
    summary_rows = df[["Year", "Delta With HRA", "Delta Without HRA"]].groupby("Year").sum().reset_index()
    summary_rows["Delta With HRA"] = summary_rows["Delta With HRA"].apply(lambda x: format_currency(x))
    summary_rows["Delta Without HRA"] = summary_rows["Delta Without HRA"].apply(lambda x: format_currency(x))

    summary_df["Delta With HRA"] = summary_df["Delta With HRA"].apply(format_currency)
    summary_df["Delta Without HRA"] = summary_df["Delta Without HRA"].apply(format_currency)

    elements.append(Spacer(1, 0.3 * inch))
    elements.append(Paragraph("<b>Year-wise Delta Impact:</b>", styles["Heading2"]))
    summary_table_data = [summary_df.columns.tolist()] + summary_df.values.tolist()
    summary_table = Table(summary_table_data, repeatRows=1)
    summary_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.beige),
        ('FONTNAME', (0, 0), (-1, -1), 'DejaVu'),
        ('FONTSIZE', (0, 0), (-1, -1), 8),
        ('GRID', (0, 0), (-1, -1), 0.25, colors.grey),
    ]))
    elements.append(summary_table)

    #table



    elements.append(Paragraph("<b>Revised Monthly Salary Data:</b>", styles["Heading2"]))
    table_data = [df.columns.tolist()] + df.values.tolist()
    table = Table(table_data, repeatRows=1)
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.lightblue),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.black),
        ('FONTNAME', (0, 0), (-1, -1), 'DejaVu'),
        ('FONTSIZE', (0, 0), (-1, -1), 7),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 5),
        ('GRID', (0, 0), (-1, -1), 0.25, colors.grey),
    ]))
    elements.append(table)

    elements.append(Spacer(1, 0.3 * inch))
    elements.append(Paragraph("<i>This report is a notional calculation based on available data and is not legally binding. For information purposes only.</i>", styles["Normal"]))

    doc.build(elements)
    return output_path
