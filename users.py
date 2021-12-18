from db import db
import re
from werkzeug.security import check_password_hash, generate_password_hash
from flask import session
import users

def register(username, password, confirmed_password) -> tuple:
    if len(username) < 1 or len(username) > 32:
        return (False, "Username must be between 1 and 32 characters long")

    if username_exists(username):
        return (False, "This username already exists")

    password_valid = is_password_valid(password)
    if not password_valid[0]:
        return (False, password_valid[1])

    if not passwords_match(password, confirmed_password):
        return (False, "Passwords do not match")

    insert_user(username, password)
    return (True, "")

def username_exists(username: str) -> bool:
    sql = "SELECT username FROM users WHERE username=:username"
    result = db.session.execute(sql, {"username":username})

    return result.fetchone()

def is_password_valid(password: str) -> tuple:
    if len(password) > 32 or len(password) < 8:
        return (False, "Password must be between 8 and 32 characters long")

    if not re.search("\d", password):
        return (False, "Password must contain a number, lower case and an upper case character")

    if not re.search("[a-z]", password):
        return (False, "Password must contain a number, lower case and an upper case character")

    if not re.search("[A-Z]", password):
        return (False, "Password must contain a number, lower case and an upper case character")

    return (True, "")

def passwords_match(password: str, confirmed_password: str) -> bool:
    return password == confirmed_password

def insert_user(username: str, password: str):
    sql = "INSERT INTO users (username, password) VALUES (:username, :password)"
    db.session.execute(sql, {"username":username, "password":generate_password_hash(password)})
    db.session.commit()

def login(username: str, password: str) -> bool:
    sql = "SELECT id, password FROM users WHERE username=:username"
    result = db.session.execute(sql, {"username":username})

    user = result.fetchone()

    if not user:
        return False

    return check_password_hash(user.password, password)

def get_id(username: str) -> int:
    sql = "SELECT id FROM users WHERE username=:username"
    result = db.session.execute(sql, {"username":username})
    return int(result.fetchone().id)

def get_friends(id: int):
    sql = "SELECT u.id, u.username FROM users u, friends f WHERE u.id=f.friend_id AND f.user_id=:id"
    result = db.session.execute(sql, {"id":id})
    return result.fetchall()

def has_friend(user1_id: int, user2_id: int) -> bool:
    sql = "SELECT * FROM friends WHERE user_id=:id1 AND friend_id=:id2;"
    result = db.session.execute(sql, {"id1":user1_id, "id2":user2_id})
    return result.fetchone()

def username_exists(username: str) -> bool:
    sql = "SELECT * FROM users WHERE username=:username;"
    result = db.session.execute(sql, {"username":username})
    return result.fetchone()

def send_friend_request(user1_id: int, user2_id: int):
    sql = "INSERT INTO friend_requests (sender_id, recipient_id) VALUES (:id1, :id2);"
    db.session.execute(sql, {"id1":user1_id, "id2":user2_id})
    db.session.commit()

def get_friend_requests(user_id: int):
    sql = "SELECT u.id, u.username FROM users u, friend_requests f WHERE u.id=f.sender_id AND f.recipient_id=:id"
    result = db.session.execute(sql, {"id":user_id})
    return result.fetchall()

def add_friend(id1: int, id2: int):
    sql = "INSERT INTO friends (user_id, friend_id) VALUES (:id1, :id2);"
    db.session.execute(sql, {"id1":id1, "id2":id2})
    db.session.execute(sql, {"id1":id2, "id2":id1})
    db.session.commit()

def remove_friend_request(sender_id: int, recipient_id: int):
    sql = "DELETE FROM friend_requests WHERE sender_id=:sender_id AND recipient_id=:recipient_id;"
    db.session.execute(sql, {"sender_id":sender_id, "recipient_id":recipient_id})
    db.session.commit()

def friend_request_exists(sender_id: int, recipient_id: int):
    sql = "SELECT * FROM friend_requests WHERE (sender_id=:sender_id AND recipient_id=:recipient_id) OR (sender_id=:recipient_id AND recipient_id=:sender_id);"
    result = db.session.execute(sql, {"sender_id":sender_id, "recipient_id":recipient_id})
    return result.fetchone()

def get_username(id: int) -> str:
    sql = "SELECT username FROM users WHERE id=:id"
    result = db.session.execute(sql, {"id":id})
    return str(result.fetchone().username)

def setup_sidebar_arguments(args: dict) -> dict:
    friends = []
    friend_requests = []
    if "username" in session:
        friends = users.get_friends(users.get_id(session["username"]))
        friend_requests = users.get_friend_requests(users.get_id(session["username"]))

    tab = args.get("tab")
    friend_request_message = args.get("friend_request")

    return {"friends":friends, "requests":friend_requests, "tab":tab, "friend_request":friend_request_message}