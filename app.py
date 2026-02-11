import streamlit as st import pandas as pd import requests from bs4 import BeautifulSoup import time

st.set_page_config(page_title="Kabutan Analyzer Pro", layout="wide") st.title("🚀 多角的財務分析ツール（修正版）")

def fetch_stock_data(code): headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"} try: url_main = f"{code}" res_main = requests.get(url_main, headers=headers) soup_main = BeautifulSoup(res_main.text, 'html.parser')

st.sidebar.header("分析設定") codes_input = st.sidebar.text_area("証券コード", value="9432, 1332, 2914, 6752, 6058, 3046, 4151") target_codes = [c.strip() for c in codes_input.replace('\n', ',').split(',') if c.strip()]

if st.button("最新データを取得して分析"): results = [] bar = st.progress(0) for i, code in enumerate(target_codes): with st.spinner(f"解析中: {code}"): results.append(fetch_stock_data(code)) time.sleep(1.5) bar.progress((i + 1) / len(target_codes))
