# -*- coding: utf-8 -*-
"""
School SNS Application Prototype (Streamlit)
高校生向け全校コミュニティSNS「校内コネクト (SchoolConnect)」
"""

import streamlit as st
import database as db
import config
import datetime

# ページ基本設定
st.set_page_config(
    page_title="校内コネクト | 高校生主体SNS",
    page_icon="🏫",
    layout="wide",
    initial_sidebar_state="expanded"
)

# データベース初期化
db.init_db()

# --- カスタムCSS（クラスルーム風の明るいUIデザイン） ---
st.markdown("""
<style>
    .stApp {
        background-color: #f8f9fa;
    }
    .post-card {
        background-color: #ffffff;
        border-radius: 12px;
        padding: 18px 22px;
        margin-bottom: 16px;
        box-shadow: 0 2px 8px rgba(0,0,0,0.05);
        border-left: 5px solid #4a90e2;
    }
    .announcement-card {
        border-left: 5px solid #f39c12 !important;
        background-color: #fffdf8 !important;
    }
    .profile-card {
        background-color: #ffffff;
        border-radius: 16px;
        padding: 24px;
        box-shadow: 0 4px 12px rgba(0,0,0,0.08);
        border: 1px solid #e1e8ed;
        margin-bottom: 20px;
    }
    .mod-badge {
        background-color: #27ae60;
        color: white;
        padding: 2px 8px;
        border-radius: 12px;
        font-size: 0.75rem;
        font-weight: bold;
        margin-left: 6px;
    }
    .user-info-text {
        color: #555555;
        font-size: 0.88rem;
    }
    .tag-chip {
        background-color: #eef2f7;
        color: #334e68;
        padding: 4px 12px;
        border-radius: 15px;
        font-size: 0.85rem;
        margin-right: 6px;
        margin-top: 4px;
        display: inline-block;
        font-weight: 500;
    }
</style>
""", unsafe_allow_html=True)

# --- セッション状態の初期化 ---
if "current_user_id" not in st.session_state:
    st.session_state.current_user_id = 1  # デフォルト: 山田太郎 (生徒)

users = db.get_users()

# --- 安全なユーザー取得とエラー防止処理 ---
user_options = {u["id"]: f"{u['avatar_emoji']} {u['grade']}年{u['class_num']}組 {u['name']} " + ("(生徒管理者)" if u["is_moderator"] else "(一般生徒)") for u in users}
user_ids = list(user_options.keys())

# ユーザーデータが存在しない場合の安全ガード
if not user_ids:
    st.error("⚠️ ユーザーデータが正しく読み込めませんでした。database.py が同じフォルダにあるか確認してください。")
    st.stop()

# セッションIDがリストに存在しない場合の自動補正
if st.session_state.current_user_id not in user_ids:
    st.session_state.current_user_id = user_ids

default_index = user_ids.index(st.session_state.current_user_id)
current_user = db.get_user_by_id(st.session_state.current_user_id)

# --- サイドバー：アカウント切り替え ---
with st.sidebar:
    st.title("🏫 校内コネクト")
    st.caption("生徒主体でつくる、高校生限定コミュニティ")
    st.divider()

    st.subheader("👤 模擬ログイン切替")
    selected_u_id = st.selectbox(
        "テスト用アカウントを選択:",
        options=user_ids,
        format_func=lambda x: user_options[x],
        index=default_index
    )
    if selected_u_id != st.session_state.current_user_id:
        st.session_state.current_user_id = selected_u_id
        st.rerun()

    # 現在のログインプロフィール（簡易表示）
    st.divider()
    st.markdown(f"### {current_user['avatar_emoji']} {current_user['name']}")
    st.markdown(f"<span class='user-info-text'>{current_user['grade']}年{current_user['class_num']}組 | {current_user['email']}</span>", unsafe_allow_html=True)
    if current_user["is_moderator"]:
        st.markdown("<span class='mod-badge'>🛡️ 生徒管理者</span>", unsafe_allow_html=True)
    
    st.info("💡 詳細なプロフィールの確認や編集は、メイン画面の **「👤 マイプロフィール」タブ** から行えます。")

    st.divider()
    st.caption("🔒 全校生徒実名制認証プラグイン稼働中 (`@highschool.ed.jp`)")


