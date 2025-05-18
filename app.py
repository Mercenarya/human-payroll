import flask
from flask import Flask,session, request, redirect, url_for, current_app, render_template, jsonify
import mysql
import json
import requests
import datetime
from functools import wraps
from cryptography.fernet import Fernet
from flask_session import Session
from flask_login import LoginManager, session_protected,UserMixin,login_required,logout_user,current_user, login_user
import re
import datetime
import time
# import config
import mysql.connector
import pyodbc
import jwt

import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.message import EmailMessage


#tạo kết nối CSDL đến SQL server thông qua pyodbc
server = 'LAPTOP-OOTVABFJ\\SQLEXPRESS'
database = 'HUMAN'
driver = '{ODBC Driver 17 for SQL Server}'

# Vì SQL Server chạy và hoạt động trên máy chính chủ nên sẽ sử dụng
#Trusted_Connection=yes thay vì dùng username và password thông thường
conn_server = pyodbc.connect(
    f'DRIVER={driver};SERVER={server};DATABASE={database};Trusted_Connection=yes;'
)
server_cursor = conn_server.cursor()



# tạo kết nối CSDL đến MYSQL thông qua connector
conn_mysql = mysql.connector.connect(
    host="localhost",
    user="root",
    password="Minh_17102004",
    database = "NEMO"
)


# tạo khóa cho bộ mã hóa 
key = Fernet.generate_key()
app = flask.Flask(__name__)
app.secret_key = "thesupevisorofthebois"
key_handler = Fernet(key)

# Khởi tạo các tiện ích hỗ trợ đăng nhập
login_mng = LoginManager()
login_mng.init_app(app=app)
SECRET_KEY = 'liulbu_polina'

class User(UserMixin):
    def __init__(self,name,email,role):
        self.id = name
        self.name = name
        self.email = email
        self.role = role

# khởi tạo 1 lớp Nhân viên để ứng dụng vào việc quản lí API
class Employee:
    def __init__(self,id,name,email,gender,phone,department,job):
        self.id = id
        self.name = name
        self.email = email
        self.gender = gender
        self.phone = phone
        self.department = department
        self.job = job
        

# kiểm tra người dùng đăng nhập 
@login_mng.user_loader
def user_loader(user_id):
    try:
        sql = '''SELECT * FROM accounts WHERE username = %s'''
        cursor = conn_mysql.cursor()
        cursor.execute(sql,[user_id])
        acc = cursor.fetchone()
        cursor.close()
        if acc:
            user = User(
                name=acc[1],
                email=acc[3],
                role =acc[4]
            )
            return user
    except Exception as error:
        return error



#Decorator - middleware
#truyền vào một tuple
def arms_decorator_cors(*role):
    # obj chính là các function - chức năng phân quyền chỉ truy cập theo từng role
    def decorate(obj):
        # giữ nguyên giá trị
        @wraps(obj)
        def wrap_obj(*args, **kwargs):
            # args xử lí các đôi số như empid của hàm
            # kwargs xử lí các keyword argument
            user_role = session.get("role")
            if user_role == "administrator" or user_role in role:
                return obj(*args, **kwargs)
            else:
                # nếu như role đăng nhập không có trong role yêu cầu
                return jsonify(
                    {
                        "Error":"Permission denied"
                    },403
                )
        return wrap_obj
    return decorate


def token_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        auth_header = request.headers.get('Authorization')

        if not auth_header:
            return jsonify({'message': 'Token is missing!'}), 403

        try:
            # Tách phần "Bearer <token>"
            token = auth_header.split(" ")[1]
            decoded_token = jwt.decode(token, SECRET_KEY, algorithms=['HS256'])
            current_user = decoded_token['user_id']
        except IndexError:
            return jsonify({'message': 'Token format is invalid!'}), 403
        except jwt.ExpiredSignatureError:
            return jsonify({'message': 'Token has expired!'}), 403
        except jwt.InvalidTokenError:
            return jsonify({'message': 'Invalid token!'}), 403

        return f(current_user, *args, **kwargs)

    return decorated_function


# Ví dụ endpoint bảo vệ
@app.route('/profile', methods=['GET'])
@token_required
def profile(current_user):
    return jsonify({'message': f'Hello, {current_user}! This is your profile.'})

# hàm chuyển đổi các dữ liệu từ dashboard sang json
@login_required
@app.route("/api/dashboard")
@arms_decorator_cors("administrator")
def json_progoluge():
    sql_server_qry = '''
            SELECT 
                Employees.EmployeeID,
                Employees.FullName,
                Employees.DateOfBirth,
                Employees.Gender,
                Employees.PhoneNumber,
                Employees.Email,
                Employees.HireDate,
                Departments.DepartmentName AS department,
                Positions.PositionName AS position,
                Employees.Status,
                Employees.CreatedAt,
                Employees.UpdatedAt

            FROM Employees
            INNER JOIN Departments ON Employees.DepartmentID = Departments.DepartmentID
            INNER JOIN Positions ON Employees.PositionID = Positions.PositionID 
        '''
    Employees = []
    server_cursor.execute(sql_server_qry)
    employees = server_cursor.fetchall()
    for obj in employees:

        Employees.append( {
            "Employee-ID": obj[0],
            "Name":obj[1],
            "Hire-Date":obj[6],
            "Department":obj[7],
            "Position":obj[8]
        })
        
    return jsonify(Employees)


