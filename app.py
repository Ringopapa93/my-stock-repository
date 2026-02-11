import streamlit as st
import pandas as pd
import requests
from bs4 import BeautifulSoup
import time

# --- 基本設定 ---
st.set_page_config(page_title="Kabutan Analyzer Pro", layout="wide")
st.title("🚀 多角的財務分析・自動投資判断ツール")

# --- 1. データ取得（スクレイピング）エンジン ---
def get_kabutan_data(code):
    """株探から財務・業績データを取得する関数"""
    try:
        # 基本URL（財務ページ）
        url_finance = f"https://kabutan.jp/stock/finance?code={code}"
        # 基本URL（決算ページ）
        url_kessan = f"https://kabutan.jp/stock/kessan?code={code}"
        
        headers = {"User-Agent": "Mozilla/5.0"}
        
        # 財務詳細ページへアクセス
        res = requests.get(url_finance, headers=headers)
        soup = BeautifulSoup(res.text, 'html.parser')
        
        # 銘柄名取得
        name = soup.find('div', class_='symbol').find('h1').text.replace(code, "").strip()
        
        # --- ここで各数値を抽出（プロトタイプでは主要項目を代表して抽出） ---
        # 本来は tableタグをループして各項目名と一致する値を取得します
        # 以下は計算用のサンプルロジック（実際にはスクレイピングした値を代入）
        
        # 例：PBRやROEを画面から抜き出す
        pbr = float(soup.find('div', id='stockinfo_i3').find_all('dd')[1].text.replace("倍", ""))
        
        # ※実際の運用ではここでB/S, P/Lの全項目をループ取得します
        # 取得できない場合のダミー処理を含めたデータ構造
        data = {
            "コード": code,
            "略称": name,
            "PBR": pbr,
            "ROE": 12.5,  # ここにスクレイピング値を連結
            "自己資本比率": 60.2,
            "流動比率": 150.0,
            "売上成長率": 7.5,
            "清算価値": 1000, # 修正資産-総負債の計算結果
            "配当性向": 30.5,
            "時価総額": "取得中..."
        }
        return data
    except Exception as e:
        return {"コード": code, "Error": str(e)}

# --- 2. 投資判断（A~E）ロジック ---
def judge_stock(d):
    if "Error" in d: return "取得不可"
    score = 0
    # 割安性：PBR1倍割れかつROE8%以上なら加点
    if d['PBR'] < 1.0: score += 2
    if d['ROE'] > 10.0: score += 2
    if d['自己資本比率'] > 50: score += 1
    
    mapping = {5: "A", 4: "B", 3: "C", 2: "D", 1: "E"}
    return mapping.get(score, "E")

# --- 3. UI（画面構成） ---
st.sidebar.header("分析設定")
codes_input = st.sidebar.text_area("証券コード（リスト）", value="9432, 1332, 2914, 6752, 6058, 3046, 4151")
target_codes = [c.strip() for c in codes_input.replace('\n', ',').split(',') if c.strip()]

if st.button("最新データを取得して分析"):
    results = []
    bar = st.progress(0)
    
    for i, code in enumerate(target_codes):
        with st.spinner(f"解析中: {code}..."):
            res = get_kabutan_data(code)
            res['投資判断'] = judge_stock(res)
            results.append(res)
            time.sleep(1.5) # 株探への負荷軽減（重要！）
            bar.progress((i + 1) / len(target_codes))
            
    df = pd.DataFrame(results)
    
    # 4. 結果表示
    st.subheader("📊 銘柄分析一覧")
    st.dataframe(df)
    
    # Excel/CSV 出力
    st.download_button("Excel用CSVをダウンロード", df.to_csv(index=False).encode('utf-8-sig'), "analysis_result.csv")
