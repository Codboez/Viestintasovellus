from app import app
from flask import redirect, render_template, request, session
import users
import threads

@app.route("/")
def index():
    thread_list = threads.get_all_public_threads()
    friends = []
    friend_requests = []
    if "username" in session:
        friends = users.get_friends(users.get_id(session["username"]))
        friend_requests = users.get_friend_requests(users.get_id(session["username"]))

    tab = request.args.get("tab")
    friend_request_message = request.args.get("friend_request")
    
    return render_template("index.html", threads=thread_list, friends=friends, tab=tab, requests=friend_requests, friend_request=friend_request_message)

@app.route("/register", methods=["GET", "POST"])
def register():
    return render_template("register.html")

@app.route("/login", methods=["GET", "POST"])
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
    if "username" not in session:
        return redirect("/access_denied")

    creator_id = users.get_id(session["username"])
    threads.create_thread(creator_id, True, request.form["name"])
    thread_id = threads.get_thread_amount()
    return redirect("/threads/" + str(thread_id))

@app.route("/threads/<int:id>/send_message", methods=["POST"])
def threads_send_message(id: int):
    sender_id = users.get_id(session["username"])
    message = request.form["message"]

    if threads.user_has_access(sender_id):
        threads.send_message(id, sender_id, message)
        return redirect("/threads/" + str(id))
    else:
        return redirect("/access_denied")

@app.route("/send_friend_request", methods=["POST"])
def send_friend_request():
    sender_name = session["username"]
    recipient_name = request.form["username"]
    sender_id = users.get_id(sender_name)
    recipient_id = users.get_id(recipient_name)

    if sender_name == recipient_name:
        return redirect("/", friend_request="self")

    if not users.username_exists(recipient_name):
        return redirect("/", friend_request="invalid_username")

    if users.has_friend(sender_id, recipient_id):
        return redirect("/", friend_request="friend_exists")

    if users.friend_request_exists(sender_id, recipient_id):
        return redirect("/", friend_request="friend_request_exists")

    users.send_friend_request(sender_id, recipient_id)
    return redirect("/", friend_request="sent")

@app.route("/send_friend_request_answer", methods=["POST"])
def send_friend_request_answer():
    answer = request.form["request_answer"]
    user_id = users.get_id(session["username"])
    friend_id = request.form["friend_id"]

    if answer == "accept":
        users.add_friend(user_id, friend_id)
    elif answer == "decline":
        pass