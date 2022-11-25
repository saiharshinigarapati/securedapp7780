from flask import Flask,send_file,make_response,render_template,flash, redirect,url_for,session,logging,request
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash,check_password_hash
import os
import sqlite3
import uuid
from werkzeug.utils import secure_filename
from datetime import datetime
import sha256


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:////Users/bozkurt/Desktop/login-register-form/database.db'
db = SQLAlchemy(app)


# class user(db.Model):
#     id = db.Column(db.Integer, primary_key=True)
#     username = db.Column(db.String(80))
#     email = db.Column(db.String(120))
#     password = db.Column(db.String(80))

# class groups(db.Model):
#     id = db.Column(db.Integer, primary_key=True)
#     group_id = db.Column(db.Integer)
#     user_id = db.Column(db.Integer)

# class friends(db.Model):
#     id = db.Column(db.Integer, primary_key=True)
#     request_sent = db.Column(db.String(80))
#     request_accepted = db.Column(db.Boolean())
#     password = db.Column(db.String(80))

app.config['SECRET_KEY']='004f2af45d3a4e161a7dd2d17fdae47f'
app.config['SQLALCHEMY_DATABASE_URI']='sqlite:///user.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True


# This Code will conect and create the table in the database
def connect():
    conn = sqlite3.connect('user.db')
    cur = conn.cursor()
    cur.execute("CREATE TABLE IF NOT EXISTS user (id VARCHAR(255) PRIMARY KEY,username Text, name TEXT,password Text,activate Boolean)")
    cur.execute("CREATE TABLE IF NOT EXISTS groups (id VARCHAR(255) PRIMARY KEY, name TEXT)")
    cur.execute("CREATE TABLE IF NOT EXISTS shared_groups (id VARCHAR(255) PRIMARY KEY,group_id VARCHAR(255), user_id,FOREIGN KEY (id) REFERENCES groups (id))")
    cur.execute("CREATE TABLE IF NOT EXISTS user_groups (user_id VARCHAR(255), allow Boolean)")
    cur.execute("CREATE TABLE IF NOT EXISTS admin (id VARCHAR(255) PRIMARY KEY,name VARCHAR(255),username VARCHAR(20),password VARCHAR(255))")
    cur.execute("CREATE TABLE IF NOT EXISTS friend_files (id VARCHAR(255) PRIMARY KEY,file_path VARCHAR(255),uploaded_by VARCHAR(255),uploaded_to VARCHAR(255))")
    conn.commit()
    conn.close()

if os.path.isfile('user.db')==False:
    print('hello')
    connect()

@app.route("/")
def index():
    return render_template("index.html")

@app.route('/download_file/<string:file_id>')
def download_file(file_id):
    conn = sqlite3.connect('user.db')
    cur = conn.cursor()
    query = f"select * from friend_files where id='{file_id}'"
    cur.execute(query)
    rows = cur.fetchone()
    print(rows)
    conn.commit()
    conn.close()
    return send_file(rows[1],as_attachment=True)

@app.route('/download_group_file/<string:id>')
def download_group_file(id):
    conn = sqlite3.connect('user.db')
    cur = conn.cursor()
    query = f"select * from shared_groups where id='{id}'"
    cur.execute(query)
    rows = cur.fetchone()
    print(rows)
    conn.commit()
    conn.close()
    return send_file(rows[3],as_attachment=True)

@app.route("/user_request/<string:user_id>")
def user_request(user_id):
    if user_id:
        pass
    else:
        conn = sqlite3.connect('user.db')
        cur = conn.cursor()
        query = f"select * from user  where activate=0"
        cur.execute(query)
        rows = cur.fetchall()
        conn.commit()
        conn.close()
    return render_template("users_request.html",records = rows)

@app.route("/delete_file/<string:file_id>")
def delete_file(file_id):
    conn = sqlite3.connect('user.db')
    cur = conn.cursor()
    query = f"delete from friend_files  where id='{file_id}'"
    cur.execute(query)
    
    userID = request.cookies.get('userID')
    cur = conn.cursor()
    query = f"select * from friend_files where uploaded_by='{userID}'"
    cur.execute(query)
    rows = cur.fetchall()
    conn.commit()
    conn.close()
    return render_template("myfiles.html",records = rows)

