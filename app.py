import streamlit as st
import json
from datetime import datetime
import os

st.set_page_config(page_title="ライフハック・スレッドメモ", layout="wide")

CONFIG_FILE = "config.json"
DATA_FILE = "lifehacks.json"

# 設定・認証
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

# データ関数
def load_data():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return []

def save_data(data):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

data = load_data()

# ====================== 新規投稿 ======================
with st.sidebar:
    st.header("📝 新規投稿")
    title = st.text_input("タイトル", key="title_input")
    content = st.text_area("内容（改行OK）", height=150, key="content_input")
    tags = st.text_input("タグ", key="tags_input")
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

for i, hack in enumerate(data):
    stars = "⭐" * hack.get("importance", 3)
    with st.expander(f"{stars} {hack['title']} — {hack['date']}", expanded=False):
        st.markdown(hack['content'].replace('\n', '<br>'), unsafe_allow_html=True)

        col1, col2 = st.columns(2)
        with col1:
            if st.button("✏️ 編集", key=f"edit_{i}"):
                st.session_state[f"edit_mode_{i}"] = True
        with col2:
            if st.button("🗑 削除", key=f"del_{i}"):
                st.session_state[f"del_confirm_{i}"] = True

        if st.session_state.get(f"del_confirm_{i}", False):
            st.warning("本当に削除しますか？")
            c1, c2 = st.columns(2)
            with c1:
                if st.button("はい", key=f"yes_del_{i}"):
                    data.pop(i)
                    save_data(data)
                    st.success("削除しました")
                    st.rerun()
            with c2:
                if st.button("いいえ", key=f"no_del_{i}"):
                    st.session_state[f"del_confirm_{i}"] = False
                    st.rerun()

        # 返信機能（簡略）
        st.markdown("**スレッド返信**")
        for j, reply in enumerate(hack.get("replies", [])):
            st.markdown(reply['content'].replace('\n', '<br>'), unsafe_allow_html=True)

        reply_text = st.text_area("返信を追加", key=f"new_reply_{i}", height=80)
        if st.button("返信する", key=f"add_reply_{i}"):
            if reply_text.strip():
                hack.setdefault("replies", []).append({
                    "content": reply_text,
                    "date": datetime.now().strftime("%Y-%m-%d %H:%M")
                })
                save_data(data)
                st.success("返信追加！")
                st.rerun()