# --- メインコンテンツ領域 ---
st.title("🌟 校内コネクト ダッシュボード")

# ナビゲーションタブ
tab_names = ["🏠 全校タイムライン", "📢 告知・募集専用板", "🏫 学年別掲示板", "💬 話題グループ(スレッド)", "👤 マイプロフィール", "🛡️ 生徒管理者パネル"]
tabs = st.tabs(tab_names)

# ---------------------------------------------------------
# TAB 1: 全校タイムライン
# ---------------------------------------------------------
with tabs:
    st.subheader("📢 全校タイムライン")
    st.caption("全校の告知や学年別・グループの更新が一覧で確認できます。気軽に声をかけてみましょう！")

    # 投稿フォーム
    with st.form("main_post_form", clear_on_submit=True):
        st.write("✏️ **全校へメッセージを投稿する**")
        post_title = st.text_input("タイトル（任意）", placeholder="例: 放課後の自習仲間募集！")
        post_content = st.text_area("本文 (※実名で投稿されます。NGワード自動チェック機能つき)", placeholder="今日一緒に図書館で勉強できる人いませんかー？", height=100)
        target_board = st.selectbox("投稿先掲示板", options=["announcement", "grade_1", "grade_2", "grade_3"], format_func=lambda x: {"announcement": "📢 告知・募集専用板", "grade_1": "1年生掲示板", "grade_2": "2年生掲示板", "grade_3": "3年生掲示板"}[x])
        
        is_anno = 1 if target_board == "announcement" else 0
        submit_post = st.form_submit_button("投稿する")

        if submit_post:
            if not post_content.strip():
                st.warning("本文を入力してください。")
            else:
                # NGワードリアルタイムチェック
                has_ng, ng_words, sanitized = config.check_ng_words(post_content)
                if has_ng:
                    st.error(f"⚠️ 投稿内に不適切な言葉が含まれている可能性があります: **[{', '.join(ng_words)}]**")
                    st.info(f"💡 自動修正案 (伏字処理): 「{sanitized}」")
                    if st.checkbox("自動伏字処理して投稿を続行する"):
                        db.create_post(target_board, current_user["id"], sanitized, post_title, is_anno)
                        st.success("投稿を公開しました！")
                        st.rerun()
                else:
                    db.create_post(target_board, current_user["id"], post_content, post_title, is_anno)
                    st.success("投稿を公開しました！")
                    st.rerun()

    st.divider()

    # タイムライン投稿一覧
    posts = db.get_posts()
    for post in posts:
        card_class = "post-card announcement-card" if post["is_announcement"] else "post-card"
        mod_badge = "<span class='mod-badge'>🛡️ 生徒管理者</span>" if post["author_is_mod"] else ""
        
        st.markdown(f"""
        <div class='{card_class}'>
            <div style='display: flex; justify-content: space-between; align-items: center;'>
                <div>
                    <span style='font-size: 1.2rem;'>{post['author_avatar']} <b>{post['author_name']}</b></span>
                    <span class='user-info-text'>({post['author_grade']}年{post['author_class']}組)</span> {mod_badge}
                </div>
                <div style='color: #888; font-size: 0.8rem;'>
                    📌 投稿先: {post['board_name']} | 🕒 {post['created_at']}
                </div>
            </div>
            <h4 style='margin-top: 10px; margin-bottom: 5px;'>{post['title'] or ''}</h4>
            <p style='font-size: 1.05rem; line-height: 1.6; color: #2c3e50;'>{post['content']}</p>
        </div>
        """, unsafe_allow_html=True)

        # 通報機能ボタン
        col_flag, col_space = st.columns([1, 3])
        with col_flag:
            with st.popover("🚩 通報する"):
                flag_reason = st.text_input("通報理由 (例: 誹謗中傷、個人情報)", key=f"flag_reason_{post['id']}")
                if st.button("送信", key=f"flag_btn_{post['id']}"):
                    if flag_reason:
                        db.flag_post(post["id"], current_user["id"], flag_reason)
                        st.warning("生徒管理者に通報しました。確認まで一時非表示になります。")
                        st.rerun()


