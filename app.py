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
    st.subheader("🔄 データ復元")
    uploaded_file = st.file_uploader("バックアップJSONを選択", type=["json"], key="restore_uploader")
    if uploaded_file is not None:
        if st.button("📤 復元する", type="primary", key="restore_btn"):
            try:
                restored_data = json.load(uploaded_file)
                if isinstance(restored_data, list):
                    save_data(restored_data)
                    st.success(f"✅ 復元完了！ {len(restored_data)}件復元しました。")
                    st.rerun()
                else:
                    st.error("❌ 正しい形式のファイルではありません。")
            except:
                st.error("❌ 読み込み失敗。正しいバックアップJSONを選択してください。")

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
            
            # 安全なリフレッシュ（これで確実に空になる）
            st.session_state.title_input = ""
            st.session_state.content_input = ""
            st.session_state.tags_input = ""
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
            if st.button("🗑 削除", key=f"del_main_{hack['id']}"):
                st.session_state[f"confirm_del_main_{hack['id']}"] = True

        if st.session_state.get(f"editing_main_{hack['id']}", False):
            new_title = st.text_input("タイトル", hack["title"], key=f"nt_{hack['id']}")
            new_content = st.text_area("内容", hack["content"], height=200, key=f"nc_{hack['id']}")
            new_tags = st.text_input("タグ", ",".join(hack.get("tags", [])), key=f"ntg_{hack['id']}")
            new_imp = st.slider("重要度", 1, 5, hack.get("importance", 3), key=f"ni_{hack['id']}")
            
            c1, c2 = st.columns(2)
            with c1:
                if st.button("✅ 保存", key=f"save_main_{hack['id']}"):
                    hack["title"] = new_title
                    hack["content"] = new_content
                    hack["tags"] = [t.strip() for t in new_tags.split(",") if t.strip()]
                    hack["importance"] = new_imp
                    hack["date"] = datetime.now().strftime("%Y-%m-%d %H:%M") + "（編集済）"
                    save_data(data)
                    st.session_state[f"editing_main_{hack['id']}"] = False
                    st.rerun()
            with c2:
                if st.button("❌ キャンセル", key=f"cancel_main_{hack['id']}"):
                    st.session_state[f"editing_main_{hack['id']}"] = False
                    st.rerun()

        # 返信機能
        st.markdown("**スレッド返信**")
        for j, reply in enumerate(hack.get("replies", [])):
            col1, col2, col3 = st.columns([6, 2, 2])
            with col1:
                st.markdown(reply['content'].replace('\n', '<br>'), unsafe_allow_html=True)
            with col2:
                if st.button("✏️", key=f"edit_r_{i}_{j}"):
                    st.session_state[f"edit_reply_{i}_{j}"] = True
            with col3:
                if st.button("🗑", key=f"del_r_{i}_{j}"):
                    st.session_state[f"del_reply_{i}_{j}"] = True

            if st.session_state.get(f"edit_reply_{i}_{j}", False):
                new_text = st.text_area("返信編集", reply["content"], key=f"edit_text_{i}_{j}")
                c1, c2 = st.columns(2)
                with c1:
                    if st.button("保存", key=f"save_r_{i}_{j}"):
                        hack["replies"][j]["content"] = new_text
                        hack["replies"][j]["date"] = datetime.now().strftime("%Y-%m-%d %H:%M") + "（編集済）"
                        save_data(data)
                        st.session_state[f"edit_reply_{i}_{j}"] = False
                        st.rerun()
                with c2:
                    if st.button("キャンセル", key=f"cancel_r_{i}_{j}"):
                        st.session_state[f"edit_reply_{i}_{j}"] = False
                        st.rerun()

            if st.session_state.get(f"del_reply_{i}_{j}", False):
                st.warning("この返信を削除しますか？")
                c1, c2 = st.columns(2)
                with c1:
                    if st.button("はい", key=f"yes_rdel_{i}_{j}"):
                        hack["replies"].pop(j)
                        save_data(data)
                        st.success("削除しました")
                        st.rerun()
                with c2:
                    if st.button("いいえ", key=f"no_rdel_{i}_{j}"):
                        st.session_state[f"del_reply_{i}_{j}"] = False
                        st.rerun()

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