# Home page
@login_required
@app.route('/')
def home():
    today = datetime.datetime.today()
    max_leave_day = 0
    largest_indexs = 0
    largest_indexes_emp = ""
    anni_list = []
    user = session.get("username")
    try:
        conn_mysql.consume_results()
    except: pass
    try:
        total_sql_emp = '''SELECT COUNT(*) AS total_emp FROM Employees'''
        total_sql_active = '''
        SELECT COUNT(*) AS total_active FROM Employees
        WHERE status = 'Active'
        '''
        total_sql_inactive = '''
        SELECT COUNT(*) AS total_active FROM Employees
        WHERE status = 'inactive'
        '''
        total_departments = '''
        SELECT COUNT(*) AS total_dp FROM Departments
        '''

        anni_emp = '''
        SELECT EmployeeID, HireDate FROM Employees
        '''

        index_salary_qry = '''
        SELECT 
            EmployeeID,
            MAX(Salaryindex) AS CurrentIndex,
            MAX(Salaryindex) - MIN(Salaryindex) AS Difference
        FROM (
            SELECT EmployeeID, Salaryindex
            FROM nemo.salaries_index
            ORDER BY SalaryID DESC
        ) AS recent
        GROUP BY EmployeeID
        HAVING Difference > 5000000;

        '''

        server_cursor.execute(total_sql_emp)
        total_count = server_cursor.fetchone()[0]

        server_cursor.execute(total_sql_active)
        active_count = server_cursor.fetchone()[0]

        server_cursor.execute(total_sql_inactive)
        inactive_count = server_cursor.fetchone()[0]

        server_cursor.execute(total_departments)
        total_dp = server_cursor.fetchone()[0]

        server_cursor.execute(anni_emp)
        anniversaries = server_cursor.fetchall()
        for anni in anniversaries:
            emp = anni[0]
            hired = anni[1]
            if hired.month == today.month and hired.day == today.day:
                anni_list.append(
                    f"Employee.ID {emp} - {hired}"
                )


        with conn_mysql.cursor(dictionary=True,buffered=True) as cursor:
            total_salaries_recieved = '''
            SELECT COUNT(*) AS total_slr FROM salaries
            '''
            highest_slr = '''SELECT MAX(NetSalary) AS max_slr
            FROM salaries'''

            max_leave = '''SELECT EmployeeID AS max_leave FROM attendance
            WHERE LeaveDays > 5 '''

            cursor.execute(total_salaries_recieved)
            total_slr = cursor.fetchone()['total_slr']

            cursor.execute(highest_slr)
            highest_slr_getdata = cursor.fetchone()['max_slr']
            
            
            cursor.execute(max_leave)
            max_leave_emp = cursor.fetchone()


            cursor.execute(index_salary_qry)
            largest_index = cursor.fetchone()

            if max_leave_emp :
                max_leave_day = max_leave_emp["max_leave"]
                

            if largest_index:
                largest_indexs = largest_index['Difference']
                largest_indexes_emp = largest_index["EmployeeID"]

        
        return render_template('home.html',
                               usr = user,
                            total_count=total_count,
                            total_active=active_count,
                            total_inactive=inactive_count,
                            total_dp = total_dp,
                            total_slr=total_slr,
                            highest_SR=highest_slr_getdata,
                            max_leave_day = max_leave_day,
                            anni_list=anni_list,
                            largest_index_slr=largest_indexs,
                            largest_indexes_emp=largest_indexes_emp)


    except Exception as error:
        return {
            "error-message":f"{error}"
        }
    

# trang đăng nhập
@app.route('/login', methods=['GET', 'POST'])
def login():
    message = ""
    session.clear()
    
    if request.method == "POST":
        try:
            username = request.form.get('username')
            password = request.form.get('password')
            email = request.form.get('email')

            my_sql = '''
                SELECT username, password, email, role
                FROM accounts
                WHERE username = %s AND password = %s AND email = %s
            '''
            
            with conn_mysql.cursor() as mysql_cursor:
                mysql_cursor.execute(my_sql, [username, password, email])
                account = mysql_cursor.fetchone()

            if account:
                # Ghi thông tin vào session để middleware sử dụng
                session['username'] = account[0]
                session['email'] = account[2]
                session['role'] = account[3]

                # Tạo JWT Token
                payload = {
                    'user_id': account[0],
                    'email': account[2],
                    'role': account[3],
                    'exp': datetime.datetime.utcnow() + datetime.timedelta(hours=2)  # Token hết hạn sau 2 giờ
                }
                token = jwt.encode(payload, SECRET_KEY, algorithm='HS256')

                message = "Sign in Successfully"
                
                # Trả về giao diện chính kèm token nếu cần
                return render_template("home.html", usr=account[0], token=token)
            else:
                message = "Sorry, this account is invalid"
        except mysql.connector.Error as err:
            return jsonify({'error': str(err)})
    
    return render_template('login.html', msg=message)




# trang đăng kí tài khoản người dùng và phân quyền
@app.route('/register', methods = ['GET','POST'])
def register():
    message = ''
    emailform = ['@gmail.com']
    try:
        conn_mysql.consume_results()
    except: pass
    if request.method == 'POST':

        try:
           
            username = request.form.get('username')
            password = request.form.get('password')
            rppassword = request.form.get('rp-password')
            email = request.form.get('email')
            phone = request.form.get('phonenumber')
            # kiểm tra yêu cầu @gmail.com cần thêm vào dữ liệu đầu vào
            matches = re.search('@gmail.com',email)
            
            check_mysql = '''SELECT * FROM accounts 
                        WHERE username = %s'''
            check_sqlserver = '''SELECT * FROM accounts 
                        WHERE username = ?'''
            mysql_cursor = conn_mysql.cursor()            
            mysql_cursor.execute(check_mysql,[username])
            server_cursor.execute(check_sqlserver,[username])
            mysql_acc = mysql_cursor.fetchone()
            server_acc = server_cursor.fetchone()
            # kiểm tra mức độ của dữ liệu đầu vào
            if (mysql_acc and username == mysql_acc[1]) or (server_acc and username == server_acc[1]):
                message = 'This name is already taken'
            if password != rppassword:
                message = 'Password does not matched'
            if email not in emailform:
                message = 'Email is invalid'
            if (mysql_acc and email == mysql_acc[3]) or (server_acc and email == server_acc[3]):
                message = 'This email account is already taken'
            if not matches or matches == None:
                message = "Invalid email account"
            if not phone:
                message = "Phone is required"
            else:
                my_sql = '''
                INSERT INTO accounts (username,password,email,role)
                VALUES (%s,%s,%s,%s)
                '''
                sql_server = '''
                INSERT INTO accounts (username,password,email,role)
                VALUES (?,?,?,?)
                '''
                mysql_cursor.execute(my_sql,[username,password,email,"not assign"])
                server_cursor.execute(sql_server,[username,password,email,"not assign"])

                conn_mysql.commit()
                server_cursor.connection.commit()
                
                return redirect(url_for('login'))
        except mysql.connector.Error as err:
            return f"Error - {err}"


    return render_template('register.html',msg = message)

# api kiểm tra phiên hoạt động của người dùng theo thời gian hiện tại
@login_required
@app.route("/api/session")
def user_session():
    username = session.get("username")
    role = session.get("role")
    user = {
        "username":username,
        "role":role,
        "check":datetime.datetime.now()
    }
    return jsonify(user)



