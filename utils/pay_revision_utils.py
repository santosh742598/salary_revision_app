import pandas as pd
import streamlit as st

from typing import Tuple

# Simulated utility functions and constants (normally imported)
def get_da_percentage(month: int, year: int) -> float:
    index = (year - 2017) * 12 + (month - 1)
    da_rates = [
        0, 0, 0, -1.1, -1.1, -1.1, -0.2, -0.2, -0.2, 2.2, 2.2, 2.2,
        3.4, 3.4, 3.4, 3.5, 3.5, 3.5, 3.8, 3.8, 3.8, 7.3, 7.3, 7.3,
        8.8, 8.8, 8.8, 10, 10, 10, 12.4, 12.4, 12.4, 14.8, 14.8, 14.8,
        17.2, 17.2, 17.2, 18.7, 18.7, 18.7, 18.4, 18.4, 18.4, 20.9, 20.9, 20.9,
        23.7, 23.7, 23.7, 23.2, 23.2, 23.2, 24.7, 24.7, 24.7, 27.2, 27.2, 27.2,
        29.4, 29.4, 29.4, 30, 30, 30, 32.5, 32.5, 32.5, 34.8, 34.8, 34.8,
        37.2, 37.2, 37.2, 37.7, 37.7, 37.7, 39.2, 39.2, 39.2, 43.8, 43.8, 43.8,
        43.7, 43.7, 43.7, 44.3, 44.3, 44.3, 44.8, 44.8, 44.8, 47.7, 47.7, 47.7,
        49.6, 49.6, 49.6, 48.7, 48.7, 48.7
    ]
    return da_rates[index] if 0 <= index < len(da_rates) else 0

prc_minimums = {
    "E1": 40000, "E2": 50000, "E3": 60000, "E4": 70000, "E5": 80000,
    "E6": 90000, "E7": 100000, "E8": 110000, "E9": 120000
}

month_order = {
    "Jan": 1, "Feb": 2, "Mar": 3, "Apr": 4, "May": 5, "Jun": 6,
    "Jul": 7, "Aug": 8, "Sep": 9, "Oct": 10, "Nov": 11, "Dec": 12
}

def calculate_individual_revision(
    df: pd.DataFrame,
    fitment_rate: float,
    oa_rate: float,
    start_month: str | None = None,
    start_year: int | None = None,
) -> Tuple[pd.DataFrame, pd.DataFrame]:
    """Calculate revised salary from a specific revision start date.

    If ``start_month`` and ``start_year`` are provided, the computation
    begins from that month onwards. Earlier months are ignored, effectively
    giving a zero delta for the prior period.

    The first month's basic pay is adjusted by adding 119% and then applying
    the fitment percentage. In formula terms::

        revised_basic = old_basic * 2.19 * (1 + fitment_rate / 100)

    The result is then compared against the PRC grade minimum and the higher
    value is taken as the starting basic for subsequent calculations.
    """

    df = df.copy()
    df["Month"] = df["Month"].astype(str).str.strip().str.title()
    df["Year"] = df["Year"].astype(int)
    df["Month_num"] = df["Month"].map(month_order)

    df = df.sort_values(["Year", "Month_num"]).reset_index(drop=True)

    if start_month is not None and start_year is not None:
        sm = start_month.strip().title()
        sm_num = month_order.get(sm, 1)
        df = df[(df["Year"] > start_year) | ((df["Year"] == start_year) & (df["Month_num"] >= sm_num))]

    revised_data: list[dict] = []
    year_wise_impact: dict[str, list[float]] = {}

    previous_group = None
    current_basic = None

    for idx, row in df.iterrows():
        month = row["Month"].strip().title()
        year = int(row["Year"])
        month_num = month_order.get(month, 0)

        basic = float(str(row["Basic"]).replace(",", ""))
        group = str(row["Pay Scale Group"]).strip()
        grade_prefix = group[:2]

        if current_basic is None:
            base_basic = basic * 2.19 * (1 + fitment_rate / 100)
            current_basic = max(base_basic, prc_minimums.get(grade_prefix, base_basic))
        else:
            if group != previous_group:
                if grade_prefix in prc_minimums:
                    min_basic = prc_minimums[grade_prefix]
                    if current_basic < min_basic:
                        current_basic = min_basic
                    else:
                        current_basic *= 1.03
                else:
                    current_basic *= 1.03
            elif month == "Apr":
                current_basic *= 1.03

        previous_group = group

        da_pct = get_da_percentage(month_num, year)
        new_vda = current_basic * da_pct / 100

        hra_pct = float(row["HRA percentage"])
        if da_pct >= 25:
            hra_pct = {30: 27, 20: 18, 10: 9}.get(hra_pct, hra_pct)
        else:
            hra_pct = {30: 24, 20: 16, 10: 8}.get(hra_pct, hra_pct)

        hra = current_basic * hra_pct / 100
        oa = current_basic * oa_rate / 100

        revised_total = current_basic + new_vda + hra + oa
        original_total = basic + float(row["VDA"]) + float(row["HRA"]) + float(row["Other Allowance"])
        delta_with_hra = revised_total - original_total
        delta_without_hra = (current_basic + new_vda + oa) - (basic + float(row["VDA"]) + float(row["Other Allowance"]))

        revised_row = row.copy()
        revised_row["Revised Basic"] = round(current_basic, 2)
        revised_row["Revised VDA"] = round(new_vda, 2)
        revised_row["Revised HRA"] = round(hra, 2)
        revised_row["Revised OA"] = round(oa, 2)
        revised_row["Total Revised"] = round(revised_total, 2)
        revised_row["Delta With HRA"] = round(delta_with_hra, 2)
        revised_row["Delta Without HRA"] = round(delta_without_hra, 2)
        revised_data.append(revised_row)

        fy = f"{year}-{year + 1}" if month_num >= 4 else f"{year - 1}-{year}"
        if fy not in year_wise_impact:
            year_wise_impact[fy] = [0.0, 0.0]
        year_wise_impact[fy][0] += delta_with_hra
        year_wise_impact[fy][1] += delta_without_hra

    revised_df = pd.DataFrame(revised_data)
    if "Month_num" in revised_df.columns:
        revised_df = revised_df.drop(columns=["Month_num"])
    summary_df = pd.DataFrame([
        {"Financial Year": k, "Delta With HRA": round(v[0], 2), "Delta Without HRA": round(v[1], 2)}
        for k, v in sorted(year_wise_impact.items())
    ])

    st.dataframe(revised_df, use_container_width=True)
    return revised_df, summary_df
