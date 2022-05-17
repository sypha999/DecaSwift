from cs50 import SQL
from flask import Flask, flash, redirect, render_template, request, session
from flask_session import Session
from tempfile import mkdtemp
#from flask.ext.session import Session
from werkzeug.security import check_password_hash, generate_password_hash

from helpers import error_page,login_required,get_count,admin_required

# Configure application
app = Flask(__name__)

# Ensure templates are auto-reloaded
app.config["TEMPLATES_AUTO_RELOAD"] = True


# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Configure CS50 Library to use SQLite database
db = SQL("sqlite:///decaswift.db")

@app.route('/set/')
def set():
    session['key'] = 'value'
    return 'ok'

@app.route('/get/')
def get():
    return session.get('key', 'not set')


@app.after_request
def after_request(response):
    """Ensure responses aren't cached"""
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response

@app.route("/")
def index():
    return render_template("/home.html")

@app.route("/home", methods=["GET"])
def homd():
    return render_template("/home.html")


@app.route("/about", methods=["GET"])
def about():
    return render_template("/about.html")



@app.route("/admin", methods=["GET", "POST"])
@admin_required
def admin():

    all_users=db.execute("SELECT * FROM users ORDER BY name")
    all_users2=db.execute("SELECT * FROM users")
    count_users=get_count["all_users"][0]["COUNT(id)"]
    count_engineers=get_count["all_engineers"][0]["COUNT(id)"]
    count_companies=get_count["all_companies"][0]["COUNT(id)"]
    count_engaged=get_count["all_engaged"][0]["COUNT(user_id)"]
    count_unengaged=get_count["all_unengaged"][0]["COUNT(user_id)"]
    all_engineers=db.execute("SELECT * FROM engineers")
    all_companies=db.execute("SELECT * FROM companies")
    
    arr=[]
    arr2=[]
    arr3=[]
    for i in range(count_users):
        arr.append(i+1)
        arr.append(all_users[i]['name'])
        arr.append(all_users[i]['type'])
        if all_users[i]['type']=="company":
            arr.append(db.execute('SELECT status FROM companies WHERE user_id=?',all_users[i]['id'])[0]['status'])
            arr.append('Unapplicable')
        if all_users[i]['type']=="engineer":
            arr.append(db.execute('SELECT status FROM engineers WHERE user_id=?',all_users[i]['id'])[0]['status'])
            arr.append(db.execute('SELECT emp_status FROM engineers WHERE user_id=?',all_users[i]['id'])[0]['emp_status'])

    for i in range(1,len(arr)+1):
        arr2.append(arr[i-1])
        if i%5==0:
            arr3.append(arr2)
            arr2=[]



    
    if request.method == "POST":
        sniff_status=request.form.get("nrm_stat")
        sniff_emp=request.form.get("emp_stat")
        sniff_id=request.form.get("id")
        sniff_id2=request.form.get("id2")
      
        if sniff_emp:
            db.execute("UPDATE engineers SET emp_status = ? WHERE user_id=?",sniff_emp,sniff_id2)
        if sniff_status:
            check=db.execute("SELECT type FROM users WHERE id=?",sniff_id)[0]["type"]
            if check=="engineer":
                db.execute("UPDATE engineers SET status = ? WHERE user_id=?",sniff_status,sniff_id)
            if check=="company":
                db.execute("UPDATE companies SET status = ? WHERE user_id=?",sniff_status,sniff_id)
         
        return redirect("/admin")
        

     
    return render_template("/admin.html",users=count_users,engineers=count_engineers,companies=count_companies,engaged=count_engaged,unengaged=count_unengaged,all_users=all_users,all_engineers=all_engineers,all_companies=all_companies,all_users2=all_users2,arr_final=arr3)


#done
@app.route("/login", methods=["GET", "POST"])
def login():

    # Forget any user_id
    session.clear()

    sniff_name=request.form.get("username")
    sniff_password=request.form.get("password")
    

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        # Ensure username was submitted
        if not sniff_name:
            return error_page("must provide username", 403)

        # Ensure password was submitted
        elif not sniff_password:
            return error_page("must provide password", 403)

        # Query database for username
        rows = db.execute("SELECT * FROM users WHERE username = ?", sniff_name)

        admin_rows = db.execute("SELECT * FROM admin WHERE username = ?",sniff_name)
        print(rows)
        print(admin_rows)
        if admin_rows:

            if admin_rows[0]["username"]=="admin":
        
                if len(admin_rows)!=1 or (sniff_password!=admin_rows[0]["password"]):
                    return error_page("Invalid username and or password", 403)

            # Remember which user has logged in
                else:
                    session["name"] = admin_rows[0]["username"]
                    return redirect("/admin")
        elif rows:
            if rows[0]["type"]=="company" or rows[0]["type"]=="engineer":

                if (len(rows) != 1 or not check_password_hash(rows[0]["password"], sniff_password)):
                    return error_page("Invalid username and or password", 403)
        
            
                else:
                    if rows[0]["type"]=="engineer":
                        session["name"] = rows[0]["type"]
                        session["id"]= rows[0]["id"]
                        return redirect("/engrprofile")
                    
                    if rows[0]["type"]=="company":
                        session["name"] = rows[0]["type"]
                        session["id"]= rows[0]["id"]
                        return redirect("/compprofile")
        else:
            return error_page("No such user exist, please try registering",400)
        
     
    else:
        return render_template("login.html")



