import streamlit as st
import pandas as pd
from utils.session_utils import get_original_data
from utils.pay_revision_utils import calculate_individual_revision, month_order
from utils.pdf_utils import generate_individual_pdf

st.title("👤 Individual Salary Revision Impact")

# Get uploaded original data
original_df = get_original_data()

if original_df is None or original_df.empty:
    st.warning("Please upload the salary data on the main page first.")
    st.stop()

# Get SAP number from user
sap_no = st.text_input("Enter SAP Number:")

if sap_no:
    # Clean column names just in case
    original_df.columns = original_df.columns.str.strip().str.replace('\u200b', '')

    try:
        emp_data = original_df[original_df["Employee No"] == int(sap_no)]
    except:
        emp_data = original_df[original_df["Employee No"].astype(str) == sap_no]

    if emp_data.empty:
        st.error("No data found for the given SAP number.")
        st.stop()

    # Default revision inputs
    fitment_pct = st.slider("Fitment %", 0, 30, 0)
    oa_pct = st.slider("Other Allowance %", 0, 35, 35)

    months = list(month_order.keys())
    year_options = sorted(emp_data["Year"].astype(int).unique())
    start_year = st.selectbox("Revision Start Year", year_options, index=0)
    start_month = st.selectbox("Revision Start Month", months, index=0)


    st.markdown("---")
    st.write("### Revised Salary Data")

    revised_df, summary_df = calculate_individual_revision(
        emp_data,
        fitment_pct,
        oa_pct,
        start_month,
        int(start_year),
    )

    st.dataframe(revised_df, use_container_width=True)

    st.write("### Year-wise Delta Impact")
    st.dataframe(summary_df, use_container_width=True)

    st.markdown("---")
    revision_date = f"{start_month} {start_year}"
    if st.button("📥 Download PDF Report"):
        pdf_path = generate_individual_pdf(
            revised_df,  # Month-wise revised data
            sap_no,  # SAP number
            fitment_pct,  # Selected fitment rate
            oa_pct,  # Selected OA rate
            summary_df,  # Year-wise delta summary
            revision_date,
        )

        with open(pdf_path, "rb") as f:
            st.download_button(
                label="Download Now",
                data=f,
                file_name=f"draft_3rd_prc_revision_{sap_no}.pdf",
                mime="application/pdf"
            )




else:
    st.info("Please enter a SAP number to proceed.")
