from db import db

def get_thread_info(id: int) -> tuple:
    sql = "SELECT u.username, t.creation_time, t.is_public, t.name FROM users u, threads t WHERE t.id=:id AND t.creator_id=u.id"
    thread = db.session.execute(sql, {"id":id})

    sql = "SELECT message, sender_id, creation_time FROM messages WHERE thread_id=:id"
    messages = db.session.execute(sql, {"id":id})

    return (thread.fetchall()[0], messages.fetchall())

def user_has_access(info) -> bool:
    return True

def get_all_public_threads() -> list:
    sql = "SELECT * FROM threads WHERE is_public=TRUE;"
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