@app.route("/update/",methods=["POST","GET"])
def update():

    if request.method == "POST":
        userID = request.cookies.get('userID')
        file_id = request.form["file_id"]
        file = request.files['file']
        random_name = str(uuid.uuid4())
        file.filename = random_name + '.' + str(file.filename).split('.')[-1]
        # file.filename = "abc."  #some custom file name that you want
        file.save("Uploads/"+file.filename)     
        conn = sqlite3.connect('user.db')
        cur = conn.cursor()
        path = os.getcwd()+'/Uploads/'+file.filename
        conn = sqlite3.connect('user.db')
        cur = conn.cursor()
        query = f"update friend_files set file_path='{path}'  where id='{file_id}'"
        cur.execute(query)
        query = f"select * from friend_files where uploaded_by='{userID}'"
        cur.execute(query)
        rows = cur.fetchall()
        print(rows)

        conn.commit()
        conn.close()
        return render_template("myfiles.html",records = rows)


@app.route("/update_file/<string:file_id>")
def update_file(file_id):

    return render_template("update_send_file.html",file_id=file_id)


@app.route("/my_files/<string:flow>")
def my_files(flow):
    if flow=="sent":

        userID = request.cookies.get('userID')
        conn = sqlite3.connect('user.db')
        cur = conn.cursor()
        query = f"select * from friend_files where uploaded_by='{userID}'"
        cur.execute(query)
        rows = cur.fetchall()
        print(rows)
        conn.commit()
        conn.close()
        return render_template("myfiles.html",records = rows)
    else:
        userID = request.cookies.get('userID')
        conn = sqlite3.connect('user.db')
        cur = conn.cursor()
        print(userID)
        query = f"select * from friend_files where uploaded_to='{userID}'"
        cur.execute(query)
        rows = cur.fetchall()
        print(rows)
        conn.commit()
        conn.close()
        return render_template("received_file.html",records = rows)

@app.route("/send_friends_files",methods=["GET", "POST"])
def send_friends_files():

    if request.method == "POST":
        friend_id = request.form["friend_id"]
        file = request.files['file']
        random_name = str(uuid.uuid4())
        userID = request.cookies.get('userID')
        file.filename = random_name + '.' + str(file.filename).split('.')[-1]
        file.save("Uploads/"+file.filename)     
        conn = sqlite3.connect('user.db')
        cur = conn.cursor()
        path = os.getcwd()+'/Uploads/'+file.filename
        cur.execute("INSERT INTO friend_files VALUES (?,?,?,?)", (
        random_name,
        path,
        userID,
        friend_id
        ))
        conn.commit()
        conn.close()
        return redirect(url_for("dashboard"))
    return render_template("send_file.html",friend_id=user_id)


@app.route("/send_files/<string:user_id>")
def send_files(user_id):
    if request.method == "POST":
        friend_id = request.form["friend_id"]
        file = request.files['file1']
        
        print('///////////////',file.filename)
        return redirect(url_for("dashboard"))
    return render_template("send_file.html",friend_id=user_id)



@app.route("/add_friends/<string:user_id>")
def add_friends(user_id):
    conn = sqlite3.connect('user.db')
    cur = conn.cursor()

    cur.execute("INSERT INTO friend VALUES (?,?,?,?)", (
    str(uuid.uuid4()),
    request.cookies.get('userID'),
    user_id,
    True
    ))
    conn.commit()
    conn.close()
    return render_template("dashboard.html")


@app.route("/view_group_files/<string:group_id>")
def view_group_files(group_id):
    userID = request.cookies.get('userID')
    conn = sqlite3.connect('user.db')
    cur = conn.cursor()
    query = f"select * from shared_groups where group_id='{group_id}'"
    cur.execute(query)
    rows = cur.fetchall()
    print(rows)
    conn.commit()
    conn.close()
    return render_template("view_group_files.html",records = rows)