@login_required
@arms_decorator_cors('staff')
@app.route("/staff",methods=["GET","POST"])
def staff():
    id = session.get("id")
    user = session.get("user")
    emp_sv_query = '''
        SELECT 
            accounts.EmployeeID,
            Employees.Fullname,
            Employees.DateOfBirth,
            Employees.Gender,
            Employees.Phonenumber,
            Employees.Email,
            Employees.DepartmentID,
            Employees.HireDate
        FROM Employees
        INNER JOIN Employees ON Employees.EmployeeID = accounts.EmployeeID
        WHERE accounts.user_id = ?'''
    
    server_cursor.execute(emp_sv_query,(id,))
    employees = server_cursor.fetchone()
    
    return render_template("staff.html",emp=employees,usr=user)


@login_required
@arms_decorator_cors('administrator')
@app.route('/management',methods=['POST','GET'])
def management():
    message = ""
    user = session.get("username")
    if request.method == 'POST':
        empid = request.form.get("employeeid") # cả 2
        firstname = request.form.get("firstname") # cả 2
        lastname = request.form.get("lastname") # cả 2
        phone = request.form.get("Phone") # cả 2
        email = request.form.get("email") # cả 2
        gender = request.form.get("Gender")# SQL server
        birth = request.form.get("birthday")# SQL server
        departmentid = request.form.get("departmentID")
        jobid = request.form.get("jobid") # cả 2
        hiredate = request.form.get("hiredate") # SQL server
        status = request.form.get("status") # cả 2
        departmentname = request.form.get("departmentName") # cả 2
        jobtitle = request.form.get("jobtitle") # cả 2
        

         # Mục lương bổng
         # MySQL
        deduction = request.form.get("deduction")
        bonus = request.form.get("bonus")
        basesalaries = request.form.get("basesalaries")
        netsalaries = request.form.get("netsalaries")
        monthsalary = request.form.get("monthsalary")


        # ghép chuỗi last name và first name
        fullname = str(lastname+firstname)
        # khởi tạo thời gian tạo thông tin nhân sự
        createdat = datetime.datetime.now()
        updateat = datetime.datetime.now() 
        
        def check_department_pos():
            try:
                middle_dpps_mysql = '''
                INSERT INTO departmentpositions (DepartmentID,PositionID)
                VALUES (%s,%s)
                '''

                middle_dpps_sql = '''
                INSERT INTO departmentpositions (DepartmentID,PositionID)
                VALUES (?,?)
                '''

                check_dpps_mysql = '''
                SELECT * FROM departmentpositions
                WHERE DepartmentID = %s AND PositionID = %s
                '''

                check_dpps_sql = '''
                SELECT * FROM departmentpositions
                WHERE DepartmentID = ? AND PositionID = ?
                '''

                with conn_mysql.cursor(dictionary=True,buffered=True) as mysql_cursor:
                    mysql_cursor.execute(check_dpps_mysql,[departmentid,jobid])
                    result_dpps_mysql = mysql_cursor.fetchone()

                    server_cursor.execute(check_dpps_sql,(departmentid,jobid,))
                    result_dpps_sql = server_cursor.fetchone()
                    
                    if result_dpps_mysql and result_dpps_sql:
                        pass
                    else:
                        with conn_mysql.cursor(dictionary=True,buffered=True) as cursor:
                            cursor.execute(middle_dpps_mysql,[departmentid,jobid])
                            conn_mysql.commit()
                        
                        server_cursor.execute(middle_dpps_sql,(departmentid,jobid,))
                        server_cursor.connection.commit()
                    


            except Exception as dpp_error:
                return {
                    "error-message-dppos":f"{dpp_error}"
                }


        try:
            try:
                conn_mysql.consume_results()
            except:
                pass
            #MYSQL
            # Lệnh chèn dữ liệu vào mysql ở mục nhân viên 
            my_sql_emp = '''
            INSERT INTO employees
            (EmployeeID, FullName, DepartmentID, PositionID, Status)
            VALUES (%s,%s,%s,%s,%s)
            '''
            # lệnh tạo phòng ban mới ở logic kiểm tra phía bên dưới
            my_sql_department = '''
            INSERT INTO departments (DepartmentID,DepartmentName)
            VALUES (%s,%s)
            '''
            # lệnh tạo vị trí mới ở logic kiểm tra phía bên dưới
            my_sql_pos = '''
            INSERT INTO positions (PositionID,PositionName)
            VALUES (%s,%s)
            '''

            my_sql_salary = '''
            INSERT INTO salaries 
            (EmployeeID,SalaryMonth,BaseSalary,Bonus,Deductions,
            NetSalary,CreatedAt)
            VALUES (%s,%s,%s,%s,%s,%s,%s)
            '''

            # SQL SERVER
            sql_server_emp = '''
            INSERT INTO employees (
                EmployeeID, FullName, DateOfBirth, Gender, PhoneNumber, Email, HireDate,
                DepartmentID, PositionID, Status, CreatedAt, UpdatedAt
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            '''



            # lệnh tạo phòng ban mới ở logic kiểm tra phía bên dưới
            sql_server_department = '''
            INSERT INTO Departments (DepartmentID,DepartmentName,CreatedAt,UpdatedAt)
            VALUES (?,?,?,?)
            '''
            # lệnh tạo vị trí mới ở logic kiểm tra phía bên dưới
            sql_server_pos = '''
            INSERT INTO Positions (PositionID,PositionName,CreatedAt,UpdatedAt)
            VALUES (?,?,?,?)
            '''

            middle_insert_mysql = '''
            INSERT INTO employeetotallist (EmployeeID,DepartmentID,PositionID,CreatedAt) 
            VALUES (%s,%s,%s,%s)
            '''

            middle_insert_sql = '''
            INSERT INTO employeetotallist (EmployeeID,DepartmentID,PositionID,CreatedAt) 
            VALUES (?,?,?,?)
            '''


            
            


            '''Bổ sung kiểm tra email và sđt vì đây là 2 thông tin đặc thù cho mỗi nhân viên không thể bị trùng'''
            


            # Truy vấn kiêm tra các giá trị tồn tại trong 2 table 
            sql_department = '''
            SELECT * FROM departments
            '''
            sql_pos = '''
            SELECT * FROM positions
            '''

            sql_salary = '''
            SELECT * FROM salaries
            '''

            server_department = '''
            SELECT * FROM Departments
            '''

            server_pos = '''
            SELECT * FROM Positions
            '''

            emp_query = '''SELECT * FROM Employees'''

            mysql_cursor = conn_mysql.cursor()
            
            # Thực thi lệnh từ MySQL
            mysql_cursor.execute(sql_department)
            department = mysql_cursor.fetchall()

            mysql_cursor.execute(sql_pos)
            position = mysql_cursor.fetchall()

            mysql_cursor.execute(sql_salary)
            salaries = mysql_cursor.fetchall()
            #Thực thi lệnh từ SQL Server
            server_cursor.execute(server_department)
            server_dp = server_cursor.fetchall()
            
            server_cursor.execute(server_pos)
            server_ps = server_cursor.fetchall()

            # truy vấn danh sách nhân viên từ bảng Employee

            mysql_cursor.execute(emp_query)
            emp_mysl = mysql_cursor.fetchall()

            server_cursor.execute(emp_query)
            emp_sql = server_cursor.fetchall()

            


            # so sánh thông tin vừa nhập vào với database 
            exist_dp = any(int(departmentid) == int(dp[0]) for dp in department)
            exist_pos = any(int(jobid) == int(pos[0]) for pos in position)
            
            # kiểm tra tồn tại ID
            exist_empid_mysql = any(int(empid) == int(emp[0]) for emp in emp_mysl)
            exist_empid_sql = any(int(empid) == int(emp[0]) for emp in emp_sql)
            # kiểm tra tồn tại phòng ban
            exist_dp_server = any(int(departmentid) == int(dp[0]) for dp in server_dp)
            exist_pos_server = any(int(jobid) == int(ps[0]) for ps in server_ps)
            
            
            # Nếu các thông tin chưa từng tồn tại trước đó
            # hệ thống sẽ khởi tạo một phòng ban và vị trí mới cho nhân viên đó
            if not exist_dp and not exist_dp_server:
                mysql_cursor.execute(my_sql_department,[departmentid,departmentname])
                server_cursor.execute("SET IDENTITY_INSERT Departments ON")
                server_cursor.execute(sql_server_department,[departmentid,departmentname,createdat,updateat])
                server_cursor.execute("SET IDENTITY_INSERT Departments OFF")


            # điều chỉnh tắt ràng buộc identity (auto increment trong sql server)
            # nếu không tắt, hệ thống ẽ mặc định lỗi sai khi điều chỉnh các tham số indentity tăng dần tự động
            if not exist_pos and not exist_pos_server:
                mysql_cursor.execute(my_sql_pos,[jobid,jobtitle])
                server_cursor.execute("SET IDENTITY_INSERT Positions ON")
                server_cursor.execute(sql_server_pos,[jobid,jobtitle,createdat,updateat])
                server_cursor.execute("SET IDENTITY_INSERT Positions OFF")
                

            if exist_empid_mysql and exist_empid_sql:
                message = "This User.ID is already exists"
            
            session["empID"] = empid

            mysql_cursor.execute(my_sql_emp, [empid, fullname, departmentid, jobid, status])
            server_cursor.execute("SET IDENTITY_INSERT employees ON")
            # Thêm thông tin nhân viên vào bảng employees (MySQL)
            server_cursor.execute(sql_server_emp,[empid, fullname, birth, gender, phone, email, hiredate,
                                            departmentid, jobid, status, createdat, updateat])
            server_cursor.execute("SET IDENTITY_INSERT employees OFF")
            print(check_department_pos())

            mysql_cursor.execute(my_sql_salary,[empid,monthsalary,basesalaries,
                                                bonus,deduction,netsalaries,createdat])
            
            

            mysql_cursor.execute(middle_insert_mysql,[empid,departmentid,jobid,createdat])
            server_cursor.execute(middle_insert_sql,[empid,departmentid,jobid,createdat])
            
            

           

            conn_mysql.commit()
            server_cursor.connection.commit()
            Employee(id=empid,name=fullname,email=email,gender=gender,phone=phone,department=department,job=position)
            message = "New Employee has been Added"
            
            # gửi thông báo về một thông tin mới được thêm vào
        except Exception as err:
            
            message = f"{err}"
            print(message)
            return render_template('management.html',msg=message)
        

    return render_template('management.html',msg=message, usr = user)



