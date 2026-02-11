import streamlit as st
import pandas as pd
import time

# --- 設定とタイトル ---
st.set_page_config(page_title="Stock Analysis Pro", layout="wide")
st.title("📊 多角的財務分析・投資判断ツール (Prototype)")

# --- サイドバー：銘柄管理 ---
st.sidebar.header("設定")
codes_input = st.sidebar.text_area("証券コードを入力（改行またはカンマ区切り）", 
                                   value="9432, 1332, 2914, 6752, 6058, 3046, 4151")
target_codes = [c.strip() for c in codes_input.replace('\n', ',').split(',') if c.strip()]

# --- ダミーデータ取得関数の定義（プロトタイプ用） ---
# 本番ではここを BeautifulSoup 等で株探からスクレイピングするロジックに差し替えます
def fetch_stock_data(code):
    # 本来は requests.get(f"https://kabutan.jp/stock/finance?code={code}") 等を実行
    # プロトタイプでは計算の流れを示すため、サンプル値を返します
    data = {
        "コード": code,
        "略称": f"銘柄_{code}",
        "株価": 1500,
        "ROE": 12.5,
        "自己資本比率": 55.0,
        "PBR": 0.85,
        "売上成長率": 8.2,
        "清算価値": 1200, # 資産バリューチェック用
        "配当性向": 35.0
    }
    return data

# --- 投資判断ロジック（A~E） ---
def evaluate_stock(d):
    score = 0
    # 1. 資産割安性
    if d['PBR'] < 1.0: score += 1
    # 2. 収益性
    if d['ROE'] > 10.0: score += 1
    # 3. 健全性
    if d['自己資本比率'] > 50.0: score += 1
    # 4. 成長性
    if d['売上成長率'] > 5.0: score += 1
    # 5. 株主還元
    if d['配当性向'] > 30.0: score += 1
    
    mapping = {5: "A", 4: "B", 3: "C", 2: "D", 1: "E", 0: "E"}
    return mapping.get(score, "E")

# --- メイン処理 ---
if st.button("データ取得・分析開始"):
    progress_bar = st.progress(0)
    all_data = []
    
    for i, code in enumerate(target_codes):
        # 1銘柄ずつ処理（スクレイピングの負荷軽減を想定）
        with st.spinner(f"コード {code} を解析中..."):
            stock_info = fetch_stock_data(code)
            stock_info['投資判断'] = evaluate_stock(stock_info)
            all_data.append(stock_info)
            time.sleep(0.5) # サーバーへの負荷対策
            progress_bar.progress((i + 1) / len(target_codes))
            
    # 結果の表示
    df = pd.DataFrame(all_data)
    
    # 評価によって色を変える表示設定
    def color_eval(val):
        color = 'red' if val == 'A' else 'orange' if val == 'B' else 'black'
        return f'color: {color}; font-weight: bold'

    st.subheader("分析結果一覧")
    st.dataframe(df.style.applymap(color_eval, subset=['投資判断']))

    # CSVダウンロード機能
    csv = df.to_csv(index=False).encode('utf-8-sig')
    st.download_button("結果をCSVで保存", data=csv, file_name="stock_analysis.csv", mime="text/csv")

else:
    st.info("左側のサイドバーで銘柄を確認し、「分析開始」ボタンを押してください。")
