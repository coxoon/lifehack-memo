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
    show_archive = st.checkbox("アーカイブを表示", value=False)
    
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
                "replies": [],
                "archived": False
            }
            data.append(new_hack)
            save_data(data)
            st.success("✅ 投稿しました！")
            st.rerun()

# ====================== メイン表示 ======================
st.title("🧠 ライフハック・スレッドメモ帳")

st.subheader("📋 すべてのライフハック")

# 表示対象（アーカイブ表示ON/OFF）
display_data = [h for h in data if not h.get("archived", False) or show_archive]

sorted_data = sorted(display_data, key=lambda x: x["date"], reverse=True)

for i, hack in enumerate(sorted_data):
    stars = "⭐" * hack.get("importance", 3)
    archive_mark = " 📦[アーカイブ]" if hack.get("archived", False) else ""
    
    with st.expander(f"{stars}{archive_mark} {hack['title']} — {hack['date']}", expanded=False):
        st.markdown(hack['content'].replace('\n', '<br>'), unsafe_allow_html=True)

        col1, col2, col3 = st.columns(3)
        with col1:
            if st.button("✏️ 編集", key=f"edit_main_{hack['id']}"):
                st.session_state[f"editing_main_{hack['id']}"] = True
        with col2:
            if st.button("🗑 削除", key=f"del_main_{hack['id']}"):
                st.session_state[f"confirm_del_main_{hack['id']}"] = True
        with col3:
            if hack.get("archived", False):
                if st.button("📤 元に戻す", key=f"unarchive_{hack['id']}"):
                    hack["archived"] = False
                    save_data(data)
                    st.rerun()
            else:
                if st.button("📦 アーカイブ", key=f"archive_{hack['id']}"):
                    hack["archived"] = True
                    save_data(data)
                    st.rerun()

        # 編集モード（簡略）
        if st.session_state.get(f"editing_main_{hack['id']}", False):
            # 編集UIは必要に応じて追加
            pass

        if st.session_state.get(f"confirm_del_main_{hack['id']}", False):
            st.warning("本当に削除しますか？")
            c1, c2 = st.columns(2)
            with c1:
                if st.button("はい", key=f"yes_del_{hack['id']}"):
                    data = [h for h in data if h["id"] != hack["id"]]
                    save_data(data)
                    st.success("削除しました")
                    st.rerun()
            with c2:
                if st.button("いいえ", key=f"no_del_{hack['id']}"):
                    st.session_state[f"confirm_del_main_{hack['id']}"] = False
                    st.rerun()

        # 返信機能
        st.markdown("**スレッド返信**")
        for j, reply in enumerate(hack.get("replies", [])):
            st.markdown(reply['content'].replace('\n', '<br>'), unsafe_allow_html=True)

        reply_text = st.text_area("返信を追加（改行OK）", key=f"new_reply_{hack['id']}", height=100)
        if st.button("返信する", key=f"add_reply_{hack['id']}"):
            if reply_text.strip():
                hack.setdefault("replies", []).append({
                    "content": reply_text,
                    "date": datetime.now().strftime("%Y-%m-%d %H:%M")
                })
                save_data(data)
                st.success("返信を追加しました！")
                st.rerun()
