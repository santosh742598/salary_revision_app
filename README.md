# 🧾 PSU Salary Revision & Impact Analysis App

This Streamlit-based web app allows Public Sector Undertakings (PSUs) to calculate and visualize salary revisions based on the 3rd PRC (Pay Revision Committee) recommendations. It enables individual employees to analyze their revised salaries and download a detailed PDF report.

---

## 🔧 Features

- 📤 Upload original salary data (Excel format)
- 📅 Select revision start date, fitment % and other allowance %
- 📈 Generate revised salary for individual employees based on SAP number
- 🪙 Apply PRC logic for increments, promotions, and grade-based pay scales
- 🧾 Download a well-formatted PDF report showing:
  - Revised monthly salary components
  - Year-wise delta impact (with and without HRA)
  - Summary section with disclaimers
- 🌐 Designed for internal use by finance and HR departments of PSUs

---

## 📁 Folder Structure
salary_revision_app/
│
├── main.py # Entry point
├── pages/
│ └── 1_Individual_Impact.py # Individual salary calculator
├── utils/
│ ├── da_utils.py # DA percentage table
│ ├── constants.py # Minimum PRC grade-wise basic pay
│ ├── pdf_utils.py # ReportLab-based PDF generator
│ ├── session_utils.py # Streamlit session data handlers
│ └── pay_revision_utils.py # Salary calculation logic
├── generated_pdfs/ # Auto-created folder for PDF reports
├── requirements.txt
└── README.md


---

## 🛠 Setup Instructions

### ✅ 1. Install Dependencies

Create a virtual environment (optional but recommended):


python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
Install packages:

bash
pip install -r requirements.txt
✅ 2. Run the App
bash
streamlit run main.py
📄 Data Format (Excel)
# Ensure your uploaded file has the following columns:

Employee No
Name
Status
Month
Year
Basic
VDA
HRA
HRA percentage
Other Allowance
Other Allowance percentage
Pay Scale Group

📤 PDF Report
Each employee can download a personalized "Draft 3rd PRC Revision" report in PDF format containing:

Revised salary breakup
Delta impact (monthly and yearly)
Fitment & allowance used

Disclaimer: Notional computation for information only

📌 Disclaimer
This application is intended for internal financial simulation only. The calculations are based on assumed logic and may not reflect official government notifications or exact PRC orders.

🧑‍💻 Author
Developed by Santosh, 2025
Customizable for PSU HR & Finance departments
