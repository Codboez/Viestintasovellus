from db import db
import re
from werkzeug.security import check_password_hash, generate_password_hash

def register(username, password, confirmed_password) -> bool:
    if len(username) < 1 or len(username) > 32:
        return False

    if username_exists(username):
        return False

    if not is_password_valid(password):
        return False

    if not passwords_match(password, confirmed_password):
        return False

    insert_user(username, password)
    return True

def username_exists(username: str) -> bool:
    sql = "SELECT username FROM users WHERE username=:username"
    result = db.session.execute(sql, {"username":username})

    return result.fetchone()

def is_password_valid(password: str) -> bool:
    if len(password) > 32 or len(password) < 8:
        return False

    if not re.search("\d", password):
        return False

    if not re.search("[a-z]", password):
        return False

    if not re.search("[A-Z]", password):
        return False

    return True

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