@app.route("/send_files_to_group/<string:group_id>",methods=["POST","GET"])
def send_files_to_group(group_id):
    if request.method == 'POST':
        name = request.form["name"]
        description = request.form["description"]
        now = datetime.now()
        current_time = now.strftime("%d/%m/%Y %H:%M:%S")
        userID = request.cookies.get('userID')
        file = request.files['file']
        random_name = str(uuid.uuid4())
        file.filename = random_name + '.' + str(file.filename).split('.')[-1]
        file.save("Uploads/"+file.filename)     
        conn = sqlite3.connect('user.db')
        cur = conn.cursor()
        path = os.getcwd()+'/Uploads/'+file.filename
        cur.execute("INSERT INTO shared_groups VALUES (?,?,?,?,?,?,?)",(
        str(uuid.uuid4()),
        group_id,
        userID,
        path,
        name,
        description,
        current_time
        ))
        conn.commit()
        conn.close()
        return redirect(url_for("dashboard"))
    return render_template("send_files_to_group.html",group_id=group_id)

@app.route("/dashboard")
def dashboard():
    userID = request.cookies.get('userID')
    query= f"select * from user where id !='{userID}' and activate=1"
    conn = sqlite3.connect('user.db')
    cur = conn.cursor()
    cur.execute(query)
    rows1 = cur.fetchall()
    query= f"select * from user_groups where user_id='{userID}'"
    cur.execute(query)
    rows2 = cur.fetchall()
    if len(rows2)>0:
        query= f"select * from groups"
        cur.execute(query)
        rows2 = cur.fetchall()
    data = {}
    data['rows1'] = rows1
    data['rows2'] = rows2
    conn.commit()
    conn.close()
    return render_template("dashboard.html",users=data)

@app.route("/delete_user/<string:user_id>")
def delete_user(user_id):
    conn = sqlite3.connect('user.db')
    cur = conn.cursor()
    query = f"delete from user  where id='{user_id}'"
    cur.execute(query)
    conn.commit()
    conn.close()
    return redirect(url_for("admin_dashboard"))

@app.route("/ativate_user/<string:user_id>")
def ativate_user(user_id):
    conn = sqlite3.connect('user.db')
    cur = conn.cursor()
    query = f"update user set activate=1  where id='{user_id}'"
    cur.execute(query)
    conn.commit()
    conn.close()
    return redirect(url_for("admin_dashboard"))
    # return render_template("dashboard.html",file_id=file_id)

@app.route("/allow_group_user/<string:user_id>")
def allow_group_user(user_id):
    query = f"insert into user_groups values(?,?)"
    conn = sqlite3.connect('user.db')
    cur = conn.cursor()
    cur.execute(query,(user_id,True))
    # rows = cur.fetchall()
    conn.commit()
    conn.close()
    return redirect(url_for('admin_dashboard'))

@app.route("/list_group_user")
def list_group_user():

    query= f"select user_id from user_groups"
    conn = sqlite3.connect('user.db')
    cur = conn.cursor()
    cur.execute(query)
    row1 = cur.fetchall()
    print(row1)
    query= f"select * from user"
    conn = sqlite3.connect('user.db')
    cur = conn.cursor()
    cur.execute(query)
    rows = cur.fetchall()
    print(rows)
    records = []
    visited = []
    if len(row1)<1:
        records = rows
    for i in rows:
        for j in row1:
            if i[0]==j[0]:
                pass
            else:
                if j[0] not in visited:
                    visited.append(j)
                    records.append(i)
    print(records)
    conn.commit()
    conn.close()
    return render_template('list_group_user.html',records=records)

@app.route("/all_groups")
def all_groups():

    query= f"select * from groups"
    conn = sqlite3.connect('user.db')
    cur = conn.cursor()
    cur.execute(query)
    rows = cur.fetchall()
    conn.commit()
    conn.close()
    return render_template('all_groups.html',records=rows)

@app.route("/add_new_user_group",methods=["GET", "POST"])
def add_new_user_group():
    if request.method == "POST":
        group_name = request.form["group_name"]
        # is_admin = request.form["is_admin"]
        
        query= f"insert into groups values(?,?)"
        conn = sqlite3.connect('user.db')
        cur = conn.cursor()
        cur.execute(query,(
            str(uuid.uuid4()),
            group_name))
        conn.commit()
        conn.close()

        return redirect(url_for('admin_dashboard'))
    return render_template('add_new_user_group.html')

