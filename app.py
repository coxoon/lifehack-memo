import streamlit as st
import json
from datetime import datetime
import os

# ページ設定
st.set_page_config(page_title="ライフハック・スレッドメモ", layout="wide")

# ダークモード設定
if "dark_mode" not in st.session_state:
    st.session_state.dark_mode = False

if st.session_state.dark_mode:
    st.markdown("""
    <style>
    .stApp { background-color: #0E1117; color: #FAFAFA; }
    </style>
    """, unsafe_allow_html=True)

st.title("🧠 ライフハック・スレッドメモ帳")
st.caption("アイデアを深掘り整理しよう")

# パスワード保護
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False

PASSWORD = "1234"  # ← ここを自分好みに変更してください！

if not st.session_state.authenticated:
    st.subheader("🔒 パスワードを入力してください")
    pw = st.text_input("パスワード", type="password")
    if st.button("ログイン"):
        if pw == PASSWORD:
            st.session_state.authenticated = True
            st.rerun()
        else:
            st.error("パスワードが違います")
    st.stop()

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

# ====================== サイドバー ======================
with st.sidebar:
    st.header("設定")
    st.session_state.dark_mode = st.toggle("🌙 ダークモード", st.session_state.dark_mode)
    
    st.markdown("---")
    sort_option = st.selectbox("並び順", ["最新順", "古い順"])
    
    st.markdown("---")
    st.header("フィルター")
    all_tags = set()
    for h in data:
        all_tags.update(h.get("tags", []))
    selected_tags = st.multiselect("タグで絞り込み", sorted(all_tags))
    
    st.markdown("---")
    st.header("新しいライフハック")
    title = st.text_input("タイトル")
    content = st.text_area("内容（Markdown対応）", height=150)
    tags = st.text_input("タグ（カンマ区切り）", placeholder="生産性,朝活")
    importance = st.slider("重要度 ⭐", 1, 5, 3)
    
    if st.button("投稿する", type="primary"):
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
            st.success("投稿しました！")
            st.rerun()

# ====================== メイン表示 ======================
st.subheader("📋 ライフハック一覧")

# 並び替え
if sort_option == "最新順":
    sorted_data = sorted(data, key=lambda x: x["date"], reverse=True)
else:
    sorted_data = sorted(data, key=lambda x: x["date"])

# フィルタリング
display_data = sorted_data
if selected_tags:
    display_data = [h for h in sorted_data if any(tag in h.get("tags", []) for tag in selected_tags)]

for i, hack in enumerate(display_data):
    # 重要度表示
    stars = "⭐" * hack.get("importance", 3)
    
    with st.expander(f"{stars} {hack['title']}  —  {hack['date']}"):
        # Markdown対応で表示
        st.markdown(hack['content'])
        
        # タグ表示
        if hack.get("tags"):
            st.caption("🏷️ " + " ".join([f"`{tag}`" for tag in hack["tags"]]))
        
        # 編集・削除ボタン
        col1, col2 = st.columns(2)
        with col1:
            if st.button("✏️ 編集", key=f"edit_{i}"):
                st.session_state[f"editing_{i}"] = True
        with col2:
            if st.button("🗑 削除", key=f"del_{i}"):
                st.session_state[f"confirm_del_{i}"] = True

        # 編集モード
        if st.session_state.get(f"editing_{i}", False):
            new_title = st.text_input("タイトル", hack["title"], key=f"nt_{i}")
            new_content = st.text_area("内容（Markdown OK）", hack["content"], height=200, key=f"nc_{i}")
            new_tags = st.text_input("タグ", ",".join(hack.get("tags", [])), key=f"ntg_{i}")
            new_imp = st.slider("重要度", 1, 5, hack.get("importance", 3), key=f"ni_{i}")
            
            c1, c2 = st.columns(2)
            with c1:
                if st.button("保存", key=f"save_{i}"):
                    hack["title"] = new_title
                    hack["content"] = new_content
                    hack["tags"] = [t.strip() for t in new_tags.split(",") if t.strip()]
                    hack["importance"] = new_imp
                    hack["date"] = datetime.now().strftime("%Y-%m-%d %H:%M") + "（編集済）"
                    save_data(data)
                    st.session_state[f"editing_{i}"] = False
                    st.rerun()
            with c2:
                if st.button("キャンセル", key=f"can_{i}"):
                    st.session_state[f"editing_{i}"] = False
                    st.rerun()

        # 削除確認
        if st.session_state.get(f"confirm_del_{i}", False):
            st.warning("本当に削除しますか？")
            c1, c2 = st.columns(2)
            with c1:
                if st.button("はい", key=f"yes_{i}"):
                    data.remove(hack)
                    save_data(data)
                    st.success("削除しました")
                    st.rerun()
            with c2:
                if st.button("いいえ", key=f"no_{i}"):
                    st.session_state[f"confirm_del_{i}"] = False
                    st.rerun()

        # 返信部分（改行・Markdown対応）
        st.markdown("**スレッド返信**")
        for j, reply in enumerate(hack.get("replies", [])):
            st.markdown(reply["content"])
            # 返信編集・削除は簡略化（必要ならさらに拡張可能）

        # 新規返信
        reply_content = st.text_area("返信を追加（Markdown OK）", key=f"reply_{i}", height=100)
        if st.button("返信する", key=f"btn_{i}"):
            if reply_content.strip():
                hack.setdefault("replies", []).append({
                    "content": reply_content,
                    "date": datetime.now().strftime("%Y-%m-%d %H:%M")
                })
                save_data(data)
                st.success("返信追加！")
                st.rerun()
