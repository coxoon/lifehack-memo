import streamlit as st
import json
from datetime import datetime
import os

st.set_page_config(page_title="ライフハック・スレッドメモ", layout="wide")

CONFIG_FILE = "config.json"
DATA_FILE = "lifehacks.json"

# ====================== 設定 ======================
def load_config():
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {"password": None}

def save_config(config):
    with open(CONFIG_FILE, "w", encoding="utf-8") as f:
        json.dump(config, f, ensure_ascii=False, indent=2)

config = load_config()

# 初回パスワード設定
if config["password"] is None:
    st.title("🧠 初回パスワード設定")
    st.markdown("**初めての利用です。パスワードを設定してください。**")
    pw1 = st.text_input("パスワード", type="password", key="setup_pw1_unique")
    pw2 = st.text_input("パスワード（確認）", type="password", key="setup_pw2_unique")
    if st.button("設定する", type="primary", key="setup_button"):
        if pw1 and pw1 == pw2:
            config["password"] = pw1
            save_config(config)
            st.success("設定完了！")
            st.rerun()
        else:
            st.error("パスワードが一致しません")
    st.stop()

# ログイン
PASSWORD = config["password"]
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False

if not st.session_state.authenticated:
    st.title("🔒 ログイン")
    pw = st.text_input("パスワード", type="password", key="login_pw_unique")
    if st.button("ログイン", key="login_button"):
        if pw == PASSWORD:
            st.session_state.authenticated = True
            st.rerun()
        else:
            st.error("パスワードが違います")
    st.stop()

# ====================== メイン ======================
st.title("🧠 ライフハック・スレッドメモ帳")

with st.sidebar:
    st.header("⚙️ 設定")
    with st.expander("🔑 パスワード変更"):
        cur = st.text_input("現在のパスワード", type="password", key="change_cur_unique")
        new1 = st.text_input("新しいパスワード", type="password", key="change_new1_unique")
        new2 = st.text_input("確認", type="password", key="change_new2_unique")
        if st.button("変更する", key="change_pw_button"):
            if cur == PASSWORD and new1 == new2 and new1:
                config["password"] = new1
                save_config(config)
                st.success("変更完了！ 再度ログインしてください")
                st.session_state.authenticated = False
                st.rerun()
            else:
                st.error("入力エラー")

    sort_option = st.selectbox("並び順", ["最新順", "古い順"], key="sort_select")

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

# 新規投稿
with st.sidebar:
    st.markdown("---")
    st.header("📝 新規投稿")
    title = st.text_input("タイトル", key="new_title_unique")
    content = st.text_area("内容（改行OK）", height=180, key="new_content_unique")
    tags = st.text_input("タグ（カンマ区切り）", key="new_tags_unique")
    importance = st.slider("重要度 ⭐", 1, 5, 3, key="new_imp_unique")
    
    if st.button("投稿する", type="primary", key="post_button_unique"):
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

# ====================== 表示 ======================
st.subheader("📋 すべてのライフハック")

sorted_data = sorted(data, key=lambda x: x["date"], reverse=(sort_option == "最新順"))

all_tags = set(tag for h in data for tag in h.get("tags", []))
selected_tags = st.multiselect("タグでフィルタ", sorted(all_tags), key="tag_filter_unique")

display_data = [h for h in sorted_data if not selected_tags or any(t in h.get("tags", []) for t in selected_tags)]

