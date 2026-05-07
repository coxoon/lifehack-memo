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

with st.sidebar:
    st.header("新しいライフハック")
    title = st.text_input("タイトル（例: 朝のルーティン最適化）")
    content = st.text_area("内容・ハック詳細", height=150)
    tags = st.text_input("タグ（カンマ区切り）", placeholder="生産性,朝活,健康")
    
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
        else:
            st.error("タイトルと内容を入力してください")

st.subheader("📋 すべてのライフハック（スレッド展開）")

for hack in data:
    with st.expander(f"🔸 {hack['title']}  —  {hack['date']}  {' | '.join(hack.get('tags', []))}", expanded=False):
        st.write(hack['content'])
        
        if hack.get('replies'):
            st.markdown("**スレッド返信**")
            for reply in hack['replies']:
                st.info(f"↳ {reply['content']}  —  {reply['date']}")
        
        reply_content = st.text_area("このハックに返信・改善アイデアを追加", key=f"reply_{hack['id']}", height=80)
        if st.button("返信する", key=f"btn_{hack['id']}"):
            if reply_content.strip():
                hack['replies'].append({
                    "content": reply_content,
                    "date": datetime.now().strftime("%Y-%m-%d %H:%M")
                })
                save_data(data)
                st.success("返信追加！")
                st.rerun()

search = st.text_input("🔍 検索")
if search:
    filtered = [h for h in data if search.lower() in str(h).lower()]
    st.write(f"検索結果: {len(filtered)}件")