# hiển thị danh sách
@login_required
@arms_decorator_cors('administrator')
@arms_decorator_cors('HR')
@app.route('/dashboard', methods = ['GET','POST'])
def dashboard():
    user = session.get("username")
    try:
        conn_mysql.consume_results()
    except: 
        pass
    try:
        
        sql_server_qry = '''
            SELECT 
                employeetotallist.EmployeeID,
                Employees.FullName,
                Employees.DateOfBirth,
                Employees.Gender,
                Employees.PhoneNumber,
                Employees.Email,
                Employees.HireDate,
                Departments.DepartmentName AS department,
                Positions.PositionName AS position,
                Employees.Status,
                Employees.CreatedAt,
                Employees.UpdatedAt

            FROM employeetotallist
            INNER JOIN Departments ON employeetotallist.DepartmentID = Departments.DepartmentID
            INNER JOIN Positions ON employeetotallist.PositionID = Positions.PositionID
            INNER JOIN Employees ON employeetotallist.EmployeeID = Employees.EmployeeID
        '''
        
        with conn_mysql.cursor() as cursor:
            server_cursor.execute(sql_server_qry)
            employees = server_cursor.fetchall()
        
        
        return render_template('dashboard.html',human = employees,usr = user)
    except Exception as error:
        return {
            "error-message":f"{error}"
        }


