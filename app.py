 import streamlit as st
import json
from datetime import datetime
import os

st.set_page_config(page_title="ライフハック・スレッドメモ", layout="wide")
st.title("🧠 ライフハック・スレッドメモ帳")
st.caption("アイデアをスレッド展開して深掘り・整理しよう")

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

# ====================== 新規投稿 ======================
with st.sidebar:
    st.header("📝 新しいライフハック")
    title = st.text_input("タイトル")
    content = st.text_area("内容", height=150)
    tags = st.text_input("タグ（カンマ区切り）", placeholder="生産性,朝活")
    
    if st.button("投稿する", type="primary"):
        if title and content:
            new_hack = {
                "id": len(data) + 1,
                "title": title,
                "content": content,
                "tags": [t.strip() for t in tags.split(",") if t.strip()],
                "date": datetime.now().strftime("%Y-%m-%d %H:%M"),
                "replies": []
            }
            data.append(new_hack)
            save_data(data)
            st.success("投稿しました！")
            st.rerun()

# ====================== メイン表示 ======================
st.subheader("📋 すべてのライフハック")

for i, hack in enumerate(data):
    with st.expander(f"🔸 {hack['title']}  —  {hack['date']}  |  {' | '.join(hack.get('tags', []))}", expanded=False):
        
        # メイン内容表示・編集
        col1, col2 = st.columns([7, 3])
        with col1:
            st.write(hack['content'])
        with col2:
            if st.button("✏️ 編集", key=f"edit_main_{i}"):
                st.session_state[f"editing_main_{i}"] = True

        # 編集モード
        if st.session_state.get(f"editing_main_{i}", False):
            new_title = st.text_input("新しいタイトル", value=hack['title'], key=f"new_title_{i}")
            new_content = st.text_area("新しい内容", value=hack['content'], height=150, key=f"new_content_{i}")
            new_tags = st.text_input("新しいタグ", value=",".join(hack.get('tags', [])), key=f"new_tags_{i}")
            
            col_a, col_b = st.columns(2)
            with col_a:
                if st.button("✅ 保存", key=f"save_main_{i}"):
