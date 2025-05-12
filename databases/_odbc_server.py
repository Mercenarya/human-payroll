import pyodbc
import time

server = 'LAPTOP-OOTVABFJ\\SQLEXPRESS'
database = 'HUMAN'
# username = 'LAPTOP-OOTVABFJ\Admin'
# password = 'Minh_17102004'
driver = '{ODBC Driver 17 for SQL Server}'

# Vì SQL Server chạy và hoạt động trên máy chính chủ nên sẽ sử dụng
#Trusted_Connection=yes thay vì dùng username và password thông thường
conn = pyodbc.connect(
    f'DRIVER={driver};SERVER={server};DATABASE={database};Trusted_Connection=yes;'
)

# Kiêm tra kết nối đến server
print("Connected")
cursor = conn.cursor()

def check_employees():
    cursor.execute("SELECT * FROM Employees")
    for obj in cursor.fetchall():
        print(obj)

# Khởi tạo bảng tài khoản người dùng hệ thống
def create_accounts():
    sql = '''
        CREATE TABLE accounts (
            user_id INT IDENTITY(1,1) PRIMARY KEY,
            username VARCHAR(250) NOT NULL,
            password VARCHAR(250) NOT NULL,
            email VARCHAR(250) NOT NULL,
            role VARCHAR(150) NOT NULL
        )
    '''
    try:
        cursor.execute(sql)
        cursor.connection.commit()
        return "Accounts set up"
    except pyodbc.Error as err:
        return err
    
# Tạo một tài khoản hệ thống với quyền là Administrator
def new_accounts():
    sql = '''
        INSERT INTO accounts (username,password,email,role)
        VALUES ('admin','admin_123','mtranquoc77@gmail.com','administrator')
    '''
    try:
        cursor.execute(sql)
        cursor.connection.commit()
        return "new account have been created"
    except pyodbc.Error as err:
        return err

def check_accounts():
    sql = '''
    SELECT * FROM accounts
    '''
    try:
        cursor.execute(sql)
        for obj in cursor.fetchall():
            print(f"Username: {obj[1]} - email: {obj[3]} - role: {obj[4]}")
    except pyodbc.Error as err:
        return err
    
'''Các bảng CSDL nguyên bản sau khi tạo thành đều cần đến các bảng CSDL trung gian'''
"Mục đích của các bản CSDL để nhằm đảm bảo tính chuẩn hóa CSDL,"
" tính mở rộng cho các bảng, tránh các xung đột và khuyết điểm không cần thiết"

def create_middle_department_pos():
    try:
        sql = '''
        CREATE TABLE DepartmentPositions (
            ID INT IDENTITY PRIMARY KEY,
            DepartmentID INT NOT NULL,
            PositionID INT NOT NULL,
            FOREIGN KEY (DepartmentID) REFERENCES departments(DepartmentID),
            FOREIGN KEY (PositionID) REFERENCES positions(PositionID)
        )
        '''
        cursor.execute(sql)
        conn.commit()
        return "DeparmentPositions has established"
    except pyodbc.Error as err:
        return f"{err}"
def create_middle_employees_dp_pos():
    try:
        sql = '''
            CREATE TABLE employeetotallist  (
                ID INT IDENTITY PRIMARY KEY ,
                EmployeeID INT NOT NULL,
                DepartmentID INT NOT NULL,
                PositionID INT NOT NULL,
                CreatedAt DATETIME NULL DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (DepartmentID) REFERENCES departments(DepartmentID),
                FOREIGN KEY (PositionID) REFERENCES positions(PositionID),
                FOREIGN KEY (EmployeeID) REFERENCES employees(EmployeeID)
            )
        '''
        cursor.execute(sql)
        cursor.connection.commit()
        return "Table Employee has established"
    except pyodbc.Error as err:
        return f"{err}"
def truncate_emp():
    sql = '''TRUNCATE TABLE employees'''
    try:
        cursor.execute(sql)
        cursor.connection.commit()
        return "Clear records of employees"
    except pyodbc.Error as err:
        return f"{err}"

if __name__ == "__main__":
    # cursor.execute("SELECT * FROM sys.tables")
    print("Requesting...")
    time.sleep(5)
    # for obj in cursor.fetchall():
    #     print(obj)
    print('*'*50)
    # print(check_employees())
    # print(create_accounts())
    # print(new_accounts())
    # print(check_accounts())
    print(create_middle_department_pos())
    print(create_middle_employees_dp_pos())
    # print(truncate_emp())

