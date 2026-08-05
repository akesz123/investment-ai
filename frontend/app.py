import streamlit as st
import requests

API_BASE_URL = "http://backend:8000"

st.set_page_config(page_title="Investment AI", layout="wide")


def page_overview():
    st.title("Investment AI – Overview")
    health = requests.get(f"{API_BASE_URL}/health", timeout=10).json()
    st.success(f"Backend status: {health['status']} – {health['app']}")

    if st.button("Run market scan"):
        with st.spinner("Scanning market (ETFs and indices)..."):
            resp = requests.get(f"{API_BASE_URL}/scan", timeout=60)
            if resp.ok:
                data = resp.json()
                st.write(data)
            else:
                st.error(f"Scan failed: {resp.status_code} {resp.text}")


def page_top_stocks():
    st.title("Top Stocks (AI Score)")
    limit = st.slider("Number of stocks", 5, 50, 10)
    resp = requests.get(f"{API_BASE_URL}/top-stocks", params={"limit": limit}, timeout=30)
    if resp.ok:
        data = resp.json()
        st.dataframe(data)
    else:
        st.error("Failed to load top stocks")


def page_top_etfs():
    st.title("Top ETFs (AI Score)")
    limit = st.slider("Number of ETFs", 5, 50, 10)
    resp = requests.get(f"{API_BASE_URL}/top-etfs", params={"limit": limit}, timeout=30)
    if resp.ok:
        data = resp.json()
        st.dataframe(data)
    else:
        st.error("Failed to load top ETFs")


PAGES = {
    "Overview": page_overview,
    "Top Stocks": page_top_stocks,
    "Top ETFs": page_top_etfs,
}


page = st.sidebar.selectbox("Page", list(PAGES.keys()))
PAGES[page]()