@app.route("/add_new_group",methods=["GET", "POST"])
def add_new_group():
    if request.method == "POST":
        group_name = request.form["group_name"]
        # is_admin = request.form["is_admin"]
        
        query= f"insert into groups values(?,?)"
        conn = sqlite3.connect('user.db')
        cur = conn.cursor()
        cur.execute(query,(
            str(uuid.uuid4()),
            group_name))
        conn.commit()
        conn.close()

        return redirect(url_for('admin_dashboard'))
    return render_template('add_group.html')

@app.route("/admin_dashboard")
def admin_dashboard():
    userID = request.cookies.get('userID')
    query= f"select * from user where activate=0"
    conn = sqlite3.connect('user.db')
    cur = conn.cursor()
    cur.execute(query)
    rows = cur.fetchall()
    conn.commit()
    conn.close()
    return render_template("admin_dashboard.html",users=rows)



@app.route("/admin_login",methods=["GET", "POST"])
def admin_login():
    if request.method == "POST":
        uname = request.form["uname"]
        passw = request.form["passw"]
        query= f"select * from admin where username='{uname}'"
        conn = sqlite3.connect('user.db')
        cur = conn.cursor()
        cur.execute(query)
        row = cur.fetchall()
        conn.commit()
        conn.close()
        print("hello")
        if row and check_password_hash(row[0][3],passw):
            print('Login Successfully')
        # login = user.query.filter_by(username=uname, password=passw).first()
        # if login is not None:
            resp = redirect(url_for("admin_dashboard"))
            resp.set_cookie('adminID', row[0][0])
            return resp
    return render_template("admin_login.html")


@app.route("/admin_register", methods=["GET", "POST"])
def admin_register():
    if request.method == "POST":
        uname = request.form['uname']
        name = request.form['name']
        passw = request.form['passw']

        hashed_password = generate_password_hash(passw, method='sha256')

        conn = sqlite3.connect('user.db')
        cur = conn.cursor()
        cur.execute("INSERT INTO admin VALUES (?,?,?,?)", (
        str(uuid.uuid4()),
        uname,
        name,
        hashed_password
        ))
        conn.commit()
        conn.close()
        # register = user(username = uname, email = mail, password = passw)
        # db.session.add(register)
        # db.session.commit()

        return redirect(url_for("admin_login"))
    return render_template("admin_register.html")

@app.route("/login",methods=["GET", "POST"])
def login():
    if request.method == "POST":
        uname = request.form["uname"]
        passw = request.form["passw"]
        
        query= f"select * from user where username='{uname}' and activate=1"
        conn = sqlite3.connect('user.db')
        cur = conn.cursor()
        cur.execute(query)
        row = cur.fetchone()
        
        conn.commit()
        conn.close()
        print(row)
        s=passw.encode('utf-8')
        hashed_password = sha256.Sha256(s).hexdigest()
        if row:
            if row[3]==hashed_password:
                print('Login Successfully')
        # login = user.query.filter_by(username=uname, password=passw).first()
        # if login is not None:
            resp = redirect(url_for("dashboard"))
            resp.set_cookie('userID', row[0])
            return resp
    return render_template("login.html")



@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        uname = request.form['uname']
        name = request.form['name']
        passw = request.form['passw']
        s=passw.encode('utf-8')
        hashed_password = sha256.Sha256(s).hexdigest()

        conn = sqlite3.connect('user.db')
        cur = conn.cursor()
        cur.execute("INSERT INTO user VALUES (?,?,?,?,?)", (
        str(uuid.uuid4()),
        uname,
        name,
        hashed_password,
        False
        ))
        conn.commit()
        conn.close()
        # register = user(username = uname, email = mail, password = passw)
        # db.session.add(register)
        # db.session.commit()

        return redirect(url_for("login"))
    return render_template("register.html")

if __name__ == "__main__":
    # db.create_all()
    app.run(debug=True)