# model sublime - below:
'''
    non-local variables
    if (Post);
       post methods logic (try - except)
    get methods logic - else

'''
@app.route("/edit/<int:id>", methods=["GET", "POST"])
@arms_decorator_cors('administrator')
@arms_decorator_cors('payroll manager')
@arms_decorator_cors('hr manager')
def edit_employees(id):
    user = session.get("username")
    role = session.get("role")  # 'Administrator', 'HR Manager', 'Payroll Manager'
    message = ""

    try:
        conn_mysql.consume_results()
    except:
        pass

    if request.method == "POST":
        empid = request.form.get("employeeid")
        fullname = request.form.get("fullname")
        phone = request.form.get("Phone")
        email = request.form.get("email")
        gender = request.form.get("Gender")
        birth = request.form.get("birthday")
        departmentid = request.form.get("departmentID")
        jobid = request.form.get("jobid")
        hiredate = request.form.get("hiredate")
        status = request.form.get("status")
        departmentname = request.form.get("departmentName")
        jobtitle = request.form.get("jobtitle")

        deduction = request.form.get("deduction")
        bonus = request.form.get("bonus")
        basesalaries = request.form.get("basesalaries")
        netsalaries = request.form.get("netsalaries")
        monthsalary = request.form.get("monthsalary")

        try:
            # --- HR Manager or Administrator: Update HR info ---
            if role in ["hr manager", "administrator"]:
                emp_sql_query = '''
                    UPDATE employees SET
                        Fullname = ?, DateOfBirth = ?, Gender = ?,
                        PhoneNumber = ?, Email = ?, HireDate = ?,
                        DepartmentID = ?, PositionID = ?, Status = ?
                    WHERE EmployeeID = ?
                '''
                server_cursor.execute(emp_sql_query, (
                    fullname, birth, gender,
                    phone, email, hiredate,
                    departmentid, jobid, status, empid
                ))
                server_cursor.connection.commit()

                if role == "Administrator":
                    emp_msql_qry = '''
                        UPDATE employees SET
                            Fullname = %s, DepartmentID = %s, 
                            PositionID = %s, Status = %s
                        WHERE EmployeeID = %s
                    '''
                    with conn_mysql.cursor(dictionary=True, buffered=True) as cursor:
                        cursor.execute(emp_msql_qry, [fullname, departmentid, jobid, status, empid])
                        conn_mysql.commit()

            # --- Payroll Manager or Administrator: Update payroll info ---
            if role in ["payroll manager", "administrator"]:
                salary_update_qry = '''
                    UPDATE salaries SET
                        Bonus = %s, Deductions = %s,
                        BaseSalary = %s, NetSalary = %s, SalaryMonth = %s
                    WHERE EmployeeID = %s
                '''
                
                check_salary_id = '''
                SELECT SalaryID FROM salaries WHERE EmployeeID = %s
                '''


                salary_index_qry = '''
                INSERT INTO salaries_index (SalaryID,EmployeeID,Salaryindex)
                VALUES (%s,%s,%s)
                '''

                
                

                with conn_mysql.cursor(dictionary=True, buffered=True) as cursor:
                    cursor.execute(salary_update_qry, [bonus, deduction, basesalaries, netsalaries, monthsalary, empid])
                    conn_mysql.commit()

                with conn_mysql.cursor(dictionary=True, buffered=True) as cursor:
                    cursor.execute(check_salary_id,[empid])
                    slryID = cursor.fetchone()
                    if slryID:
                        slry_id = slryID["SalaryID"]
                        cursor.execute(salary_index_qry,[slry_id,empid,netsalaries])
                    
                    else:
                        message = f"Salary ID {slryID} is invalid"
                    conn_mysql.commit()
                # with conn_mysql.cursor(dictionary=True,buffered=True) as q_cursor:
            else:
                return {
                    "error":"role denied"
                },403

            # Lấy lại thông tin sau khi cập nhật
            emp_sv_query = '''
                SELECT 
                    Employees.EmployeeID,
                    Employees.Fullname,
                    Employees.DateOfBirth,
                    Employees.Gender,
                    Employees.Phonenumber,
                    Employees.Email,
                    Employees.DepartmentID,
                    Departments.DepartmentName as departmentname,
                    Employees.PositionID,
                    Positions.PositionName as positionname,
                    Employees.HireDate
                FROM Employees
                INNER JOIN Departments ON Departments.DepartmentID = Employees.DepartmentID
                INNER JOIN Positions ON Positions.PositionID = Employees.PositionID
                WHERE Employees.EmployeeID = ?
            '''
            server_cursor.execute(emp_sv_query, (id,))
            employees = server_cursor.fetchone()

            message = "Update Successfully"
            return render_template("editemp.html", usr=user, msg=message, emp=employees, role=role)

        except Exception as err:
            return {"error-message": f"{err}"}

    else:
        # GET: load data
        try:
            emp_sv_query = '''
                SELECT 
                    Employees.EmployeeID,
                    Employees.Fullname,
                    Employees.DateOfBirth,
                    Employees.Gender,
                    Employees.Phonenumber,
                    Employees.Email,
                    Employees.DepartmentID,
                    Departments.DepartmentName as departmentname,
                    Employees.PositionID,
                    Positions.PositionName as positionname,
                    Employees.HireDate
                FROM Employees
                INNER JOIN Departments ON Departments.DepartmentID = Employees.DepartmentID
                INNER JOIN Positions ON Positions.PositionID = Employees.PositionID
                WHERE Employees.EmployeeID = ?
            '''
            server_cursor.execute(emp_sv_query, (id,))
            employees = server_cursor.fetchone()

            return render_template("editemp.html", msg=message, emp=employees, usr=user, role=role)

        except Exception as err:
            return {"error-message": f"{err}"}, 405

    
    
@login_required
@app.route("/delete/<int:id>", methods = ["GET","POST"])
@arms_decorator_cors("administrator")
@arms_decorator_cors('HR')
def delete_employees(id):
    if request.method == "GET":
        message = ""
        check_records  = '''SELECT * FROM employees
                        WHERE EmployeeID = %s'''
        check_records_server  = '''SELECT * FROM Employees
                        WHERE EmployeeID = ?'''

        dlt_emp_query = '''DELETE FROM employees
                        WHERE EmployeeID = %s'''
        server_rm_query = '''DELETE FROM Employees
                        WHERE EmployeeID = ?'''
        user = session.get("username")
        
        try:
            try:
                conn_mysql.consume_results()
            except:
                pass
            cursor = conn_mysql.cursor(dictionary=True)
            cursor.execute(check_records,[id])
            exists_records = cursor.fetchone()
            
            sv_cursor = conn_server.cursor()
            sv_cursor.execute(check_records_server,(id,))
            sv_exists_records = sv_cursor.fetchone()


            if not exists_records and not sv_exists_records:
                message = f"Employee {id} is invalid"
            else:
                cursor.execute(dlt_emp_query,[id])
                conn_mysql.commit()

                sv_cursor.execute(server_rm_query,(id,))
                conn_server.commit()

                message = f"Employee {id} has been deleted"
            return render_template('dashboard.html',
                                msg = message,
                                usr = user)
        except Exception as error:
            return {
                "error-message":f"{error}"
            } 
    return redirect(url_for("dashboard"))