#done
@app.route("/logout")
def logout():
    
    session.clear()

    return redirect("/")

@app.route("/contact", methods=["GET", "POST"])
def contact():
    if request.method == "POST":
        sniff_name=request.form.get("name")
        sniff_email=request.form.get("email")
        sniff_comment=request.form.get("comment")

        if sniff_name:
            if sniff_email:
                if sniff_comment:
                    db.execute("INSERT INTO contact (name,email,comment) VALUES(?,?,?)",sniff_name,sniff_email,sniff_comment)
                    return redirect("/")


        
        else:
            return error_page("Please fill all fields",400)

    else:
        return render_template("/contact.html")


@app.route("/reg", methods=["GET", "POST"])
def com_reg():
    if request.method=="POST":
         sniff_name=request.form.get("name")
         sniff_password=request.form.get("password")
         sniff_confirmation=request.form.get("confirmation")
         sniff_email=request.form.get("email")
         sniff_type=request.form.get("type")

         check = db.execute("SELECT id FROM users WHERE username=?",sniff_email)

       
         if len(check)>0:
            return error_page("Email already exist",400)

         if sniff_password != sniff_confirmation:
            return error_page("Passwords do not match",400)

         db.execute("INSERT INTO users (username, password,type,name) VALUES(?,?,?,?)", sniff_email, generate_password_hash(sniff_password),sniff_type,sniff_name)

         if sniff_type=="company":
             session["name"] = sniff_type
             db.execute("INSERT INTO companies (user_id) SELECT id FROM users WHERE username = ?",sniff_email)
             return redirect("/compupdate")
         
         elif sniff_type=="engineer":
             session["name"] = sniff_type
             db.execute("INSERT INTO engineers (user_id) SELECT id FROM users WHERE username = ?",sniff_email)
             return redirect("/engrupdate")

    else:
        return render_template("reg.html")
    

@app.route("/hire", methods=["GET", "POST"])
@login_required
def hire():
    user_id=session.get("id")

    if request.method == "POST":
        name=db.execute("SELECT name FROM users WHERE id=?",user_id)[0]["name"]
        sniff_number=request.form.get("number")
        sniff_criteria=request.form.get("criteria")
        sniff_date=request.form.get("date")
        sniff_stack=request.form.get("stack")

        #print(sniff_criteria,  sniff_date,  sniff_number,  sniff_stack,  name)

        db.execute("INSERT INTO request (stack,criteria,deadline,quantity,company) VALUES(?,?,?,?,?)",sniff_stack,sniff_criteria,sniff_date,sniff_number,name)
        
        return redirect("/compprofile")

    else:
        return render_template("/hire.html")




@app.route("/engrprofile", methods=["GET"])
@login_required
def engr_prof():

    user_id=session.get("id")     
    old_date=db.execute("SELECT dob FROM engineers WHERE user_id=?",user_id)[0]["dob"]
    old_email=db.execute("SELECT email FROM engineers WHERE user_id=?",user_id)[0]["email"]
    old_stack=db.execute("SELECT stack FROM engineers WHERE user_id=?",user_id)[0]["stack"]
    old_gitlink=db.execute("SELECT git_link FROM engineers WHERE user_id=?",user_id)[0]["git_link"]
    old_phone=db.execute("SELECT phone FROM engineers WHERE user_id=?",user_id)[0]["phone"]
    old_desc=db.execute("SELECT description FROM engineers WHERE user_id=?",user_id)[0]["description"]
    name=db.execute("SELECT name FROM users WHERE id=?",user_id)[0]["name"]
    
    return render_template("engrprofile.html",old_date=old_date,old_email=old_email,old_stack=old_stack,old_gitlink=old_gitlink,old_phone=old_phone,old_desc=old_desc,name=name)

    
    

