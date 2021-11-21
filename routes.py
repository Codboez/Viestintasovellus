from app import app
from flask import redirect, render_template, request, session
import users
import threads

@app.route("/")
def index():
    thread_list = threads.get_all_public_threads()
    return render_template("index.html", threads=thread_list)

@app.route("/register")
def register():
    return render_template("register.html")

@app.route("/login")
def login():
    return render_template("login.html")

@app.route("/register/send", methods=["POST"])
def send_register():
    if users.register(request.form["username"], request.form["password"], request.form["confirm_password"]):
        return redirect("/")
    else:
        return redirect("/invalid_credentials")

@app.route("/login/send", methods=["POST"])
def send_login():
    username = request.form["username"]
    password = request.form["password"]

    if users.login(username, password):
        session["username"] = username
        return redirect("/")
    else:
        return redirect("/invalid_credentials")

@app.route("/logout")
def logout():
    del session["username"]
    return redirect("/")

@app.route("/invalid_credentials")
def invalid_credentials():
    return render_template("invalid_credentials.html")

@app.route("/threads/<int:id>", methods=["GET", "POST"])
def thread(id: int):
    info = threads.get_thread_info(id)

    if threads.user_has_access(info):
        return render_template("thread.html", id=id, messages=info[1], creator=info[0].username, creation_time=info[0].creation_time, name=info[0].name)
    else:
        return redirect("/access_denied")

@app.route("/access_denied")
def access_denied():
    return render_template("access_denied.html")

@app.route("/threads/create")
def create_thread():
    return render_template("create_thread.html")

@app.route("/threads/create/send", methods=["POST"])
def send_created_thread():
    creator_id = users.get_id(session["username"])
    threads.create_thread(creator_id, True, request.form["name"])
    thread_id = threads.get_thread_amount()
    return redirect("/threads/" + str(thread_id))