@app.route("/search",methods=["GET","POST"])
def search():
    message = ""
    if request.method == "POST":
        searchvalue = request.form.get("searchfield")
        sql_server_qry = '''
            SELECT 
                Employees.EmployeeID,
                Employees.FullName,
                Employees.DateOfBirth,
                Employees.Gender,
                Employees.PhoneNumber,
                Employees.Email,
                Employees.HireDate,
                Departments.DepartmentName AS department,
                Positions.PositionName AS position,
                Employees.Status,
                Employees.CreatedAt,
                Employees.UpdatedAt

            FROM Employees
            INNER JOIN Departments ON Employees.DepartmentID = Departments.DepartmentID
            INNER JOIN Positions ON Employees.PositionID = Positions.PositionID 
            WHERE
                Employees.EmployeeID LIKE ? OR
                Employees.FullName LIKE ? OR
                Employees.PhoneNumber LIKE ? OR 
                Departments.DepartmentName LIKE ? OR 
                Positions.PositionName LIKE ?
        '''
        # sử dụng lệnh truy vấn LIKE nhằm mục đích hiển thị kết ngay từ khóa đầu tiên
        try:
            
            search_param = f"%{searchvalue}%"
            server_cursor.execute(sql_server_qry,(search_param, search_param, search_param, search_param, search_param))
            result = server_cursor.fetchall()
            # Nếu kết quả chứa các kí tự theo từ khóa
            if result:
                
                return render_template("dashboard.html",human=result)
            else:
                # trả về thông báo nếu không tìm thấy kết quả nào khớp
                message = "No result found"

        except Exception as error:
            return f"{error}"
        return render_template("dashboard.html",msg = message)
    

@app.route('/clear',methods = ["POST","GET"])
@arms_decorator_cors("administrator")
# xóa tất cả các dữ liệu employees - yêu cầu : Admin
def clear_all_employees_data():
    message = ""
    user = session.get("username")
    if request.method == "POST":
        # xóa ở mục My SQL
        mysql_cursor = conn_mysql.cursor()
        mysql_query = '''TRUNCATE TABLE employees'''
        mysql_cursor.execute(mysql_query)
        conn_mysql.commit()
        #Xóa ở mục SQL Server
        server_query = '''TRUNCATE TABLE employees'''
        server_cursor.execute(server_query)
        server_cursor.connection.commit()

        message = "Employees Data have been dropped"

    return render_template('/management.html',usr=user,msg = message)




# Danh sách bảng lương nhân viên
@app.route("/payroll",methods=["GET","POST"])
@arms_decorator_cors('administrator')
@arms_decorator_cors("Payroll manager")
def payroll():
    # Non-local Variables
    message = ""
    salaries = []
    data = []
    user = session.get("username")

    mysql_query = '''
        SELECT
            salaries.SalaryID,
            salaries.EmployeeID,
            employees.FullName as fullname,
            salaries.BaseSalary,
            salaries.SalaryMonth,
            salaries.Bonus,
            salaries.Deductions,
            salaries.NetSalary,
            salaries.CreatedAt
        FROM salaries
        INNER JOIN employees ON employees.EmployeeID = salaries.EmployeeID

        '''
    
        
    data = []
    try:
        conn_mysql.consume_results()
    except:
        pass
    with conn_mysql.cursor(buffered=True) as mysql_cursor:
        mysql_cursor.execute(mysql_query)
        salary = mysql_cursor.fetchall()
        for obj in salary:
            data.append(
                {
                    "SalaryID":obj[0],
                    "EmployeeID":obj[1],
                    "Fullname":obj[2],
                    "BaseSalary":obj[3],
                    "SalaryMonth":obj[4],
                    "Bonus":obj[5],
                    "Deductions":obj[6],
                    "NetSalary":obj[7],
                    "Createat":obj[8]

                }
            )
       
                       
        
    try:
        salaries = data
        return render_template("salaries.html",slr = salaries,usr=user,msg=message)

    except Exception as error:
        message = f"{error}"
        return {
            "error-message":f"{message}"
        }


@app.route("/attendance/<int:id>", methods=["GET", "POST"])
@arms_decorator_cors("Payroll Manager")
@arms_decorator_cors('administrator')
def attendance(id):

    empid = request.form.get("employee_id")
    workdays = request.form.get("workdays", type=int)
    absentdays = request.form.get("absentdays", type=int)
    leavedays = request.form.get("leavedays", type=int)
    attendancemonth = request.form.get("attendancemonth")

    user = session.get("username")
    message = ""
    try:
        conn_mysql.consume_results()
    except: pass
    if request.method == "POST":
        sql = '''
        INSERT INTO attendance (EmployeeID, WorkDays, AbsentDays, LeaveDays, AttendanceMonth, CreatedAt)
        VALUES (%s, %s, %s, %s, %s, NOW()) 

        '''
        try:
            with conn_mysql.cursor(dictionary=True,buffered=True) as cursor:
                cursor.execute(sql,[empid,workdays,absentdays,leavedays,attendancemonth])
                conn_mysql.commit()
                message = "Attendance Successfully"
        except Exception as error:
            return {
                "error-message":f"{error}"
            }           
    return render_template("attendance.html",EmployeeID=id,usr=user,msg=message)



    

        

# Hiển thị dánh sách phòng ban
@app.route("/departments",methods=["GET","POST"])
@arms_decorator_cors('administrator')
# danh sách phòng ban là không yêu cầu ràng buộc bởi vai trò cụ thể nên ko dùng đến middleware
def show_departments():
    message = ""
    departments = []
    user = session.get("username")
    try:
        conn_mysql.consume_results()
    except: 
        pass
      
    try:
        
        sql = '''SELECT DISTINCT
                    
                    departmentpositions.DepartmentID as departmentID,
                    departments.DepartmentName as departmentname
                    
                FROM departmentpositions
                INNER JOIN departments ON departments.departmentID = departmentpositions.DepartmentID'''
        #tùy chỉnh 1 trong 2 CSDL 
        with conn_mysql.cursor(dictionary=True,buffered=True) as mysql_cursor:
            mysql_cursor.execute(sql)
            result = mysql_cursor.fetchall()
            for obj in result:
                departments.append(
                    {
                        
                        "DepartmentID":obj["departmentID"],
                        "DepartmentName":obj["departmentname"]
                    }
                )
        return render_template("departments.html"
                            ,usr = user,message = message, department = departments)
    except Exception as error:
        return {
            "error-message":f"{error}"
        }      
        



