import streamlit as st
import json
from datetime import datetime
import os

st.set_page_config(page_title="ライフハック・スレッドメモ", layout="wide")

# ====================== パスワード管理 ======================
CONFIG_FILE = "config.json"

def load_config():
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {"password": "1234"}  # 初回初期パスワード

def save_config(config):
    with open(CONFIG_FILE, "w", encoding="utf-8") as f:
        json.dump(config, f, ensure_ascii=False, indent=2)

config = load_config()
PASSWORD = config["password"]

# 認証
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False

if not st.session_state.authenticated:
    st.title("🔒 ライフハック・スレッドメモ帳")
    pw = st.text_input("パスワードを入力してください", type="password")
    if st.button("ログイン"):
        if pw == PASSWORD:
            st.session_state.authenticated = True
            st.rerun()
        else:
            st.error("パスワードが違います")
    st.stop()

# ====================== メインアプリ ======================
st.title("🧠 ライフハック・スレッドメモ帳")

with st.sidebar:
    st.header("⚙️ 設定")
    
    # パスワード変更機能
    with st.expander("🔑 パスワード変更"):
        st.write("現在のパスワードを確認してから変更します")
        current_pw = st.text_input("現在のパスワード", type="password", key="current_pw")
        new_pw = st.text_input("新しいパスワード", type="password", key="new_pw")
        new_pw_confirm = st.text_input("新しいパスワード（確認）", type="password", key="new_pw_confirm")
        
        if st.button("パスワードを変更する"):
            if current_pw == PASSWORD and new_pw == new_pw_confirm and new_pw:
                config["password"] = new_pw
                save_config(config)
                st.success("✅ パスワードを変更しました！")
                st.info("※ 再度ログインしてください")
                st.session_state.authenticated = False
                st.rerun()
            else:
                st.error("現在のパスワードが間違っているか、新しいパスワードが一致しません")

    st.markdown("---")
    dark_mode = st.toggle("🌙 ダークモード", False)
    sort_option = st.selectbox("並び順", ["最新順", "古い順"])

# ====================== データ処理部分 ======================
DATA_FILE = "lifehacks.json"

def load_data():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return []

def save_data(data):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

data = load_data()

# 以降は以前の機能（タグフィルタ、重要度、Markdown、並び替えなど）を維持
# （コードが長くなるのでここでは省略しましたが、必要なら完全版を送ります）

st.success("アプリ内でパスワード変更が可能になりました！")

# 残りの機能（新規投稿、表示、編集など）は前のバージョンをベースにしています
# 必要なら「完全版コードをもう一度全部送って」と教えてください
