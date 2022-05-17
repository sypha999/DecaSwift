import os
import urllib.parse
from webbrowser import get
from cs50 import SQL

from flask import redirect, render_template, request, session
from functools import wraps

# Configure CS50 Library to use SQLite database
db = SQL("sqlite:///decaswift.db")

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get("name")==" ":
            return redirect("/login")
        return f(*args, **kwargs)
    return decorated_function

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get("name") !="admin":
            return error_page("you do not have permission to view this page",400)
        return f(*args, **kwargs)
    return decorated_function



def error_page(message,code):
    return render_template("/error.html",code=code,message=message)

get_count={
    "all_users":db.execute(" SELECT COUNT(id) FROM users"),
    "all_engineers":db.execute("SELECT COUNT(id) FROM users WHERE type=?","engineer"),
    "all_companies":db.execute("SELECT COUNT(id) FROM users WHERE type=?","company"),
    "all_engaged":db.execute("SELECT COUNT(user_id) FROM engineers WHERE ?=?","emp_status","engaged"),
    "all_unengaged":db.execute("SELECT COUNT(user_id) FROM engineers WHERE ?=?","emp_status","unengaged")
    }


