import streamlit as st
import json
from datetime import datetime
import os

st.set_page_config(page_title="ライフハック・スレッドメモ", layout="wide")

CONFIG_FILE = "config.json"
DATA_FILE = "lifehacks.json"

# ====================== 設定読み込み ======================
def load_config():
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {"password": None}  # 初回はNone

def save_config(config):
    with open(CONFIG_FILE, "w", encoding="utf-8") as f:
        json.dump(config, f, ensure_ascii=False, indent=2)

config = load_config()

# ====================== 初回パスワード設定 ======================
if config["password"] is None:
    st.title("🧠 初回パスワード設定")
    st.markdown("**初めての利用です。パスワードを設定してください。**")
    
    new_pw = st.text_input("パスワード", type="password", key="setup_pw")
    new_pw_confirm = st.text_input("パスワード（確認）", type="password", key="setup_pw_confirm")
    
    if st.button("パスワードを設定する", type="primary"):
        if new_pw and new_pw == new_pw_confirm:
            config["password"] = new_pw
            save_config(config)
            st.success("✅ パスワードを設定しました！")
            st.rerun()
        else:
            st.error("パスワードが一致しません")
    st.stop()

# ====================== ログイン ======================
PASSWORD = config["password"]

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
st.caption("アイデアをスレッド展開して深掘り・整理しよう")

with st.sidebar:
    st.header("⚙️ 設定")
    
    # パスワード変更
    with st.expander("🔑 パスワード変更"):
        current = st.text_input("現在のパスワード", type="password", key="curr")
        newp = st.text_input("新しいパスワード", type="password", key="newp")
        newp2 = st.text_input("新しいパスワード（確認）", type="password", key="newp2")
        if st.button("変更する"):
            if current == PASSWORD and newp == newp2 and newp:
                config["password"] = newp
                save_config(config)
                st.success("パスワード変更完了！ 再度ログインしてください。")
                st.session_state.authenticated = False
                st.rerun()
            else:
                st.error("入力に誤りがあります")

    dark_mode = st.toggle("🌙 ダークモード", False)
    sort_option = st.selectbox("並び順", ["最新順", "古い順"])

# ====================== データ処理 ======================
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
    st.markdown("---")
    st.header("📝 新規投稿")
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

# ====================== 表示部分 ======================
st.subheader("📋 ライフハック一覧")

# タグフィルタ
all_tags = set()
for h in data:
    all_tags.update(h.get("tags", []))
selected_tags = st.multiselect("🏷️ タグでフィルタ", sorted(all_tags), key="tag_filter")

# 並び替え
sorted_data = sorted(data, key=lambda x: x["date"], reverse=(sort_option == "最新順"))

# フィルタ適用
display_data = [h for h in sorted_data if not selected_tags or any(t in h.get("tags", []) for t in selected_tags)]

for idx, hack in enumerate(display_data):
    stars = "⭐" * hack.get("importance", 3)
    with st.expander(f"{stars} {hack['title']} — {hack['date']}"):
        st.markdown(hack['content'])
        if hack.get("tags"):
            st.caption(" ".join([f"`{t}`" for t in hack["tags"]]))
        
        # 編集・削除（簡略版）
        col1, col2 = st.columns(2)
        with col1:
            if st.button("✏️ 編集", key=f"e{idx}"):
                st.session_state[f"edit_{idx}"] = True
        with col2:
            if st.button("🗑 削除", key=f"d{idx}"):
                st.session_state[f"del_{idx}"] = True

        # 返信部分（Markdown対応）
        for r, reply in enumerate(hack.get("replies", [])):
            st.markdown(f"↳ {reply['content']}")
        
        reply_text = st.text_area("返信を追加（Markdown OK）", key=f"rep{idx}", height=80)
        if st.button("返信する", key=f"btn{idx}"):
            if reply_text.strip():
                hack.setdefault("replies", []).append({
                    "content": reply_text,
                    "date": datetime.now().strftime("%Y-%m-%d %H:%M")
                })
                save_data(data)
                st.rerun()

# バックアップ
if st.button("💾 全データをバックアップ"):
    st.download_button("ダウンロード", json.dumps(data, ensure_ascii=False, indent=2), "lifehacks_backup.json")
