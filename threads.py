from db import db

def get_thread_info(id: int) -> tuple:
    sql = "SELECT u.username, t.creation_time, t.is_public FROM users u, threads t WHERE t.id=:id AND t.sender_id=u.id"
    thread = db.session.execute(sql, {"id":id})

    sql = "SELECT message FROM messages WHERE thread_id=:id"
    messages = db.session.execute(sql, {"id":id})

    return (thread.fetchall()[0], messages.fetchall())

def user_has_access(info) -> bool:
    return True

def get_all_public_threads() -> list:
    sql = "SELECT * FROM threads WHERE is_public=TRUE;"
    result = db.session.execute(sql)
    return result.fetchall()