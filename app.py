import streamlit as st
import json
from datetime import datetime
import os

st.set_page_config(page_title="ライフハック・スレッドメモ", layout="wide")

CONFIG_FILE = "config.json"
DATA_FILE = "lifehacks.json"

# ====================== 設定・認証 ======================
def load_config():
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {"password": None}

def save_config(config):
    with open(CONFIG_FILE, "w", encoding="utf-8") as f:
        json.dump(config, f, ensure_ascii=False, indent=2)

config = load_config()

if config["password"] is None:
    st.title("🧠 初回パスワード設定")
    st.markdown("**初めての利用です。パスワードを設定してください。**")
    pw1 = st.text_input("パスワード", type="password", key="setup1")
    pw2 = st.text_input("確認", type="password", key="setup2")
    if st.button("設定する", type="primary", key="setup_btn"):
        if pw1 and pw1 == pw2:
            config["password"] = pw1
            save_config(config)
            st.success("設定完了！")
            st.rerun()
    st.stop()

PASSWORD = config["password"]
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False

if not st.session_state.authenticated:
    st.title("🔒 ログイン")
    pw = st.text_input("パスワード", type="password", key="login_pw")
    if st.button("ログイン", key="login_btn"):
        if pw == PASSWORD:
            st.session_state.authenticated = True
            st.rerun()
        else:
            st.error("パスワードが違います")
    st.stop()

# ====================== データ ======================
def load_data():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return []

def save_data(data):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

data = load_data()

# ====================== サイドバー ======================
with st.sidebar:
    st.header("⚙️ 設定")
    sort_option = st.selectbox("並び順", ["最新順", "古い順"], key="sort_key")
    
    if st.button("💾 今すぐバックアップ", type="primary"):
        current_data = load_data()
        st.download_button(
            label="📥 バックアップダウンロード",
            data=json.dumps(current_data, ensure_ascii=False, indent=2),
            file_name=f"lifehacks_backup_{datetime.now().strftime('%Y%m%d_%H%M')}.json",
            mime="application/json"
        )

    st.markdown("---")
    st.header("📝 新規投稿")
    title = st.text_input("タイトル", key="title_input")
    content = st.text_area("内容（改行OK）", height=150, key="content_input")
    tags = st.text_input("タグ（カンマ区切り）", key="tags_input")
    importance = st.slider("重要度 ⭐", 1, 5, 3, key="imp_input")
    
    if st.button("投稿する", type="primary", key="post_btn"):
        if title and content:
            new_hack = {
                "id": len(data) + 1,
                "title": title,
                "content": content,
                "tags": [t.strip() for t in tags.split(",") if t.strip()],
                "importance": importance,
                "date": datetime.now().strftime("%Y-%m-%d %H:%M"),
                "replies": []
            }
            data.append(new_hack)
            save_data(data)
            st.success("✅ 投稿しました！")
            st.rerun()

# ====================== メイン表示 ======================
st.title("🧠 ライフハック・スレッドメモ帳")

st.subheader("📋 すべてのライフハック")

sorted_data = sorted(data, key=lambda x: x["date"], reverse=True)

for i, hack in enumerate(sorted_data):
    stars = "⭐" * hack.get("importance", 3)
    with st.expander(f"{stars} {hack['title']} — {hack['date']}", expanded=False):
        st.markdown(hack['content'].replace('\n', '<br>'), unsafe_allow_html=True)

        col1, col2 = st.columns(2)
        with col1:
            if st.button("✏️ 編集", key=f"edit_main_{hack['id']}"):
                st.session_state[f"editing_main_{hack['id']}"] = True
        with col2:
            if st.button("🗑 削除", key