@app.route("/compprofile", methods=["GET"])
@login_required
def com_prof():
    user_id=session.get("id")
    

    old_desc=db.execute("SELECT description FROM companies WHERE user_id=?",user_id)[0]["description"]
    old_email=db.execute("SELECT email FROM companies WHERE user_id=?",user_id)[0]["email"]
    old_website=db.execute("SELECT website FROM companies WHERE user_id=?",user_id)[0]["website"]
    old_address=db.execute("SELECT address FROM companies WHERE user_id=?",user_id)[0]["address"]
    old_phone=db.execute("SELECT phone FROM companies WHERE user_id=?",user_id)[0]["phone"]
    name=db.execute("SELECT name FROM users WHERE id=?",user_id)[0]["name"]
   
    return render_template("compprofile.html",old_email=old_email,old_website=old_website,old_address=old_address,old_phone=old_phone,old_desc=old_desc,name=name)
    
    
    
@app.route("/compupdate", methods=["GET", "POST"])
@login_required
def compupdate():

    user_id=session.get("id")
    print(user_id)
    old_desc=db.execute("SELECT description FROM companies WHERE user_id=?",user_id)[0]["description"]
    old_email=db.execute("SELECT email FROM companies WHERE user_id=?",user_id)[0]["email"]
    old_website=db.execute("SELECT website FROM companies WHERE user_id=?",user_id)[0]["website"]
    old_address=db.execute("SELECT address FROM companies WHERE user_id=?",user_id)[0]["address"]
    old_phone=db.execute("SELECT phone FROM companies WHERE user_id=?",user_id)[0]["phone"]
    sniff_phone=request.form.get("phone")
    sniff_address=request.form.get("address")
    sniff_email=request.form.get("email")
    sniff_desc=request.form.get("description")
    sniff_website=request.form.get("website")

    if request.method == "POST":
        
        #photo_type=secure_filename(sniff_photo.filename)
        if sniff_phone:
            db.execute("UPDATE companies SET phone = ? WHERE user_id=?",sniff_phone,user_id)

        if sniff_email:
            db.execute("UPDATE companies SET email = ? WHERE user_id=?",sniff_email,user_id)
        
        if sniff_desc:
            db.execute("UPDATE companies SET description = ? WHERE user_id=?",sniff_desc,user_id)
        
        if sniff_address:
            db.execute("UPDATE companies SET address = ? WHERE user_id=?",sniff_address,user_id)
        
        if sniff_website:
            db.execute("UPDATE companies SET website = ? WHERE user_id=?",sniff_website,user_id)


        return redirect("/compprofile")
    
    else:
        return render_template("compupdate.html",old_email=old_email,old_website=old_website,old_address=old_address,old_phone=old_phone,old_desc=old_desc)


@app.route("/engrupdate", methods=["GET", "POST"])
@login_required
def engrupdate():
    user_id=session.get("id")
    sniff_photo=request.form.get("photo")
    sniff_date=request.form.get("date")
    sniff_email=request.form.get("email")
    sniff_stack=request.form.get("stack")
    sniff_gitlink=request.form.get("gitlink")
    sniff_phone=request.form.get("phone")
    sniff_description=request.form.get("description")

    old_date=db.execute("SELECT dob FROM engineers WHERE user_id=?",user_id)[0]["dob"]
    old_email=db.execute("SELECT email FROM engineers WHERE user_id=?",user_id)[0]["email"]
    old_stack=db.execute("SELECT stack FROM engineers WHERE user_id=?",user_id)[0]["stack"]
    old_gitlink=db.execute("SELECT git_link FROM engineers WHERE user_id=?",user_id)[0]["git_link"]
    old_phone=db.execute("SELECT phone FROM engineers WHERE user_id=?",user_id)[0]["phone"]
    old_desc=db.execute("SELECT description FROM engineers WHERE user_id=?",user_id)[0]["description"]

    if request.method == "POST":
        
        #photo_type=secure_filename(sniff_photo.filename)
        if sniff_photo:
            db.execute("UPDATE engineers SET passport = ? WHERE user_id=?",sniff_photo,user_id)

        if sniff_date:
            db.execute("UPDATE engineers SET dob = ? WHERE user_id=?",sniff_date,user_id)
        
        if sniff_email:
            db.execute("UPDATE engineers SET email = ? WHERE user_id=?",sniff_email,user_id)
        
        if sniff_stack:
            db.execute("UPDATE engineers SET stack = ? WHERE user_id=?",sniff_stack,user_id)
        
        if sniff_gitlink:
            db.execute("UPDATE engineers SET git_link = ? WHERE user_id=?",sniff_gitlink,user_id)
        
        if sniff_phone:
            db.execute("UPDATE engineers SET phone = ? WHERE user_id=?",sniff_phone,user_id)

        if sniff_description:
            db.execute("UPDATE engineers SET description = ? WHERE user_id=?",sniff_description,user_id)

        return redirect("/engrprofile")

    else:
        return render_template("engrupdate.html",old_date=old_date,old_email=old_email,old_stack=old_stack,old_gitlink=old_gitlink,old_phone=old_phone,old_desc=old_desc)