# ---------------------------------------------------------
# TAB 2: 告知・募集専用板
# ---------------------------------------------------------
with tabs[1]:
    st.subheader("📢 告知・募集専用板")
    st.info("💡 部活動の練習試合応援、有志イベント、落とし物情報、ボランティアメンバー募集などを全校生徒に向けてお知らせする専用スペースです。")

    anno_posts = db.get_posts(board_id="announcement")
    for post in anno_posts:
        st.markdown(f"""
        <div class='post-card announcement-card'>
            <div style='font-size: 1.1rem; color: #d35400;'><b>📣 【全校告知】 {post['title'] or 'お知らせ'}</b></div>
            <div style='margin-top: 5px;'>{post['author_avatar']} <b>{post['author_name']}</b> ({post['author_grade']}年{post['author_class']}組)</div>
            <p style='font-size: 1.05rem; margin-top: 10px;'>{post['content']}</p>
            <div style='color: #888; font-size: 0.8rem;'>🕒 {post['created_at']}</div>
        </div>
        """, unsafe_allow_html=True)


# ---------------------------------------------------------
# TAB 3: 学年別掲示板
# ---------------------------------------------------------
with tabs[4]:
    st.subheader("🏫 学年別掲示板")
    st.caption("デフォルトで設置されている同級生限定の雑談・情報共有掲示板です。")

    grade_sub_tabs = st.tabs(["1年生の板", "2年生の板", "3年生の板"])
    for i, g_tab in enumerate(grade_sub_tabs, start=1):
        with g_tab:
            st.markdown(f"#### 🏫 {i}年生専用タイムライン")
            g_posts = db.get_posts(board_id=f"grade_{i}")
            if not g_posts:
                st.info("まだ投稿がありません。最初のメッセージを投稿してみましょう！")
            for post in g_posts:
                st.markdown(f"""
                <div class='post-card'>
                    <div><b>{post['author_avatar']} {post['author_name']}</b> ({post['author_grade']}年{post['author_class']}組)</div>
                    <p style='font-size: 1.05rem; margin-top: 8px;'>{post['content']}</p>
                    <div style='color: #888; font-size: 0.8rem;'>🕒 {post['created_at']}</div>
                </div>
                """, unsafe_allow_html=True)


# ---------------------------------------------------------
# TAB 4: 話題グループ(スレッド)
# ---------------------------------------------------------
with tabs[2]:
    st.subheader("💬 話題別カスタムグループ")
    st.caption("好きな話題、部活動、趣味、文化祭企画などで自由にグループを作成して会話できます。")

    col_groups, col_create = st.columns([1, 4])

    with col_create:
        st.markdown("### ➕ 新しいグループを作る")
        with st.form("create_group_form"):
            g_name = st.text_input("グループ名", placeholder="例: ⚽ サッカー同好会")
            g_desc = st.text_area("説明", placeholder="例: 週末のフットサルやサッカーの話題で盛り上がるグループです！")
            submit_g = st.form_submit_button("グループを作成")
            if submit_g:
                if g_name.strip():
                    new_b_id = f"custom_{int(datetime.datetime.now().timestamp())}"
                    db.create_board(new_b_id, g_name, g_desc, current_user["id"])
                    st.success(f"グループ「{g_name}」を作成しました！")
                    st.rerun()

    with col_groups:
        custom_boards = db.get_boards(board_type="custom")
        if not custom_boards:
            st.info("現在カスタムグループはありません。")
        else:
            selected_custom = st.selectbox("表示するグループを選択:", options=[b["id"] for b in custom_boards], format_func=lambda x: [b["name"] for b in custom_boards if b["id"] == x])
            
            c_board_info = [b for b in custom_boards if b["id"] == selected_custom]
            st.markdown(f"### {c_board_info['name']}")
            st.write(f"📝 **説明:** {c_board_info['description']}")

            # グループ内投稿フォーム
            with st.form(f"custom_post_{selected_custom}", clear_on_submit=True):
                c_content = st.text_area("グループにメッセージを送信", placeholder="気軽にコメントしてみよう！")
                c_submit = st.form_submit_button("送信")
                if c_submit and c_content.strip():
                    has_ng, ng_words, sanitized = config.check_ng_words(c_content)
                    final_content = sanitized if has_ng else c_content
                    db.create_post(selected_custom, current_user["id"], final_content)
                    st.rerun()

            st.divider()

            c_posts = db.get_posts(board_id=selected_custom)
            for post in c_posts:
                st.markdown(f"""
                <div class='post-card'>
                    <div><b>{post['author_avatar']} {post['author_name']}</b> ({post['author_grade']}年{post['author_class']}組)</div>
                    <p style='font-size: 1.05rem; margin-top: 8px;'>{post['content']}</p>
                    <div style='color: #888; font-size: 0.8rem;'>🕒 {post['created_at']}</div>
                </div>
                """, unsafe_allow_html=True)