for hack in display_data:
    stars = "⭐" * hack.get("importance", 3)
    
    with st.expander(f"{stars} {hack['title']} — {hack['date']}", expanded=False):
        
        st.markdown(hack['content'].replace('\n', '<br>'), unsafe_allow_html=True)
        
        if hack.get("tags"):
            st.caption(" ".join([f"`{t}`" for t in hack["tags"]]))

        # メイン編集・削除
        col1, col2 = st.columns(2)
        with col1:
            if st.button("✏️ 編集", key=f"edit_main_{hack['id']}_unique"):
                st.session_state[f"editing_main_{hack['id']}"] = True
        with col2:
            if st.button("🗑 削除", key=f"del_main_{hack['id']}_unique"):
                st.session_state[f"confirm_del_main_{hack['id']}"] = True

        # 編集モード
        if st.session_state.get(f"editing_main_{hack['id']}", False):
            new_title = st.text_input("タイトル", hack["title"], key=f"nt_{hack['id']}_unique")
            new_content = st.text_area("内容", hack["content"], height=200, key=f"nc_{hack['id']}_unique")
            new_tags = st.text_input("タグ", ",".join(hack.get("tags", [])), key=f"ntg_{hack['id']}_unique")
            new_imp = st.slider("重要度", 1, 5, hack.get("importance", 3), key=f"ni_{hack['id']}_unique")
            
            c1, c2 = st.columns(2)
            with c1:
                if st.button("✅ 保存", key=f"save_main_{hack['id']}_unique"):
                    hack["title"] = new_title
                    hack["content"] = new_content
                    hack["tags"] = [t.strip() for t in new_tags.split(",") if t.strip()]
                    hack["importance"] = new_imp
                    hack["date"] = datetime.now().strftime("%Y-%m-%d %H:%M") + "（編集済）"
                    save_data(data)
                    st.session_state[f"editing_main_{hack['id']}"] = False
                    st.rerun()
            with c2:
                if st.button("❌ キャンセル", key=f"cancel_main_{hack['id']}_unique"):
                    st.session_state[f"editing_main_{hack['id']}"] = False
                    st.rerun()

        # 削除確認
        if st.session_state.get(f"confirm_del_main_{hack['id']}", False):
            st.warning("本当に削除しますか？")
            c1, c2 = st.columns(2)
            with c1:
                if st.button("はい", key=f"yes_main_{hack['id']}_unique"):
                    data = [h for h in data if h["id"] != hack["id"]]
                    save_data(data)
                    st.success("削除しました")
                    st.rerun()
            with c2:
                if st.button("いいえ", key=f"no_main_{hack['id']}_unique"):
                    st.session_state[f"confirm_del_main_{hack['id']}"] = False
                    st.rerun()

        # 返信部分
        st.markdown("**スレッド返信**")
        for j, reply in enumerate(hack.get("replies", [])):
            st.markdown(reply['content'].replace('\n', '<br>'), unsafe_allow_html=True)
            
            rcol1, rcol2 = st.columns([1, 1])
            with rcol1:
                if st.button("✏️", key=f"edit_r_{hack['id']}_{j}_unique"):
                    st.session_state[f"editing_r_{hack['id']}_{j}"] = True
            with rcol2:
                if st.button("🗑", key=f"del_r_{hack['id']}_{j}_unique"):
                    st.session_state[f"confirm_del_r_{hack['id']}_{j}"] = True

            # 返信編集
            if st.session_state.get(f"editing_r_{hack['id']}_{j}", False):
                new_reply = st.text_area("返信編集", reply["content"], key=f"er_text_{hack['id']}_{j}_unique")
                c1, c2 = st.columns(2)
                with c1:
                    if st.button("保存", key=f"save_r_{hack['id']}_{j}_unique"):
                        hack["replies"][j]["content"] = new_reply
                        save_data(data)
                        st.session_state[f"editing_r_{hack['id']}_{j}"] = False
                        st.rerun()
                with c2:
                    if st.button("キャンセル", key=f"can_r_{hack['id']}_{j}_unique"):
                        st.session_state[f"editing_r_{hack['id']}_{j}"] = False
                        st.rerun()

            # 返信削除
            if st.session_state.get(f"confirm_del_r_{hack['id']}_{j}", False):
                st.warning("この返信を削除しますか？")
                c1, c2 = st.columns(2)
                with c1:
                    if st.button("はい", key=f"yes_r_{hack['id']}_{j}_unique"):
                        hack["replies"].pop(j)
                        save_data(data)
                        st.success("削除しました")
                        st.rerun()
                with c2:
                    if st.button("いいえ", key=f"no_r_{hack['id']}_{j}_unique"):
                        st.session_state[f"confirm_del_r_{hack['id']}_{j}"] = False
                        st.rerun()

        # 新規返信
        reply_text = st.text_area("返信を追加（改行OK）", key=f"new_reply_{hack['id']}_unique", height=100)
        if st.button("返信する", key=f"add_reply_{hack['id']}_unique"):
            if reply_text.strip():
                hack.setdefault("replies", []).append({
                    "content": reply_text,
                    "date": datetime.now().strftime("%Y-%m-%d %H:%M")
                })
                save_data(data)
                st.success("返信追加！")
                st.rerun()
