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
    print(check_accounts())
    
