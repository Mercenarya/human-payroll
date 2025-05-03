import mysql.connector

db = mysql.connector.connect(
    host = '127.0.0.1',
    user = 'root',
    password = 'Minh_17102004',
    database = 'payroll_baitap'
)

cursor = db.cursor()

def _test_connection_():
    try:
        if db.is_connected():
            return f'{db._host} is connected'
        else:
            return f"{db._host} is disconnected"
    except Exception as error:
        return error

def _Create_databases():
    sql = '''
        CREATE DATABASE IF NOT EXISTS payroll_baitap;
    '''
    try:
        cursor.execute(sql)
        return 'payroll set up '
    except mysql.connector.errors.Error as err:
        return err
def _create_hsnv():
    sql = '''
        CREATE TABLE `hosonhanvien` (
            `MaNV` int NOT NULL AUTO_INCREMENT,
            `HoTen` varchar(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci
            NULL DEFAULT NULL,
            `NgaySinh` date NULL DEFAULT NULL,
            `GioiTinh` varchar(10) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci
            NULL DEFAULT NULL,
            `SoDienThoai` varchar(15) CHARACTER SET utf8mb4 COLLATE
            utf8mb4_0900_ai_ci NULL DEFAULT NULL,
            `Email` varchar(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci
            NULL DEFAULT NULL,
            `NgayVaoLam` date NULL DEFAULT NULL,
            PRIMARY KEY (`MaNV`) USING BTREE
        ) ENGINE = InnoDB AUTO_INCREMENT = 22 CHARACTER SET = utf8mb4
        COLLATE = utf8mb4_0900_ai_ci ROW_FORMAT = Dynamic
    '''
    try:
        cursor.execute(sql)
        return 'hsnv set up table'
    except mysql.connector.errors.Error as err:
        return err
    
def _create_lnv():
    sql = '''
        CREATE TABLE `luongnhanvien` (
            `MaLuong` int NOT NULL AUTO_INCREMENT,
            `MaNV` int NULL DEFAULT NULL,
            `ThangNam` date NULL DEFAULT NULL,
            `LuongCoBan` decimal(10, 2) NULL DEFAULT NULL,
            `PhuCap` decimal(10, 2) NULL DEFAULT NULL,
            `Thuong` decimal(10, 2) NULL DEFAULT NULL,
            `KhauTru` decimal(10, 2) NULL DEFAULT NULL,
            `LuongThucNhan` decimal(10, 2) NULL DEFAULT NULL,
            PRIMARY KEY (`MaLuong`) USING BTREE,
            INDEX `MaNV`(`MaNV` ASC) USING BTREE,
            CONSTRAINT `luongnhanvien_ibfk_1` FOREIGN KEY (`MaNV`) REFERENCES
            `hosonhanvien` (`MaNV`) ON DELETE RESTRICT ON UPDATE RESTRICT
        ) ENGINE = InnoDB AUTO_INCREMENT = 41 CHARACTER SET = utf8mb4
        COLLATE = utf8mb4_0900_ai_ci ROW_FORMAT = Dynamic;
    '''
    try:
        cursor.execute(sql)
        return 'lnv is created'
    except mysql.connector.errors.Error as err:
        return err
def create_records():
    sql = '''
      SET FOREIGN_KEY_CHECKS = 1;
    '''
    try:
        cursor.execute(sql)
        db.commit()
        return 'records appended'
    except mysql.connector.errors.Error as err:
        return err
    
def check_records():
    sql = '''
        SELECT * FROM hsnv
    '''
    try:
        cursor.execute(sql)
        
    except mysql.connector.errors.Error as err:
        return err

if __name__ == "__main__":
    print(_test_connection_())
    # print(_Create_databases())
    # print(_create_hsnv())
    print(create_records())
    # print(_create_lnv())