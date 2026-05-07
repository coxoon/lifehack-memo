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
                    hack['title'] = new_title
                    hack['content'] = new_content
                    hack['tags'] = [t.strip() for t in new_tags.split(",") if t.strip()]
                    hack['date'] = datetime.now().strftime("%Y-%m-%d %H:%M") + "（編集済）"
                    save_data(data)
                    st.success("更新しました！")
                    st.session_state[f"editing_main_{i}"] = False
                    st.rerun()
            with col_b:
                if st.button("❌ キャンセル", key=f"cancel_main_{i}"):
                    st.session_state[f"editing_main_{i}"] = False
                    st.rerun()

        # メイン削除
        if st.button("🗑 このハックを削除", key=f"del_main_{i}", type="secondary"):
            if st.checkbox("本当に削除しますか？", key=f"confirm_main_{i}"):
                del data[i]
                save_data(data)
                st.success("削除しました")
                st.rerun()

        # ====================== 返信部分 ======================
        st.markdown("**スレッド返信**")
        for j, reply in enumerate(hack.get('replies', [])):
            col1, col2, col3 = st.columns([7, 1.5, 1.5])
            with col1:
                st.info(f"↳ {reply['content']}  —  {reply['date']}")
            
            with col2:
                if st.button("✏️", key=f"edit_reply_{i}_{j}"):
                    st.session_state[f"editing_reply_{i}_{j}"] = True
            
            with col3:
                if st.button("🗑", key=f"del_reply_{i}_{j}"):
                    if st.checkbox("削除？", key=f"confirm_reply_{i}_{j}"):
                        hack['replies'].pop(j)
                        save_data(data)
                        st.success("返信を削除しました")
                        st.rerun()

            # 返信編集モード
            if st.session_state.get(f"editing_reply_{i}_{j}", False):
                new_reply = st.text_area("返信を編集", value=reply['content'], height=100, key=f"edit_text_{i}_{j}")
                col_edit1, col_edit2 = st.columns(2)
                with col_edit1:
                    if st.button("保存", key=f"save_reply_{i}_{j}"):
                        hack['replies'][j]['content'] = new_reply
                        hack['replies'][j]['date'] = datetime.now().strftime("%Y-%m-%d %H:%M") + "（編集済）"
                        save_data(data)
                        st.success("返信を更新しました")
                        st.session_state[f"editing_reply_{i}_{j}"] = False
                        st.rerun()
                with col_edit2:
                    if st.button("キャンセル", key=f"cancel_reply_{i}_{j}"):
                        st.session_state[f"editing_reply_{i}_{j}"] = False
                        st.rerun()

        # 新規返信
        reply_content = st.text_area("返信・改善アイデアを追加", key=f"new_reply_{i}", height=80)
        if st.button("返信する", key=f"btn_reply_{i}"):
            if reply_content.strip():
                hack.setdefault('replies', []).append({
                    "content": reply_content,
                    "date": datetime.now().strftime("%Y-%m-%d %H:%M")
                })
                save_data(data)
                st.success("返信を追加しました！")
                st.rerun()

# 検索
search = st.text_input("🔍 検索（タイトル・内容）")
if search:
    filtered = [h for h in data if search.lower() in str(h).lower()]
    st.write(f"検索結果: {len(filtered)} 件")

# 全データダウンロード
if st.button("💾 全データをバックアップ"):
    st.download_button("ダウンロード", json.dumps(data, ensure_ascii=False, indent=2), "lifehacks_backup.json")