@app.route('/positions/<int:id>',methods=["GET","POST"])
@arms_decorator_cors('administrator')
def show_positions(id):
    positions = []
    user = session.get("username")
    try:
        conn_mysql.consume_results()
    except : pass

    if request.method == "POST":
        sql = '''
        
        SELECT DISTINCT
            
            departmentpositions.PositionID as PositionID,
            Positions.PositionName as PositionName
        FROM departmentpositions
        INNER JOIN Positions ON Positions.PositionID = departmentpositions.PositionID
        WHERE departmentpositions.DepartmentID = %s
        

        '''
        try:
            with conn_mysql.cursor(dictionary=True,buffered=True) as mysql_cursor:
                mysql_cursor.execute(sql,[id])
                result = mysql_cursor.fetchall()
                for obj in result:
                    positions.append(
                        {
                            "PositionID":obj["PositionID"],
                            "PositionName":obj["PositionName"]
                        }
                    )
            return render_template("position.html",usr=user,positions=positions)
        except Exception as error:
            return {
                "error-message":f"{error}"
            }
    else:
        sql = '''
        
        SELECT DISTINCT
            
            departmentpositions.PositionID as PositionID,
            Positions.PositionName as PositionName
        FROM departmentpositions
        INNER JOIN Positions ON Positions.PositionID = departmentpositions.PositionID
        WHERE departmentpositions.DepartmentID = %s
        

        '''
        try:
            with conn_mysql.cursor(dictionary=True,buffered=True) as mysql_cursor:
                mysql_cursor.execute(sql,[id])
                result = mysql_cursor.fetchall()
                for obj in result:
                    positions.append(
                        {
                            "PositionID":obj["PositionID"],
                            "PositionName":obj["PositionName"]
                        }
                    )
            return render_template("position.html",usr=user,positions=positions)
        except Exception as error:
            return {
                "error-message":f"{error}"
            }


            

# hiển thị danh sách tài khoản ban quản trị - administrator
@app.route('/rights',methods = ["GET","POST"])
@arms_decorator_cors("administrator")
def permission_rights():
    message = ""
    accounts = []
    user = session.get("username")

    # chưa dùng tới
    # sqlserver_query = '''SELECT * FROM accounts'''
    # server_cursor.execute(sqlserver_query)
    # sqlserver_accounts = server_cursor.fetchall()
    try:
        conn_mysql.consume_results()
    except:
        pass

    with conn_mysql.cursor(buffered=True) as mysql_cursor:
        mysql_query = '''SELECT * FROM accounts'''
        mysql_cursor.execute(mysql_query)
        mysql_accounts = mysql_cursor.fetchall()
        
    
        for obj in mysql_accounts:

            accounts.append(
                {
                    "userID": obj[0],
                    "Username": obj[1],
                    "Email":obj[3],
                    "Role":obj[4]
                }
            )
        
    
    return render_template("rights&role.html",usr = user,account = accounts)







#Tìm kiếm tài khoản thuộc ban quản trị 
@app.route('/rolesearch',methods = ['GET','POST'])
@arms_decorator_cors("administrator")
def accounts_search():
    mysql_cursor = conn_mysql.cursor()
    accounts = []
    user = session.get("username")
    params = request.form.get("searchfield")
    sql = '''
    SELECT * FROM accounts
    WHERE user_id LIKE %s OR
    username LIKE %s OR
    role LIKE %s OR
    email LIKE %s
    '''
    mysql_cursor.execute(sql,[params,params,params,params])
    result = mysql_cursor.fetchall()

    try:
        if result:
            for obj in result:

                accounts.append(
                    {
                        "userID": obj[0],
                        "Username": obj[1],
                        "Email":obj[3],
                        "Role":obj[4]
                    }
                )
                
            
            
            return render_template("rights&role.html",usr = user,account = accounts)
    except Exception as error:
        return {
            "error-message":f"{error}"
        }
    return render_template("rights&role.html",usr = user,account = accounts)

    




# chỉnh sửa quyền và thông tin vai trò

# model sublime - below:
'''
    non-local variables
    if (Post);
       post methods logic (try - except)
    get methods logic - else

'''
@app.route("/rights/<int:id>", methods = ["GET","POST"])
@arms_decorator_cors("administrator")
def edit_rights(id):
    
    # xác định người dùng hiện tại qua session lữu trữ
    user = session.get('username')
    message = ""
    try:
        conn_mysql.consume_results()
    except:
        pass
    if request.method == "POST":
        form_request_id = request.form.get("user_id")
        form_request_role= request.form.get("role")
        

        try:

            
            sql_sv_query = '''
                UPDATE accounts SET role = ? 
                WHERE user_id = ?
            '''

            with conn_mysql.cursor(buffered=True,dictionary=True) as mysql_curssor:
                sql_query = '''UPDATE accounts SET role = %s 
                        WHERE user_id = %s'''
                mysql_curssor.execute(sql_query,[form_request_role,form_request_id])
                conn_mysql.commit()
                
            with conn_mysql.cursor(buffered=True,dictionary=True) as mysql_curssor:
                mysql_query = '''SELECT * FROM accounts WHERE user_id = %s'''
                mysql_curssor.execute(mysql_query, [form_request_id])
                data = mysql_curssor.fetchone()

                accounts = {
                    "userID": data["user_id"],
                    "username": data["username"],
                    "Email": data["email"],
                    "role": data["role"]
                }
            


            # Truy vấn lại thông tin account để render template
            
            server_cursor.execute(sql_sv_query,(form_request_role,form_request_id,))    
            server_cursor.connection.commit()

            message = "Updated rights & permissions successfully"
            return render_template("permissionedit.html",msg = message,usr=user,account=accounts)
        except Exception as error:
            return {
                "error-message":f"{error}"
            },405

       
        
    else:
        try:
            message = ""
            mysql_query = '''SELECT * FROM accounts
                            WHERE user_id = %s
                        '''
            sql_query = '''SELECT * FROM accounts
                            WHERE user_id = ?
                    '''
            # lệnh truy vấn vào MySQL
            with conn_mysql.cursor(buffered=True,dictionary=True) as mysql_curssor:
                mysql_curssor.execute(mysql_query,[id])
                data = mysql_curssor.fetchone()
                accounts = {
                        "userID":data["user_id"],
                        "username":data["username"],
                        "Email":data["email"],
                        "role":data["role"]
                    }
            
            # lệnh  truy vấn vào SQL server
            server_cursor.execute(sql_query,(id,))
            server_cursor.fetchone()

            
            return render_template("permissionedit.html",msg = message,usr=user, account = accounts)
        except Exception as error:
            return {
                "error-message":f"{error}"
            },408
            

   