# ---------------------------------------------------------
# TAB 5: 👤 マイプロフィール (専用タブ)
# ---------------------------------------------------------
with tabs[5]:
    st.subheader("👤 マイプロフィール・アカウント設定")
    st.caption("全校生徒へ公開されるプロフィールカードの確認と編集、および自分の過去投稿履歴を管理できます。")

    col_prof_view, col_prof_edit = st.columns([1])

    with col_prof_view:
        st.markdown("### 🪪 プロフィールカード（全校公開プレビュー）")
        mod_badge_html = "<span class='mod-badge'>🛡️ 生徒管理者</span>" if current_user["is_moderator"] else ""
        
        tags_html = ""
        if current_user["tags"]:
            tags_list = current_user["tags"].split(",")
            tags_html = " ".join([f"<span class='tag-chip'>#{t.strip()}</span>" for t in tags_list])

        st.markdown(f"""
        <div class='profile-card'>
            <div style='display: flex; align-items: center; gap: 15px;'>
                <div style='font-size: 3.5rem; background-color: #f0f4f8; border-radius: 50%; width: 80px; height: 80px; display: flex; align-items: center; justify-content: center;'>
                    {current_user['avatar_emoji']}
                </div>
                <div>
                    <h2 style='margin: 0; padding: 0;'>{current_user['name']} {mod_badge_html}</h2>
                    <p style='color: #555; margin-top: 4px; font-size: 1rem;'>
                        🏫 {current_user['grade']}年 {current_user['class_num']}組 | ✉️ {current_user['email']}
                    </p>
                    <span style='background-color: #e8f5e9; color: #2e7d32; font-size: 0.75rem; padding: 2px 8px; border-radius: 10px; font-weight: bold;'>
                        ✔ 校内ドメイン認証済み生徒
                    </span>
                </div>
            </div>
            <hr style='border: none; border-top: 1px solid #eee; margin: 16px 0;'>
            <div>
                <p style='font-weight: bold; color: #333; margin-bottom: 6px;'>💬 自己紹介・メッセージ:</p>
                <p style='font-size: 1.05rem; line-height: 1.6; color: #2c3e50; background-color: #f9fbfd; padding: 12px; border-radius: 8px;'>
                    {current_user['bio'] or '自己紹介がまだ設定されていません。右側のフォームから追加してみましょう！'}
                </p>
            </div>
            <div style='margin-top: 12px;'>
                <p style='font-weight: bold; color: #333; margin-bottom: 6px;'>🏷️ 関心・部活・趣味タグ:</p>
                <div>{tags_html or '<span style="color:#888; font-size:0.9rem;">タグ未設定</span>'}</div>
            </div>
        </div>
        """, unsafe_allow_html=True)

    with col_prof_edit:
        st.markdown("### ✏️ プロフィールを編集する")
        with st.form("edit_profile_tab_form"):
            edit_emoji = st.text_input("アバター絵文字", value=current_user["avatar_emoji"])
            edit_bio = st.text_area("自己紹介文", value=current_user["bio"] or "", placeholder="趣味や所属している部活、話したいテーマなどを自由に書こう！", height=120)
            edit_tags = st.text_input("関心・部活タグ (カンマ区切り)", value=current_user["tags"] or "", placeholder="サッカー部, ボードゲーム, 文化祭実行委員")
            
            submit_profile_tab = st.form_submit_button("💾 プロフィールを保存")
            if submit_profile_tab:
                db.update_user_profile(current_user["id"], edit_bio, edit_tags, edit_emoji)
                st.success("プロフィールを更新しました！")
                st.rerun()

    st.divider()

    # 自身の投稿履歴
    st.markdown("### 📜 あなたの過去の投稿履歴")
    all_posts = db.get_posts()
    my_posts = [p for p in all_posts if p["author_id"] == current_user["id"]]

    if not my_posts:
        st.info("まだ投稿がありません。「全校タイムライン」や「話題グループ」でメッセージを発信してみましょう！")
    else:
        for post in my_posts:
            st.markdown(f"""
            <div class='post-card'>
                <div style='display: flex; justify-content: space-between;'>
                    <div><b>📌 投稿先: {post['board_name']}</b></div>
                    <div style='color: #888; font-size: 0.8rem;'>🕒 {post['created_at']}</div>
                </div>
                <h4 style='margin-top: 8px; margin-bottom: 4px;'>{post['title'] or ''}</h4>
                <p style='font-size: 1rem; color: #333;'>{post['content']}</p>
            </div>
            """, unsafe_allow_html=True)


