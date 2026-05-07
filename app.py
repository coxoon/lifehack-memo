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
        
        st.write(hack['content'])
        
        # メイン編集・削除
        col1, col2 = st.columns(2)
        with col1:
            if st.button("✏️ 編集", key=f"edit_main_{i}"):
                st.session_state[f"editing_main_{i}"] = True
        with col2:
            if st.button("🗑 削除", key=f"del_main_{i}"):
                st.session_state[f"confirm_del_main_{i}"] = True

        # メイン編集モード
        if st.session_state.get(f"editing_main_{i}", False):
            # ...（編集部分は省略せず残す）
            new_title = st.text_input("新しいタイトル", hack['title'], key=f"nt_{i}")
            new_content = st.text_area("新しい内容", hack['content'], height=150, key=f"nc_{i}")
            new_tags = st.text_input("新しいタグ", ",".join(hack.get('tags', [])), key=f"ntg_{i}")
            
            c1, c2 = st.columns(2)
            with c1:
                if st.button("✅ 保存", key=f"save_m_{i}"):
                    hack['title'] = new_title
                    hack['content'] = new_content
                    hack['tags'] = [t.strip() for t in new_tags.split(",") if t.strip()]
                    hack['date'] = datetime.now().strftime("%Y-%m-%d %H:%M") + "（編集済）"
                    save_data(data)
                    st.session_state[f"editing_main_{i}"] = False
                    st.rerun()
            with c2:
                if st.button("❌ キャンセル", key=f"can_m_{i}"):
                    st.session_state[f"editing_main_{i}"] = False
                    st.rerun()

        # メイン削除確認
        if st.session_state.get(f"confirm_del_main_{i}", False):
            st.warning("本当にこのライフハック全体を削除しますか？")
            c1, c2 = st.columns(2)
            with c1:
                if st.button("はい、削除します", key=f"yes_main_{i}"):
                    del data[i]
                    save_data(data)
                    st.success("削除しました")
                    st.rerun()
            with c2:
                if st.button("キャンセル", key=f"no_main_{i}"):
                    st.session_state[f"confirm_del_main_{i}"] = False
                    st.rerun()

        # ====================== 返信部分（修正済み） ======================
        st.markdown("**スレッド返信**")
        for j, reply in enumerate(hack.get('replies', [])):
            col1, col2, col3 = st.columns([6, 2, 2])
            with col1:
                st.info(f"↳ {reply['content']} — {reply['date']}")
            
            with col2:
                if st.button("✏️ 編集", key=f"e_reply_{i}_{j}"):
                    st.session_state[f"edit_reply_{i}_{j}"] = True
            
            with col3:
                if st.button("🗑 削除", key=f"d_reply_{i}_{j}"):
                    st.session_state[f"confirm_del_reply_{i}_{j}"] = True

            # 返信編集
            if st.session_state.get(f"edit_reply_{i}_{j}", False):
                new_text = st.text_area("返信編集", reply['content'], key=f"edit_text_{i}_{j}")
                c1, c2 = st.columns(2)
                with c1:
                    if st.button("保存", key=f"save_r_{i}_{j}"):
                        hack['replies'][j]['content'] = new_text
                        hack['replies'][j]['date'] = datetime.now().strftime("%Y-%m-%d %H:%M") + "（編集済）"
                        save_data(data)
                        st.session_state[f"edit_reply_{i}_{j}"] = False
                        st.rerun()
                with c2:
                    if st.button("キャンセル", key=f"can_r_{i}_{j}"):
                        st.session_state[f"edit_reply_{i}_{j}"] = False
                        st.rerun()

            # 返信削除確認（修正ポイント）
            if st.session_state.get(f"confirm_del_reply_{i}_{j}", False):
                st.warning("この返信を削除しますか？")
                c1, c2 = st.columns(2)
                with c1:
                    if st.button("はい、削除", key=f"yes_r_{i}_{j}"):
                        hack['replies'].pop(j)
                        save_data(data)
                        st.success("返信を削除しました")
                        st.rerun()
                with c2:
                    if st.button("キャンセル", key=f"no_r_{i}_{j}"):
                        st.session_state[f"confirm_del_reply_{i}_{j}"] = False
                        st.rerun()

        # 新規返信
        reply_content = st.text_area("返信・改善アイデアを追加", key=f"new_r_{i}", height=80)
        if st.button("返信する", key=f"btn_{i}"):
            if reply_content.strip():
                hack.setdefault('replies', []).append({
                    "content": reply_content,
                    "date": datetime.now().strftime("%Y-%m-%d %H:%M")
                })
                save_data(data)
                st.success("返信追加！")
                st.rerun()
