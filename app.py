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
# import config
import mysql.connector
import pyodbc

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
mysql_cursor = conn_mysql.cursor()

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
    user = session.get("username")
    # check_status('/')
    return render_template('home.html',usr = user)

# trang đăng nhập
@app.route('/login', methods = ['GET','POST'])
def login():
    message = ""
    if request.method == "POST":
        try:
            
            username = request.form.get('username')
            password = request.form.get('password')
            email = request.form.get('email')

            my_sql = '''
                SELECT username,password,email,role
                FROM accounts
                WHERE username = %s AND password = %s AND email = %s
                
                '''
            
            mysql_cursor.execute(my_sql,[username,password,email])
            account = mysql_cursor.fetchone()
            if account:
                
                message = "Sign in Successfully"
                login_user(
                        User(
                        name=account[0],
                        email=account[2],
                        role=account[3]
                    )
                )
                session['username'] = account[0]
                session['email'] = account[2]
                session['role'] = account[3]
                return render_template("home.html")
            
            else:
                message = "Sorry, This account is invalid"
        except mysql.connector.Error as err:
            return err
    return render_template('login.html',msg = message)




# trang đăng kí tài khoản người dùng và phân quyền
@app.route('/register', methods = ['GET','POST'])
def register():
    message = ''
    emailform = ['@gmail.com']
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
        

        



        try:
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


            # so sánh thông tin vừa nhập vào với database 
            exist_dp = any(int(departmentid) == int(dp[0]) for dp in department)
            exist_pos = any(int(jobid) == int(pos[0]) for pos in position)
            exist_salary = any(int(empid) == int(sal[1]) for sal in salaries)



            exist_dp_server = any(int(departmentid) == int(dp[0]) for dp in server_dp)
            exist_pos_server = any(int(jobid) == int(ps[0]) for ps in server_ps)
            if basesalaries == "" or bonus == "":
                flask.flash("Base value or Bonus must be added first")
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
            session["empID"] = empid

            mysql_cursor.execute(my_sql_emp, [empid, fullname, departmentid, jobid, status])
            server_cursor.execute("SET IDENTITY_INSERT employees ON")
            # Thêm thông tin nhân viên vào bảng employees (MySQL)
            server_cursor.execute(sql_server_emp,[empid, fullname, birth, gender, phone, email, hiredate,
                                            departmentid, jobid, status, createdat, updateat])
            server_cursor.execute("SET IDENTITY_INSERT employees OFF")
           

            mysql_cursor.execute(my_sql_salary,[empid,monthsalary,basesalaries,
                                                bonus,deduction,netsalaries,createdat])

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
    try:
        
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
        
        server_cursor.execute(sql_server_qry)
        employees = server_cursor.fetchall()
        
        user = session.get("username")
        return render_template('dashboard.html',human = employees,usr = user)
    except Exception as error:
        return error

@app.route("/edit/<int:id>",methods=["GET","POST"])
@arms_decorator_cors("administrator")
def edit_employees(id):
    if request.method == "GET":
        emp_sql_query = '''SELECT * FROM employees WHERE Employeeid = %s'''
        message = ""
        try:
            cursor = conn_mysql.cursor(dictionary=True)
            cursor.execute(emp_sql_query,[id])
            employee = cursor.fetchone()
            if not employee:
                message = f"Employee {id} is invalid"
            
            else:
                user = session.get("username")
                return render_template("editemp.html",emp=employee,usr=user,msg = message)
            
            

        except Exception as err:
            return {
                "error-message":f"{err}"
            }
        
@app.route("/delete/<int:id>", methods = ["GET","POST"])
@arms_decorator_cors("administrator")
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
@arms_decorator_cors("Payroll Manager")
def payroll():
    message = ""
    salaries = []
    if request.method == 'POST':
        mysql_query = '''SELECT * FROM salaries'''
        try:
            mysql_cursor.execute(mysql_query)
            salary = mysql_cursor.fetchall()
            for obj in salary:
                salaries.append(
                    {
                        "Salary ID":obj[0],
                        "Employee ID":obj[1]
                    }
                )
            return render_template("",slr = salaries)
        except Exception as error:
            message = f"{error}"
            return {
                "error-message":f"{message}"
            }
        

        
        


