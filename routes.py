from app import app
from flask import redirect, render_template, request
import users

@app.route("/")
def index():
    return render_template("index.html")

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
        return redirect("/register")