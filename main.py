# Directory structure:
# salary_revision_app/
#   - main.py
#   - pages/
#       - 1_Individual_Impact.py
#   - utils/
#       - session_utils.py
#       - pay_revision_utils.py
#       - pdf_utils.py

# ================= main.py =================
import streamlit as st
import pandas as pd
from utils.session_utils import set_original_data

st.set_page_config(page_title="📊 Salary Revision & Impact Analysis")
st.title("📤 Upload & Revision Setup")

st.markdown("Upload the base salary data Excel file. You only need to upload once.")

uploaded_file = st.file_uploader("Upload Salary Excel File", type=[".xlsx", ".xls"])

if uploaded_file:
    df = pd.read_excel(uploaded_file)
    st.session_state["original_data"] = df
    set_original_data(df)
    st.success("File uploaded and loaded successfully.")
    st.dataframe(df.head())

st.markdown("---")
st.info("Navigate to the 'Individual Impact' page to compute salary revision for specific SAP numbers.")


