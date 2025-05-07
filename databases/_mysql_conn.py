import mysql.connector
import os
import cryptography
from cryptography.fernet import Fernet

# tạo hash khóa
key = Fernet.generate_key()
key_handler = "theboisdbsecrethandler"

# tạo kết nối đến database
conn = mysql.connector.connect(
    host="localhost",
    user='root',
    password = "Minh_17102004",
    database = "NEMO"
)
cursor = conn.cursor()



# kiểm tra kết nối tới mysql workbench
def check_connection():
    try:
        if conn.is_connected():
            return f'{conn._database} is connected'
        return f'{conn._database} is disconnected'
    except mysql.connector.Error as err:
        return err
# Tạo database - sau khi tạo xong , nhớ gán tên database ở mục database của conn ở trên 
def create_db():
    try:
        sql = '''CREATE DATABASE NEMO'''
        cursor.execute(sql)
        return "Database NEMO set up"
    except mysql.connector.Error as err:
        return err
# kiểm tra và tạo thử trước 1 database
def create_attendance():
    sql = '''
        CREATE TABLE `attendance`  (
        `AttendanceID` int NOT NULL AUTO_INCREMENT,
        `EmployeeID` int NULL DEFAULT NULL,
        `WorkDays` int NOT NULL,
        `AbsentDays` int NULL DEFAULT 0,
        `LeaveDays` int NULL DEFAULT 0,
        `AttendanceMonth` date NOT NULL,
        `CreatedAt` datetime NULL DEFAULT CURRENT_TIMESTAMP,
        PRIMARY KEY (`AttendanceID`) USING BTREE
        ) ENGINE = InnoDB AUTO_INCREMENT = 1 CHARACTER SET = utf8mb4 COLLATE = utf8mb4_0900_ai_ci ROW_FORMAT = Dynamic;

    '''  
    try:
        cursor.execute(sql)
        conn.commit()
        return 'attendance set up'
    except mysql.connector.Error as err:
        return err
    
def create_accounts():
    sql = '''
        CREATE TABLE accounts (
            user_id INT AUTO_INCREMENT PRIMARY KEY,
            username VARCHAR(250) NOT NULL,
            password VARCHAR(250) NOT NULL,
            email VARCHAR(250) NOT NULL,
            role VARCHAR(150) NOT NULL
        )
    '''
    try:
        cursor.execute(sql)
        return "Accounts set up"
    except mysql.connector.errors as err:
        return err
    
def new_accounts():
    sql = '''
        INSERT INTO accounts (username,password,email,role)
        VALUES ('admin','admin_123','mtranquoc77@gmail.com','administrator')
    '''
    try:
        cursor.execute(sql)
        conn.commit()
        return "new account have been created"
    except mysql.connector.errors as err:
        return err
    
def check_accounts():
    sql = '''SELECT * FROM accounts'''
    try:
        cursor.execute(sql)
        accounts = cursor.fetchall()
        for obj in accounts:
            print(obj[1])
            print(obj[2])
            print(obj[3])
    except mysql.connector.errors as err:
        return err

# Nếu bảng thử đã được tạo, có thể tạo nhiều bảng còn lại ở dưới
def create_table():
    sql = '''

        SET NAMES utf8mb4;
        SET FOREIGN_KEY_CHECKS = 0;

        CREATE TABLE `departments`  (
        `DepartmentID` int NOT NULL,
        `DepartmentName` varchar(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NOT NULL,
        PRIMARY KEY (`DepartmentID`) USING BTREE
        ) ENGINE = InnoDB CHARACTER SET = utf8mb4 COLLATE = utf8mb4_0900_ai_ci ROW_FORMAT = Dynamic;

        CREATE TABLE `employees`  (
        `EmployeeID` int NOT NULL,
        `FullName` varchar(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NOT NULL,
        `DepartmentID` int NULL DEFAULT NULL,
        `PositionID` int NULL DEFAULT NULL,
        `Status` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NULL DEFAULT NULL,
        PRIMARY KEY (`EmployeeID`) USING BTREE
        ) ENGINE = InnoDB CHARACTER SET = utf8mb4 COLLATE = utf8mb4_0900_ai_ci ROW_FORMAT = Dynamic;

        CREATE TABLE `positions`  (
        `PositionID` int NOT NULL,
        `PositionName` varchar(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NOT NULL,
        PRIMARY KEY (`PositionID`) USING BTREE
        ) ENGINE = InnoDB CHARACTER SET = utf8mb4 COLLATE = utf8mb4_0900_ai_ci ROW_FORMAT = Dynamic;

        CREATE TABLE `salaries`  (
        `SalaryID` int NOT NULL AUTO_INCREMENT,
        `EmployeeID` int NULL DEFAULT NULL,
        `SalaryMonth` date NOT NULL,
        `BaseSalary` decimal(12, 2) NOT NULL,
        `Bonus` decimal(12, 2) NULL DEFAULT 0.00,
        `Deductions` decimal(12, 2) NULL DEFAULT 0.00,
        `NetSalary` decimal(12, 2) NOT NULL,
        `CreatedAt` datetime NULL DEFAULT CURRENT_TIMESTAMP,
        PRIMARY KEY (`SalaryID`) USING BTREE
        ) ENGINE = InnoDB AUTO_INCREMENT = 1 CHARACTER SET = utf8mb4 COLLATE = utf8mb4_0900_ai_ci ROW_FORMAT = Dynamic;

        SET FOREIGN_KEY_CHECKS = 1;


    '''
    try:
        cursor.execute(sql)
        # conn.commit()
        return "all table set up"
    except mysql.connector.Error as err:
        return err
    
'''Các bảng CSDL nguyên bản sau khi tạo thành đều cần đến các bảng CSDL trung gian'''
"Mục đích của các bản CSDL để nhằm đảm bảo tính chuẩn hóa CSDL,"
" tính mở rộng cho các bảng, tránh các xung đột và khuyết điểm không cần thiết"

def create_middle_department_pos():
    try:
        sql = '''
        CREATE TABLE DepartmentPositions (
            ID INT PRIMARY KEY IDENTITY,
            DepartmentID INT NOT NULL,
            PositionID INT NOT NULL,
            FOREIGN KEY (DepartmentID) REFERENCES departments(DepartmentID),
            FOREIGN KEY (PositionID) REFERENCES positions(PositionID)
        )
        '''
        cursor.execute(sql)
        return "DeparmentPositions has established"
    except mysql.connector.errors as err:
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
        return "Table Employee has established"
    except mysql.connector.errors as err:
        return f"{err}"

# chạy các hàm ở dưới
if __name__ == '__main__':
    print(check_connection())
    # print(create_attendance())
    # print(create_table())
    # print(create_accounts())
    # print(new_accounts())
    # print(check_accounts())
    # print(create_middle_department_pos())
    print(create_middle_employees_dp_pos())