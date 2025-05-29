import streamlit as st
import pandas as pd


def set_original_data(df: pd.DataFrame):
    st.session_state["original_data"] = df


def get_original_data():
    return st.session_state.get("original_data", pd.DataFrame())
