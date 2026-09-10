# -*- coding: utf-8 -*-
"""
SQLiteデータベース管理モジュール (修正版)
"""

import sqlite3
import datetime

DB_PATH = "school_sns.db"

def get_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_connection()
    cur = conn.cursor()
    
    # ユーザーテーブル
    cur.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            grade INTEGER NOT NULL,
            class_num INTEGER NOT NULL,
            email TEXT NOT NULL,
            is_moderator INTEGER DEFAULT 0,
            bio TEXT,
            tags TEXT,
            avatar_emoji TEXT DEFAULT '🎓'
        )
    ''')
    
    # 掲示板テーブル
    cur.execute('''
        CREATE TABLE IF NOT EXISTS boards (
            id TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            description TEXT,
            board_type TEXT NOT NULL,
            created_by INTEGER
        )
    ''')
    
    # 投稿テーブル
    cur.execute('''
        CREATE TABLE IF NOT EXISTS posts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            board_id TEXT NOT NULL,
            author_id INTEGER NOT NULL,
            title TEXT,
            content TEXT NOT NULL,
            is_announcement INTEGER DEFAULT 0,
            is_hidden INTEGER DEFAULT 0,
            created_at TEXT NOT NULL
        )
    ''')
    
    # 通報テーブル
    cur.execute('''
        CREATE TABLE IF NOT EXISTS flags (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            post_id INTEGER NOT NULL,
            reporter_id INTEGER NOT NULL,
            reason TEXT NOT NULL,
            status TEXT DEFAULT 'pending',
            created_at TEXT NOT NULL
        )
    ''')
    
    conn.commit()
    
    # 初期サンプルデータの投入（修正：件数を正しく判定）
    cur.execute("SELECT COUNT(*) FROM users")
    count = cur.fetchone()
    
    if count == 0:
        sample_users = [
            ("山田 太郎", 1, 2, "yamada@highschool.ed.jp", 0, "1年2組の山田です！ボドゲとサッカーが好きです。", "サッカー部, ボードゲーム", "⚽"),
            ("佐藤 花子", 2, 1, "sato@highschool.ed.jp", 1, "生徒会＆生徒管理者です。みんなで良い学校SNSにしましょう！", "生徒会, 生徒管理者, 吹奏楽部", "🎷"),
            ("鈴木 健太", 3, 4, "suzuki@highschool.ed.jp", 0, "受験勉強中ですが息抜きに参加しました！", "軽音部, 受験生", "🎸"),
            ("高橋 美咲", 1, 1, "takahashi@highschool.ed.jp", 1, "生徒管理者を担当しています。気軽に声かけてね！", "生徒管理者, バスケ部", "🏀")
        ]
        cur.executemany("INSERT INTO users (name, grade, class_num, email, is_moderator, bio, tags, avatar_emoji) VALUES (?,?,?,?,?,?,?,?)", sample_users)
        
        sample_boards = [
            ("announcement", "📢 告知・募集専用板", "全校生徒向けのお知らせ・イベント・募集", "system", 0),
            ("grade_1", "1年生掲示板", "1年生専用の交流スペース", "system", 0),
            ("grade_2", "2年生掲示板", "2年生専用の交流スペース", "system", 0),
            ("grade_3", "3年生掲示板", "3年生専用の交流スペース", "system", 0),
            ("custom_boardgame", "🎲 ボードゲーム同好会", "放課後ボドゲやる人集まれ！", "custom", 1)
        ]
        cur.executemany("INSERT INTO boards (id, name, description, board_type, created_by) VALUES (?,?,?,?,?)", sample_boards)
        
        now_str = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
        sample_posts = [
            ("announcement", 2, "文化祭の有志ボランティア大募集！", "今年の文化祭の装飾スタッフを全校から募集しています！興味ある人は放課後生徒会室まで！", 1, 0, now_str),
            ("grade_1", 1, None, "今日の体育のダンス練習お疲れ様でしたー！みんな上手だった！", 0, 0, now_str),
            ("grade_2", 2, None, "修学旅行の自由行動、みんなどこ行く予定？", 0, 0, now_str),
            ("custom_boardgame", 1, None, "今週の金曜日、放課後にカタンかカロンやる人募集してます！", 0, 0, now_str)
        ]
        cur.executemany("INSERT INTO posts (board_id, author_id, title, content, is_announcement, is_hidden, created_at) VALUES (?,?,?,?,?,?,?)", sample_posts)
        conn.commit()
        
    conn.close()

def get_users():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM users")
    users = [dict(row) for row in cur.fetchall()]
    conn.close()
    return users

def get_user_by_id(user_id):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM users WHERE id = ?", (user_id,))
    row = cur.fetchone()
    conn.close()
    return dict(row) if row else None

def update_user_profile(user_id, bio, tags, avatar_emoji):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("UPDATE users SET bio = ?, tags = ?, avatar_emoji = ? WHERE id = ?", (bio, tags, avatar_emoji, user_id))
    conn.commit()
    conn.close()

def get_boards(board_type=None):
    conn = get_connection()
    cur = conn.cursor()
    if board_type:
        cur.execute("SELECT * FROM boards WHERE board_type = ?", (board_type,))
    else:
        cur.execute("SELECT * FROM boards")
    boards = [dict(row) for row in cur.fetchall()]
    conn.close()
    return boards

def create_board(board_id, name, description, created_by):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("INSERT INTO boards (id, name, description, board_type, created_by) VALUES (?, ?, ?, 'custom', ?)", (board_id, name, description, created_by))
    conn.commit()
    conn.close()

def get_posts(board_id=None):
    conn = get_connection()
    cur = conn.cursor()
    query = '''
        SELECT p.*, u.name as author_name, u.grade as author_grade, u.class_num as author_class,
               u.avatar_emoji as author_avatar, u.is_moderator as author_is_mod, b.name as board_name
        FROM posts p
        JOIN users u ON p.author_id = u.id
        JOIN boards b ON p.board_id = b.id
        WHERE p.is_hidden = 0
    '''
    params = []
    if board_id:
        query += " AND p.board_id = ?"
        params.append(board_id)
    query += " ORDER BY p.id DESC"
    
    cur.execute(query, params)
    posts = [dict(row) for row in cur.fetchall()]
    conn.close()
    return posts

def create_post(board_id, author_id, content, title=None, is_announcement=0):
    conn = get_connection()
    cur = conn.cursor()
    now_str = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
    cur.execute('''
        INSERT INTO posts (board_id, author_id, title, content, is_announcement, created_at)
        VALUES (?, ?, ?, ?, ?, ?)
    ''', (board_id, author_id, title, content, is_announcement, now_str))
    conn.commit()
    conn.close()

def flag_post(post_id, reporter_id, reason):
    conn = get_connection()
    cur = conn.cursor()
    now_str = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
    cur.execute("INSERT INTO flags (post_id, reporter_id, reason, created_at) VALUES (?, ?, ?, ?)", (post_id, reporter_id, reason, now_str))
    cur.execute("UPDATE posts SET is_hidden = 1 WHERE id = ?", (post_id,))
    conn.commit()
    conn.close()

def get_flagged_posts():
    conn = get_connection()
    cur = conn.cursor()
    query = '''
        SELECT f.id as flag_id, f.reason, f.created_at as flagged_at,
               p.id as post_id, p.content, u_author.name as author_name,
               u_reporter.name as reporter_name, b.name as board_name
        FROM flags f
        JOIN posts p ON f.post_id = p.id
        JOIN users u_author ON p.author_id = u_author.id
        JOIN users u_reporter ON f.reporter_id = u_reporter.id
        JOIN boards b ON p.board_id = b.id
        WHERE f.status = 'pending'
    '''
    cur.execute(query)
    flags = [dict(row) for row in cur.fetchall()]
    conn.close()
    return flags

def resolve_flag(flag_id, action):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT post_id FROM flags WHERE id = ?", (flag_id,))
    res = cur.fetchone()
    if res:
        post_id = res
        if action == "restore":
            cur.execute("UPDATE posts SET is_hidden = 0 WHERE id = ?", (post_id,))
        cur.execute("UPDATE flags SET status = ? WHERE id = ?", (action, flag_id))
        conn.commit()
    conn.close()
