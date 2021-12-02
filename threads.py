from db import db

def get_thread_info(id: int) -> tuple:
    sql = "SELECT u.username, t.creation_time, t.is_public, t.name FROM users u, threads t WHERE t.id=:id AND t.creator_id=u.id"
    thread = db.session.execute(sql, {"id":id})

    sql = "SELECT m.message, u.username, m.creation_time FROM messages m, users u WHERE thread_id=:id AND m.sender_id=u.id"
    messages = db.session.execute(sql, {"id":id})

    return (thread.fetchall()[0], messages.fetchall())

# Will do this later. Currently just sending random info here.
def user_has_access(info) -> bool:
    return True

def get_all_public_threads() -> list:
    sql = "SELECT t.id, to_char(t.creation_time, 'yyyy-MM-dd HH24:MI') as creation_date, t.name, u.username FROM threads t, users u WHERE t.creator_id=u.id AND t.is_public=TRUE;"
    result = db.session.execute(sql)
    return result.fetchall()

def create_thread(creator_id, is_public, name):
    sql = "INSERT INTO threads (creator_id, creation_time, is_public, name) VALUES (:creator_id, current_timestamp, :is_public, :name);"
    db.session.execute(sql, {"creator_id":creator_id, "is_public":is_public, "name":name})
    db.session.commit()

def get_thread_amount() -> int:
    sql = "SELECT COUNT(*) c FROM threads"
    result = db.session.execute(sql)
    return int(result.fetchone().c)

def send_message(thread_id: int, sender_id: int, message: str):
    sql = "INSERT INTO messages (message, sender_id, thread_id, creation_time) VALUES (:message, :sender_id, :thread_id, current_timestamp)"
    db.session.execute(sql, {"message":message, "sender_id":sender_id, "thread_id":thread_id})
    db.session.commit()