from reportlab.lib import colors
from reportlab.lib.pagesizes import A2
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image
from reportlab.lib.units import inch
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

from matplotlib import pyplot as plt
import matplotlib.ticker as mtick
import pandas as pd
import io
import os

from reportlab.lib.colors import HexColor

from babel.numbers import format_currency as babel_format_currency

def format_currency(value):
    try:
        value = float(value)
        return babel_format_currency(value, 'INR', locale='en_IN').replace('.00', '')
    except:
        return value


# Register font relative to this module
FONT_PATH = os.path.join(os.path.dirname(__file__), "..", "fonts", "DejaVuSans.ttf")
pdfmetrics.registerFont(TTFont("DejaVu", FONT_PATH))

# Get base styles
styles = getSampleStyleSheet()

# Define custom style using DejaVu font
normal_dejavu = ParagraphStyle(
    name="NormalDejaVu",
    parent=styles["Normal"],
    fontName="DejaVu",
    fontSize=10,
)






def generate_individual_pdf(df: pd.DataFrame, sap_no: str, fitment_pct: float, oa_pct: float, summary_df: pd.DataFrame, output_path: str = None) -> str:
    if output_path is None:
        output_dir = "generated_pdfs"
        os.makedirs(output_dir, exist_ok=True)
        output_path = os.path.join(output_dir, f"draft_3rd_prc_revision_{sap_no}.pdf")

    light_blue_heading = ParagraphStyle(
        name="LightBlueHeading",
        parent=styles["Title"],
        fontName="DejaVu",
        textColor=HexColor("#1F75FE"),  # Light blue
        fontSize=18,
    )

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
    elements = []



    elements.append(Paragraph(
        f"<b>Draft 3rd PRC revision in respect of {name}, SAP No. {sap_no}</b>",
        light_blue_heading
    ))
    elements.append(Spacer(1, 0.2 * inch))
    elements.append(Paragraph(f"<b>Status:</b> {status}", styles["Normal"]))
    elements.append(Paragraph(f"<b>Fitment %:</b> {fitment_pct}%", styles["Normal"]))
    elements.append(Paragraph(f"<b>OA %:</b> {oa_pct}%", styles["Normal"]))
    elements.append(Spacer(1, 0.2 * inch))
    elements.append(Paragraph(f"<b>Total Arrear With HRA:</b> {total_with_hra}", normal_dejavu))
    elements.append(Paragraph(f"<b>Total Arrear Without HRA:</b> {total_without_hra}", normal_dejavu))
    elements.append(Spacer(1, 0.2 * inch))

    # Year-wise Table
    summary_df["Delta With HRA"] = summary_df["Delta With HRA"].apply(format_currency)
    summary_df["Delta Without HRA"] = summary_df["Delta Without HRA"].apply(format_currency)
    elements.append(Spacer(1, 0.3 * inch))
    elements.append(Paragraph("<b>Year-wise Arrear Impact:</b>", styles["Heading2"]))
    summary_table_data = [summary_df.columns.tolist()] + summary_df.values.tolist()
    summary_table = Table(summary_table_data, repeatRows=1)
    summary_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.beige),
        ('FONTNAME', (0, 0), (-1, -1), 'DejaVu'),
        ('FONTSIZE', (0, 0), (-1, -1), 8),
        ('GRID', (0, 0), (-1, -1), 0.25, colors.lightblue),
    ]))
    elements.append(summary_table)

    # Line Chart
    chart_df = summary_df.copy()
    chart_df["Delta With HRA"] = chart_df["Delta With HRA"].replace('[₹,]', '', regex=True).astype(float)
    chart_df["Delta Without HRA"] = chart_df["Delta Without HRA"].replace('[₹,]', '', regex=True).astype(float)
    chart_df = chart_df.sort_values("Financial Year")
    fig, ax = plt.subplots(figsize=(8, 4))
    ax.plot(chart_df["Financial Year"], chart_df["Delta With HRA"], marker='o', label='With HRA')
    ax.plot(chart_df["Financial Year"], chart_df["Delta Without HRA"], marker='o', label='Without HRA')
    ax.set_title('Year-wise Arrear Impact')
    ax.set_xlabel('Year')
    ax.set_ylabel('Pending Arrear Impact (₹)')
    ax.legend()
    ax.grid(True, linestyle='--', alpha=0.5)
    ax.yaxis.set_major_formatter(mtick.FuncFormatter(lambda x, _: f'₹{int(x):,}'))

    img_buffer = io.BytesIO()
    plt.tight_layout()
    plt.savefig(img_buffer, format='png')
    plt.close()
    img_buffer.seek(0)
    elements.append(Spacer(1, 0.2 * inch))
    elements.append(Paragraph("<b>Year-wise Impact Chart:</b>", styles["Heading2"]))
    elements.append(Image(img_buffer, width=6.5 * inch, height=3.5 * inch))

    # Dual Pie Chart
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 6))
    labels = chart_df["Financial Year"]
    sizes_with = chart_df["Delta With HRA"]
    sizes_without = chart_df["Delta Without HRA"]
    ax1.pie(sizes_with, labels=labels, autopct='%1.1f%%', startangle=140)
    ax1.set_title("Delta With HRA")
    ax2.pie(sizes_without, labels=labels, autopct='%1.1f%%', startangle=140)
    ax2.set_title("Delta Without HRA")

    img_buffer = io.BytesIO()
    plt.tight_layout()
    plt.savefig(img_buffer, format="png")
    plt.close()
    img_buffer.seek(0)
    elements.append(Spacer(1, 0.3 * inch))
    elements.append(Paragraph("<b>Year-wise Delta Impact Comparison:</b>", styles["Heading2"]))
    elements.append(Image(img_buffer, width=10 * inch, height=5 * inch))

    # Monthly Revised Data Table
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
