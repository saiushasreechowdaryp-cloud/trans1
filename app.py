"""Transworld inbound processing & SKU onboarding — POC dashboard (synthetic data).
Run:  streamlit run app.py
"""
import io

import streamlit as st

st.set_page_config(page_title="Inbound & SKU Intelligence POC (synthetic)", page_icon="📦", layout="wide")

from src import ui  # noqa: E402
from src.loader import DEFAULT_WORKBOOK, WorkbookError, load_workbook  # noqa: E402
from src.logic import build_model  # noqa: E402
from views import p1_3, p4_6, p7_9  # noqa: E402

PAGES = {
    "1. Executive overview": p1_3.overview,
    "2. Inbound processing": p1_3.inbound,
    "3. Document intelligence": p1_3.documents,
    "4. SKU intelligence": p4_6.sku,
    "5. New SKU onboarding": p4_6.new_sku,
    "6. Exceptions & human review": p4_6.exceptions,
    "7. POC validation": p7_9.validation,
    "8. End-to-end demo": p7_9.demo,
    "9. Future implementation": p7_9.future,
}


@st.cache_data(show_spinner="Reading workbook…")
def get_model(data: bytes | None, path: str):
    wb = load_workbook(io.BytesIO(data) if data else path)
    return build_model(wb)


def main():
    ui.setup_page()
    with st.sidebar:
        st.markdown("### Inbound & SKU Intelligence")
        st.caption("SP Jain MGB capstone — WMS Team A. Proof of concept for an illustrative Transworld scenario.")
        page = st.radio("Page", list(PAGES), label_visibility="collapsed")
        st.divider()
        up = st.file_uploader("Use a different workbook (same structure)", type=["xlsx"])
        st.markdown(ui.pill("SYNTHETIC DATA", ui.AMBER), unsafe_allow_html=True)
    ui.banner()
    try:
        model = get_model(up.getvalue() if up else None, str(DEFAULT_WORKBOOK))
    except WorkbookError as e:
        st.error(f"The dashboard could not load the data. {e}")
        st.stop()
    for w in model.warnings:
        st.warning(w)
    try:
        PAGES[page](model)
    except Exception as e:  # keep the demo alive; show what failed
        st.error(f"This page hit an unexpected problem: {type(e).__name__}: {e}")
        st.exception(e)


main()
