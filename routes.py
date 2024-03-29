from app import app
from flask import redirect, render_template, request, session, url_for, abort
import users
import threads
import secrets

@app.route("/", methods=["GET", "POST"])
def index():
    sort_arg = request.args.get("sort")
    order_arg = request.args.get("order")

    if sort_arg == None:
        sort_arg = "creation_time"
    
    if order_arg == None:
        order_arg = "ASC"

    sort = (sort_arg, order_arg)

    try:
        thread_list = threads.get_all_public_threads(sort)
    except ValueError:
        abort(403)

    arguments = users.setup_sidebar_arguments(request.args)
    
    return render_template("index.html", threads=thread_list, arguments=arguments, sort=sort, current="/")

@app.route("/register", methods=["GET", "POST"])
def register():
    return render_template("register.html", error=request.args.get("error"))

@app.route("/login", methods=["GET", "POST"])
def login():
    return render_template("login.html", error=request.args.get("error"))

@app.route("/register/send", methods=["POST"])
def send_register():
    register_complete = users.register(request.form["username"], request.form["password"], request.form["confirm_password"])
    if register_complete[0]:
        return redirect("/")
    else:
        return redirect(url_for(".register", error=register_complete[1]))

@app.route("/login/send", methods=["POST"])
def send_login():
    username = request.form["username"]
    password = request.form["password"]

    if users.login(username, password):
        session["username"] = username
        session["csrf_token"] = secrets.token_hex(16)
        return redirect("/")
    else:
        return redirect(url_for(".login", error="invalid username or password"))

@app.route("/logout", methods=["POST"])
def logout():
    del session["username"]
    return redirect("/")

@app.route("/invalid_credentials")
def invalid_credentials():
    return render_template("invalid_credentials.html")

@app.route("/threads/<int:id>", methods=["GET", "POST"])
def thread(id: int):
    info = threads.get_thread_info(id)

    if threads.user_has_access(id, request.form.get("csrf_token"), request.method):
        arguments = users.setup_sidebar_arguments(request.args)
        return (render_template("thread.html", id=id, messages=info[1], creator=info[0].username, creation_time=info[0].creation_date, 
            name=info[0].name, arguments=arguments, current="/threads/" + str(id)))
    else:
        abort(403)

@app.route("/access_denied")
def access_denied():
    return render_template("access_denied.html")

@app.route("/threads/create", methods=["GET", "POST"])
def create_thread():
    arguments = users.setup_sidebar_arguments(request.args)
    return render_template("create_thread.html", arguments=arguments, current="/threads/create")

@app.route("/threads/create/send", methods=["POST"])
def send_created_thread():
    if "username" not in session:
        abort(403)

    name = request.form["name"]

    if len(name) > 50:
        abort(400)

    creator_id = users.get_id(session["username"])
    thread_id = threads.create_thread(creator_id, True, name)
    return redirect("/threads/" + str(thread_id), code=307)

@app.route("/threads/<int:id>/send_message", methods=["POST"])
def threads_send_message(id: int):
    sender_id = users.get_id(session["username"])
    message = request.form["message"]

    if "username" not in session:
        abort(403)

    if threads.user_has_access(id, request.form["csrf_token"], "POST"):
        threads.send_message(id, sender_id, message)
        return redirect("/threads/" + str(id))
    else:
        abort(403)

@app.route("/send_friend_request", methods=["POST"])
def send_friend_request():
    sender_name = session["username"]
    recipient_name = request.form["username"]

    if session["csrf_token"] != request.form["csrf_token"]:
        abort(403)

    if sender_name == recipient_name:
        return redirect(url_for(".index", friend_request="self"))

    if not users.username_exists(recipient_name):
        return redirect(url_for(".index", friend_request="invalid_username"))

    sender_id = users.get_id(sender_name)
    recipient_id = users.get_id(recipient_name) 

    if users.has_friend(sender_id, recipient_id):
        return redirect(url_for(".index", friend_request="friend_exists"))

    if users.friend_request_exists(sender_id, recipient_id):
        return redirect(url_for(".index", friend_request="friend_request_exists"))

    users.send_friend_request(sender_id, recipient_id)
    return redirect(url_for(".index", friend_request="sent"))

@app.route("/send_friend_request_answer", methods=["POST"])
def send_friend_request_answer():
    answer = request.form["request_answer"]
    user_id = users.get_id(session["username"])
    friend_id = request.form["friend_id"]

    if session["csrf_token"] != request.form["csrf_token"]:
        abort(403)

    if answer == "accept":
        users.add_friend(user_id, friend_id)
        users.remove_friend_request(friend_id, user_id)
    elif answer == "decline":
        users.remove_friend_request(friend_id, user_id)

    return redirect("/")

@app.route("/threads/get_private_thread", methods=["POST"])
def get_private_thread():
    user_id = users.get_id(session["username"])
    friend_id = request.form["friend_id"]
    thread_id = threads.create_and_get_private_thread(user_id, friend_id)

    if threads.user_has_access(thread_id, request.form["csrf_token"], "POST"):
        return redirect("/threads/" + str(thread_id), code=307)
    else:
        abort(403)