@app.route('/rights',methods = ["GET","POST"])
@arms_decorator_cors("administrator")
def permission_rights():
    message = ""
    accounts = []
    mysql_query = '''SELECT * FROM accounts'''
    mysql_cursor.execute(mysql_query)
    mysql_accounts = mysql_cursor.fetchall()
    
    # chưa dùng tới
    sqlserver_query = '''SELECT * FROM accounts'''
    server_cursor.execute(sqlserver_query)
    sqlserver_accounts = server_cursor.fetchall()
    for obj in mysql_accounts:

        accounts.append(
            {
                "userID": obj[0],
                "Username": obj[1],
                "Email":obj[3],
                "Role":obj[4]
            }
        )
        
    user = session.get("username")
    return render_template("rights&role.html",usr = user,account = accounts)
        
@app.route('/rolesearch',methods = ['GET','POST'])
@arms_decorator_cors("administrator")
def accounts_search():
    accounts = []
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
                
            
            user = session.get("username")
            return render_template("rights&role.html",usr = user,account = accounts)
    except Exception as error:
        return {
            "error-message":f"{error}"
        }
    




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
    converted_sqlcursor = conn_mysql.cursor(dictionary=True)
    
    if request.method == "POST":
        form_request_id = request.form.get("user_id")
        form_request_role= request.form.get("role")
        

        try:
            sql_sv_query = '''
                UPDATE accounts SET role = ? 
                WHERE user_id = ?
            '''

            sql_query = '''UPDATE accounts SET role = %s 
                        WHERE user_id = %s'''
            converted_sqlcursor.execute(sql_query,[form_request_role,form_request_id])
            conn_mysql.commit()

            server_cursor.execute(sql_sv_query,(form_request_role,form_request_id,))    
            server_cursor.connection.commit()


            # Truy vấn lại thông tin account để render template
            mysql_query = '''SELECT * FROM accounts WHERE user_id = %s'''
            converted_sqlcursor.execute(mysql_query, [form_request_id])
            data = converted_sqlcursor.fetchone()

            accounts = {
                "userID": data["user_id"],
                "username": data["username"],
                "Email": data["email"],
                "role": data["role"]
            }

            message = "Updated rights & permissions successfully"
            return render_template("permissionedit.html",msg = message,usr=user,account=accounts)
        except Exception as error:
            return {
                "error-message":f"{error}"
            }

       
        
    try:
        message = ""
        mysql_query = '''SELECT * FROM accounts
                        WHERE user_id = %s
                    '''
        sql_query = '''SELECT * FROM accounts
                        WHERE user_id = ?
                '''
        # lệnh truy vấn vào MySQL
        converted_sqlcursor.execute(mysql_query,[id])
        data = converted_sqlcursor.fetchone()
        
        # lệnh  truy vấn vào SQL server
        server_cursor.execute(sql_query,(id,))
        server_cursor.fetchone()

        accounts = {
                "userID":data["user_id"],
                "username":data["username"],
                "Email":data["email"],
                "role":data["role"]
            }
        return render_template("permissionedit.html",msg = message,usr=user, account = accounts)
    except Exception as error:
        return {
            "error-message":f"{error}"
        },408
        

   
@app.route("/delete/account<int:id>", methods = ["GET","POST"])
@arms_decorator_cors('administrator')
def delete_accounts(id):
    if request.method == "POST":
        message = ""
        converted_cursor = conn_mysql.cursor(dictionary=True)
        user = session.get("username")
        try:
            sql_sv_query = '''SELECT * FROM accounts WHERE user_id = ?'''
            sql_query = '''SELECT * FROM accounts WHERE user_id = %s'''
    
            converted_cursor.execute(sql_query,[id])
            check_record_mysql = converted_cursor.fetchone()

            server_cursor.execute(sql_sv_query,(id,))
            check_record_server = server_cursor.fetchone()

            if not check_record_mysql and not check_record_server:
                message = "This account is invalid"
                return render_template("rights&role.htnl",msg=message,usr=user)
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