@app.route("/delete/account<int:id>", methods = ["GET","POST"])
@arms_decorator_cors('administrator')
def delete_accounts(id):
    message = ""
    converted_cursor = conn_mysql.cursor(dictionary=True)
    user = session.get("username")
    if request.method == "POST":
       
        try:
            sql_sv_query = '''SELECT * FROM accounts WHERE user_id = ?'''
            sql_query = '''SELECT * FROM accounts WHERE user_id = %s'''
    
            converted_cursor.execute(sql_query,[id])
            check_record_mysql = converted_cursor.fetchone()

            server_cursor.execute(sql_sv_query,(id,))
            check_record_server = server_cursor.fetchone()

            if not check_record_mysql and not check_record_server:
                message = "This account is invalid"
                return render_template("rights&role.html",msg=message,usr=user)
            else:
                del_mysql = '''DELETE FROM accounts WHERE user_id = %s'''
                del_server = '''DELETE FROM accounts WHERE user_id = ?'''

                converted_cursor.execute(del_mysql,[id])
                server_cursor.execute(del_server,(id,))

                conn_mysql.commit()
                server_cursor.connection.commit()

                message = "This Account has been Deleted"
                return render_template("rights&role.html",msg=message,usr=user)
            
        except Exception as error:
            return {
                "error-message":f"{error}"
            },405
        
    return render_template("rights&role.html",msg=message,usr=user)
            
@app.route("/email/<int:id>", methods=["GET", "POST"])
@arms_decorator_cors('Payroll Manager')
@arms_decorator_cors('administrator')
def send_payroll_email(id):
    message = ""
    user = session.get("username")
    hr_email = "mtranquoc77@gmail.com"
    hr_password = "hxursqpuhpimjwlr"
    emp_email = ""
    try:
        conn_mysql.consume_results()
    except:
        pass

    if request.method == "POST":
        try:
            greet = "Greeting"
            

            
            sql = "SELECT * FROM salaries WHERE EmployeeID = %s"
            with conn_mysql.cursor(dictionary=True, buffered=True) as cursor:
                cursor.execute(sql, [id])
                notice_data = cursor.fetchone()

            
            email_emp = "SELECT Email FROM Employees WHERE EmployeeID = ?"
            server_cursor.execute(email_emp, (id,))
            email_data = server_cursor.fetchone()

            if not notice_data or not email_data:
                message = "Invalid Email"
                return render_template("emailSend.html", msg=message, usr=user)

            email = email_data[0]
            base_salary = notice_data['BaseSalary']
            month_salary = notice_data['SalaryMonth']
            net_salary = notice_data['NetSalary']
            deduction = notice_data['Deductions']

            msg = MIMEMultipart('alternative')
            msg["Subject"] = "Monthly Payroll Notice"
            msg["From"] = hr_email
            msg["To"] = email

            template = f'''
                <html>
                <head></head>
                <body>
                    <h2>📢 Official Monthly Salary Notification</h2>
                    <p>Hello,</p>
                    <p>This is your official salary information for the month:</p>
                    <ul>
                        <li><strong>Month:</strong> {month_salary}</li>
                        <li><strong>Base Salary:</strong> VND {base_salary}</li>
                        <li><strong>Deductions:</strong> VND {deduction}</li>
                        <li><strong>Net Salary:</strong> <b style="color: green;">VND {net_salary}</b></li>
                    </ul>
                    <p>For more details, please contact HR.</p>
                    <p>Thank you.</p>
                </body>
                </html>
            '''

            # Gửi email
            part1 = MIMEText(greet, 'plain')
            part2 = MIMEText(template, 'html')
            msg.attach(part1)
            msg.attach(part2)
            print("Attach mail...")
            time.sleep(3)
            server = smtplib.SMTP('smtp.gmail.com', 587)
            server.starttls()
            server.login(hr_email, hr_password)
            print(f"Wrapping content and Sending to {email} ...")
            time.sleep(3)
            server.sendmail(hr_email, email, msg.as_string())
            server.quit()

            message = "📧 Email sent !"
            return render_template("emailSend.html",
                                empid=id,
                                msg=message,
                                hr_email=hr_email,
                                emp_email = email,
                                content = template, usr=user)

        except Exception as error:
            
            return {"error-message": f"{error}"}
    else:
        greet = "Greeting"
        sql = "SELECT * FROM salaries WHERE EmployeeID = %s"
        with conn_mysql.cursor(dictionary=True, buffered=True) as cursor:
            cursor.execute(sql, [id])
            notice_data = cursor.fetchone()

        
        email_emp = "SELECT Email FROM Employees WHERE EmployeeID = ?"
        server_cursor.execute(email_emp, (id,))
        email_data = server_cursor.fetchone()

        if not notice_data or not email_data:
            message = "Invalid Email"
            return render_template("emailSend.html",empid=id, msg=message, usr=user)

        email = email_data[0]
        base_salary = notice_data['BaseSalary']
        month_salary = notice_data['SalaryMonth']
        net_salary = notice_data['NetSalary']
        deduction = notice_data['Deductions']

        msg = MIMEMultipart('alternative')
        msg["Subject"] = "Monthly Payroll Notice"
        msg["From"] = hr_email
        msg["To"] = email

        template = f'''
            <html>
            <head></head>
            <body>
                <h2>📢 Official Monthly Salary Notification</h2>
                <p>Hello,</p>
                <p>This is your official salary information for the month:</p>
                <ul>
                    <li><strong>Month:</strong> {month_salary}</li>
                    <li><strong>Base Salary:</strong> VND {base_salary}</li>
                    <li><strong>Deductions:</strong> VND {deduction}</li>
                    <li><strong>Net Salary:</strong> <b style="color: green;">VND {net_salary}</b></li>
                </ul>
                <p>For more details, please contact HR.</p>
                <p>Thank you.</p>
            </body>
            </html>
        '''

        # Gửi email
        part1 = MIMEText(greet, 'plain')
        part2 = MIMEText(template, 'html')
        msg.attach(part1)
        msg.attach(part2)
        print("Attach mail...")
        time.sleep(3)
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(hr_email, hr_password)
        print(f"Wrapping content and Sending to {email} ...")
        time.sleep(3)
        server.sendmail(hr_email, email, msg.as_string())
        server.quit()

        message = "📧 Email sent !"
        return render_template("emailSend.html",empid=id, msg=message,
                            hr_email=hr_email,
                            emp_email = email,
                            content = template, usr=user)


        

   
    
    
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