# ---------------------------------------------------------
# TAB 6: 生徒管理者パネル
# ---------------------------------------------------------
with tabs[3]:
    st.subheader("🛡️ 生徒管理者（モデレーター）パネル")
    
    if not current_user["is_moderator"]:
        st.warning("⚠️ このエリアは生徒の中から選ばれた「生徒管理者」のみアクセス可能です。")
        st.info("左側のサイドバーから「佐藤 花子」または「高橋 美咲」アカウントに切り替えると、管理者機能を体験できます。")
    else:
        st.success("✅ 生徒管理者としてログインしています。学校コミュニティの健全性を保ちましょう。")

        st.markdown("### 🚩 通報された投稿の一覧・確認")
        flagged_items = db.get_flagged_posts()

        if not flagged_items:
            st.info("現在、確認が必要な通報案件はありません。コミュニティは平和です！")
        else:
            for flag in flagged_items:
                with st.expander(f"⚠️ 通報案件 #{flag['flag_id']} | 投稿者: {flag['author_name']} (掲示板: {flag['board_name']})", expanded=True):
                    st.write(f"**投稿内容:** {flag['content']}")
                    st.write(f"**通報者:** {flag['reporter_name']} | **理由:** {flag['reason']}")
                    st.caption(f"通報日時: {flag['flagged_at']}")

                    col_act1, col_act2 = st.columns(2)
                    with col_act1:
                        if st.button("🚫 投稿を非表示のまま確定 (削除)", key=f"hide_{flag['flag_id']}"):
                            db.resolve_flag(flag['flag_id'], "hide")
                            st.success("投稿を非表示に確定しました。")
                            st.rerun()
                    with col_act2:
                        if st.button("✅ 問題なしとして投稿を復元", key=f"restore_{flag['flag_id']}"):
                            db.resolve_flag(flag['flag_id'], "restore")
                            st.success("投稿を復元しました。")
                            st.rerun()

        st.divider()
        st.markdown("### ⚙️ NGワードフィルター設定一覧")
        st.write("現在アクティブなNGワード（自動検出キーワード）:")
        st.code(", ".join(config.DEFAULT_NG_WORDS))
        st.caption("※文脈判断を重視しつつ、過剰検知を防ぐため生徒管理者間で定期的に見直します。")


# --- フッター（設計の背景） ---
st.divider()
st.caption("""
💡 **設計根拠と安全ガイドライン:**
本プロトタイプは校内コミュニティ事例およびコンテンツモデレーション研究に基づき、以下を実装しています。
1. 学年・全校・有志グループの階層化による投稿の心理的ハードル低下と所属感醸成 [1, 2]
2. 専用プロフィールタブによる実名制認証・信頼感の醸成 [1]
3. 投稿前リアルタイムNGワードフィルタリングによる誤爆・トラブルの未然防止 [2, 4]
4. ユーザー通報と生徒管理者による二段構えの自律的コミュニティ運営 [2, 4]
""")