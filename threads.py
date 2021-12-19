from db import db
import users
from flask import session

def get_thread_info(id: int) -> tuple:
    sql = "SELECT u.username, to_char(t.creation_time, 'yyyy-MM-dd HH24:MI') as creation_date, t.is_public, t.name FROM users u, threads t WHERE t.id=:id AND t.creator_id=u.id"
    thread = db.session.execute(sql, {"id":id})

    sql = "SELECT m.message, u.username, to_char(m.creation_time, 'yyyy-MM-dd HH24:MI') as creation_date FROM messages m, users u WHERE thread_id=:id AND m.sender_id=u.id"
    messages = db.session.execute(sql, {"id":id})

    return (thread.fetchall()[0], messages.fetchall())

def user_has_access(thread_id, csrf_token, method) -> bool:
    is_thread_public = is_public(thread_id)

    if is_thread_public:
        return True

    if "username" not in session:
        return False

    user_id = users.get_id(session["username"])

    if method == "POST" and session["csrf_token"] != csrf_token:
        return False
    
    sql = "SELECT * FROM thread_users WHERE user_id=:user_id AND thread_id=:thread_id;"
    result = db.session.execute(sql, {"user_id":user_id, "thread_id":thread_id})
    return bool(result.fetchone())

def get_all_public_threads(sort: tuple) -> list:
    if sort[0] != "name" and sort[0] != "username" and sort[0] != "creation_time":
        raise ValueError()

    if sort[1] != "ASC" and sort[1] != "DESC":
        raise ValueError()

    sort_sql = sort[0] + " " + sort[1]
    sql = ("SELECT t.id, to_char(t.creation_time, 'yyyy-MM-dd HH24:MI') as creation_date, t.name, u.username"
        " FROM threads t, users u WHERE t.creator_id=u.id AND t.is_public=TRUE ORDER BY " + sort_sql)
    result = db.session.execute(sql)
    return result.fetchall()

def create_thread(creator_id, is_public, name) -> int:
    sql = "INSERT INTO threads (creator_id, creation_time, is_public, name) VALUES (:creator_id, current_timestamp, :is_public, :name) RETURNING id;"
    result = db.session.execute(sql, {"creator_id":creator_id, "is_public":is_public, "name":name})
    db.session.commit()
    return int(result.fetchone().id)

def send_message(thread_id: int, sender_id: int, message: str):
    sql = "INSERT INTO messages (message, sender_id, thread_id, creation_time) VALUES (:message, :sender_id, :thread_id, current_timestamp)"
    db.session.execute(sql, {"message":message, "sender_id":sender_id, "thread_id":thread_id})
    db.session.commit()

def get_private_thread(user_id: int, friend_id: int):
    sql = "SELECT thread_id FROM thread_users WHERE user_id=:user_id OR user_id=:friend_id GROUP BY thread_id HAVING COUNT(*)=2;"
    result = db.session.execute(sql, {"user_id":user_id, "friend_id":friend_id})
    return result.fetchone()

def create_private_thread(user_id: int, friend_id: int) -> int:
    user_name = users.get_username(user_id)
    friend_name = users.get_username(friend_id)

    thread_id = create_thread(user_id, False, f"{user_name}, {friend_name}")

    add_thread_user(user_id, thread_id)
    add_thread_user(friend_id, thread_id)

    return thread_id 

def add_thread_user(user_id, thread_id):
    sql = "INSERT INTO thread_users (user_id, thread_id) VALUES (:user_id, :thread_id);"
    db.session.execute(sql, {"user_id":user_id, "thread_id":thread_id})
    db.session.commit()

def create_and_get_private_thread(user_id: int, friend_id: int) -> int:
    thread = get_private_thread(user_id, friend_id)

    if not thread:
        return create_private_thread(user_id, friend_id)
    else:
        return thread.thread_id

def is_public(thread_id: int) -> bool:
    sql = "SELECT is_public FROM threads WHERE id=:id"
    result = db.session.execute(sql, {"id":thread_id})
    return result.fetchone().is_public