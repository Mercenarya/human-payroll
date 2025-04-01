import flask
from flask import Flask,session, request, redirect, url_for, current_app, render_template, jsonify
import mysql
from flask_sqlalchemy import SQLAlchemy
import json
import requests
import datetime
from cryptography.fernet import Fernet
from flask_session import Session
from flask_login import LoginManager, session_protected,UserMixin,login_required,logout_user,current_user
import re

# tạo khóa cho bộ mã hóa 
key = Fernet.generate_key()
app = flask.Flask(__name__)
app.secret_key = "thesupevisorofthebois"
key_handler = Fernet(key)

# Khởi tạo các tiện ích hỗ trợ đăng nhập
login_mng = LoginManager()
login_mng.init_app(app=app)


class User(UserMixin):
    def __init__(self,name,email,role):
        self.name = name
        self.email = email
        self.role = role
    

# kiểm tra người dùng đăng nhập 
@login_mng.user_loader
def user_loader(user_id):
    user = User()
    return user


# danh sách tài khoản tạm thời (admin, supervisor và moderator)
accounts = [
    {'name':'admin','password':'admin123','email':'admin@example.com','role':'administrator'},
    {'name':'supervisor','password':'supervisor123','email':'supervisor@example.com','role':'supervisor'},
    {'name':'moderator','password':'moderator_123','email':'moderator@example.com','role':'moderator'},
]

# thông tin nhân viên (HR - Human)
hr_staff = [
    {
        'EmployeeID': 1001,
        'FirstName': 'Alice',
        'LastName': 'Smith',
        'DepartmentID': 1,
        'JobID': 1,
        'Salary': 60000,
        'HireDate': '2017-20-10',
        'Status': 'Active'
    },
    {
        'EmployeeID': 1002,
        'FirstName': 'Bob',
        'LastName': 'Johnson',
        'DepartmentID': 1,
        'JobID': 2,
        'Salary': 50000,
        'HireDate': '2017-20-10',
        'Status': 'Active'
    },
    {
        'EmployeeID': 1003,
        'FirstName': 'Charlie',
        'LastName': 'Brown',
        'DepartmentID': 1,
        'JobID': 3,
        'Salary': 45000,
        'HireDate': '2017-20-10',
        'Status': 'Inactive'
    }
]

pr_staff = [
    
]


# kiểm tra status của từng endpoint
def check_status(obj):
    status_range = []
    url = f'http://127.0.0.1:5000/{obj}'
    response=requests.get(url=url)
    current_time = datetime.datetime.now()
    status_enpoints = {
        'status':response.status_code,
        'url':url,
        'time':current_time
    }
    # thêm vào danh sách enpoints 
    status_range.append(status_enpoints)

    return {
        'status':response.status_code,
        'url':url,
        'time':current_time
    }


# Home page
@login_required
@app.route('/')
def home():
    # check_status('/')
    return render_template('home.html')

# trang đăng nhập
@app.route('/login', methods = ['GET','POST'])
def login():
    message = ""
    if request.method == "POST":
        username = request.form.get('username')
        password = request.form.get('password')
        email = request.form.get('email')
        if username == accounts[0]['name'] and password == accounts[0]['password'] and email == accounts[0]['email']:
            message = "Sign in Successfully"
            User(
                name=accounts[0]["name"],
                email=accounts[0]["email"],
                role=accounts[0]["role"]
            )
            session['username'] = accounts[0]['name']
            session['email'] = accounts[0]['email']
            session['role'] = accounts[0]['role']
            return redirect(url_for('home'))
        
        
    return render_template('login.html',msg = message)

# trang đăng kí tài khoản người dùng và phân quyền
@app.route('/register', methods = ['GET','POST'])
def register():
    message = ''
    emailform = ['@gmail.com']
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        rppassword = request.form.get('rp-password')
        email = request.form.get('email')
        phone = request.form.get('phonenumber')
        # kiểm tra yêu cầu @gmail.com cần thêm vào dữ liệu đầu vào
        matches = re.search('@gmail.com',email)
        
        # kiểm tra mức độ của dữ liệu đầu vào
        if username in accounts[0]['name']:
            message = 'This name is already taken'
        if password != rppassword:
            message = 'Password does not matched'
        if email not in emailform:
            message = 'Email is invalid'
        if email in accounts[0]['email']:
            message = 'This email account is already taken'
        if not matches or matches == None:
            message = "Invalid email account"
        if not phone:
            message = "Phone is required"
        else:
            accounts.append(
                {
                    "name":username,
                    "password":password,
                    "email":email
                }
            )
            return redirect(url_for('login'))


    return render_template('register.html',msg = message)

@login_required
@app.route('/management',methods=['POST','GET'])
def management():
    if request.method == 'POST':
        pass
    return render_template('management.html')


# hiển thị danh sách
@login_required
@app.route('/dashboard', methods = ['GET','POST'])
def dashboard():
    try:
        return render_template('dashboard.html',human = hr_staff)
    except Exception as error:
        return error



# Đăng xuất tài khoản
@app.route('/logout',methods = ['GET','POST'])
def logout():
    try:
        session.clear()
        logout_user()
        return redirect(url_for('login'))
    except Exception as error:
        return f'Error - {error}'


# chuyển về status 404 - không tìm thấy endpoint cần đến
@app.errorhandler(404)
def notfound(error):
    if request.headers.get(404):
        return '<h1>404 - NOT FOUND</h1>', 404




if __name__ == "__main__":
    app.run(debug=True)