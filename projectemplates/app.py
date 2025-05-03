from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
import config  # Import file config.py

app = Flask(__name__)

app.config["SQLALCHEMY_BINDS"] = {
    "default": config.SQL_SERVER_CONN,  # Kết nối SQL Server
    "mysql": config.MYSQL_CONN,  # Kết nối MySQL
}

db = SQLAlchemy(app)

class HoSoNhanVienSQL(db.Model):
    __tablename__ = "HoSoNhanVien"
    __bind_key__ = "default" 

    MaNV = db.Column(db.Integer, primary_key=True, autoincrement=True)
    HoTen = db.Column(db.String(100), nullable=False)
    NgaySinh = db.Column(db.Date)
    GioiTinh = db.Column(db.String(10))
    DiaChi = db.Column(db.String(255))
    SoDienThoai = db.Column(db.String(15))
    Email = db.Column(db.String(100))
    NgayVaoLam = db.Column(db.Date)

class HoSoNhanVienMySQL(db.Model):
    __tablename__ = "HoSoNhanVien"
    __bind_key__ = "mysql"

    MaNV = db.Column(db.Integer, primary_key=True, autoincrement=True)
    HoTen = db.Column(db.String(100), nullable=False)
    NgaySinh = db.Column(db.Date)
    GioiTinh = db.Column(db.String(10))
    SoDienThoai = db.Column(db.String(15))
    Email = db.Column(db.String(100))
    NgayVaoLam = db.Column(db.Date)


class LuongNhanVien(db.Model):
    __tablename__ = "LuongNhanVien"
    __bind_key__ = "mysql"

    MaLuong = db.Column(db.Integer, primary_key=True, autoincrement=True)
    MaNV = db.Column(db.Integer, db.ForeignKey("HoSoNhanVien.MaNV"))
    ThangNam = db.Column(db.Date)
    LuongCoBan = db.Column(db.Float)
    PhuCap = db.Column(db.Float)
    Thuong = db.Column(db.Float)
    KhauTru = db.Column(db.Float)
    LuongThucNhan = db.Column(db.Float)


# Trang chủ
@app.route("/")
def index():
    return render_template("index.html")


# Trang thêm nhân viên
@app.route("/them-nhan-vien", methods=["GET", "POST"])
def them_nhan_vien():
    if request.method == "POST":
        ho_ten = request.form["ho_ten"]
        ngay_sinh = request.form["ngay_sinh"]
        gioi_tinh = request.form["gioi_tinh"]
        dia_chi = request.form["dia_chi"]
        so_dien_thoai = request.form["so_dien_thoai"]
        email = request.form["email"]
        ngay_vao_lam = request.form["ngay_vao_lam"]

        # Thêm vào SQL Server
        nhan_vien_sql = HoSoNhanVienSQL(
            HoTen=ho_ten,
            NgaySinh=ngay_sinh,
            GioiTinh=gioi_tinh,
            DiaChi=dia_chi,
            SoDienThoai=so_dien_thoai,
            Email=email,
            NgayVaoLam=ngay_vao_lam,
        )
        db.session.add(nhan_vien_sql)
        db.session.commit()

        # Thêm vào MySQL
        nhan_vien_mysql = HoSoNhanVienMySQL(
            MaNV=nhan_vien_sql.MaNV,  # Lấy mã nhân viên từ SQL Server
            HoTen=ho_ten,
            NgaySinh=ngay_sinh,
            GioiTinh=gioi_tinh,
            SoDienThoai=so_dien_thoai,
            Email=email,
            NgayVaoLam=ngay_vao_lam,
        )
        db.session.add(nhan_vien_mysql)
        db.session.commit()

        return redirect(url_for("index"))

    return render_template("them_nhan_vien.html")

# Trang in bảng lương
@app.route("/in-bang-luong")
def in_bang_luong():
    # Lấy danh sách nhân viên từ SQL Server
    nhan_viens = HoSoNhanVienSQL.query.all()
    print("Danh sách nhân viên:", nhan_viens)  # Debug

    # Lấy bảng lương từ MySQL
    luong_nhan_vien = LuongNhanVien.query.all()
    print("Danh sách lương:", luong_nhan_vien)  # Debug

    # Ghép dữ liệu bằng Python thay vì JOIN SQLAlchemy
    data = []
    for nv in nhan_viens:
        luong = next((l for l in luong_nhan_vien if l.MaNV == nv.MaNV), None)
        if luong:
            data.append((nv, luong))

    print("Dữ liệu sau khi ghép:", data)  # Debug xem có dữ liệu không
    return render_template("in_bang_luong.html", nhan_viens=data)

# IN DANH SÁCH NHÂN VIÊN
@app.route("/in-danh-sach")
def in_danh_sach():
    # Lấy danh sách nhân viên từ SQL Server
    nhan_viens_sql = HoSoNhanVienSQL.query.all()
    # Lấy danh sách nhân viên từ MySQL (bao gồm cả PhongBan và ChucVu)
    nhan_viens_mysql = HoSoNhanVienMySQL.query.all()

    # Chuyển dữ liệu MySQL thành dictionary để dễ tìm kiếm theo MaNV
    mysql_dict = {nv.MaNV: nv for nv in nhan_viens_mysql}

    # Danh sách nhân viên kết hợp
    merged_data = []

    for nv_sql in nhan_viens_sql:
        if nv_sql.MaNV in mysql_dict:
            nv_mysql = mysql_dict[nv_sql.MaNV]
            merged_data.append({
                "MaNV": nv_sql.MaNV,
                "HoTen": nv_sql.HoTen,
                "NgaySinh": nv_sql.NgaySinh,
                "GioiTinh": nv_sql.GioiTinh,
                "DiaChi": nv_sql.DiaChi,
                "SoDienThoai": nv_sql.SoDienThoai,
                "Email": nv_sql.Email,
                "NgayVaoLam": nv_sql.NgayVaoLam,
                "PhongBan": getattr(nv_mysql, "PhongBan", "N/A"),  # Lấy từ MySQL nếu có
                "ChucVu": getattr(nv_mysql, "ChucVu", "N/A")  # Lấy từ MySQL nếu có
            })
            del mysql_dict[nv_sql.MaNV]  # Xóa để tránh bị lặp lại
        else:
            merged_data.append({
                "MaNV": nv_sql.MaNV,
                "HoTen": nv_sql.HoTen,
                "NgaySinh": nv_sql.NgaySinh,
                "GioiTinh": nv_sql.GioiTinh,
                "DiaChi": nv_sql.DiaChi,
                "SoDienThoai": nv_sql.SoDienThoai,
                "Email": nv_sql.Email,
                "NgayVaoLam": nv_sql.NgayVaoLam,
                "PhongBan": "N/A",  # Không có trong MySQL
                "ChucVu": "N/A"  # Không có trong MySQL
            })

    # Thêm các nhân viên chỉ có trong MySQL (sau khi loại bỏ trùng lặp)
    for nv_mysql in mysql_dict.values():
        merged_data.append({
            "MaNV": nv_mysql.MaNV,
            "HoTen": nv_mysql.HoTen,
            "NgaySinh": nv_mysql.NgaySinh,
            "GioiTinh": nv_mysql.GioiTinh,
            "DiaChi": getattr(nv_mysql, "DiaChi", "N/A"),
            "SoDienThoai": nv_mysql.SoDienThoai,
            "Email": nv_mysql.Email,
            "NgayVaoLam": nv_mysql.NgayVaoLam,
            "PhongBan": getattr(nv_mysql, "PhongBan", "N/A"),
            "ChucVu": getattr(nv_mysql, "ChucVu", "N/A")
        })

    return render_template("in_danh_sach.html", nhan_viens=merged_data)

#CẬP NHẬT HỒ SƠ NHÂN VIÊN
@app.route('/cap-nhat-nhan-vien/<int:manv>', methods=["GET", "POST"])
def cap_nhat_nhan_vien(manv):
    # Truy vấn thông tin nhân viên từ SQL Server
    nhan_viens_sql = HoSoNhanVienSQL.query.get(manv)
    # Truy vấn thông tin nhân viên từ MySQL
    nhan_viens_mysql = HoSoNhanVienMySQL.query.get(manv)
    
    if not nhan_viens_sql and not nhan_viens_mysql:
        return "Không tìm thấy nhân viên", 404 # Trả về mã lỗi nếu không có dữ liệu
    
    if request.method == "POST":
        # Lấy dữ liệu từ form nhập liệu
        ho_ten = request.form.get["ho_ten"]
        ngay_sinh = request.form.get["ngay_sinh"]   
        gioi_tinh = request.form.get["gioi_tinh"]
        dia_chi = request.form.get["dia_chi"]
        so_dien_thoai = request.form.get["so_dien_thoai"]
        email = request.form.get["email"]
        ngay_vao_lam = request.form.get["ngay_vao_lam"]
        phong_ban = request.form.get["phong_ban"]
        chuc_vu = request.form.get["chuc_vu"]
        
        # Cập nhật dữ liệu trong SQL Server (nếu tồn tại)
        if nhan_viens_sql:
            nhan_viens_sql.HoTen = ho_ten
            nhan_viens_sql.NgaySinh = ngay_sinh
            nhan_viens_sql.GioiTinh = gioi_tinh
            nhan_viens_sql.DiaChi = dia_chi
            nhan_viens_sql.SoDienThoai = so_dien_thoai
            nhan_viens_sql.Email = email
            nhan_viens_sql.NgayVaoLam = ngay_vao_lam
            db.session.commit()
        
        # Cập nhật dữ liệu trong MySQL (nếu tồn tại)
        if nhan_viens_mysql:
            nhan_viens_mysql.HoTen = ho_ten
            nhan_viens_mysql.NgaySinh = ngay_sinh
            nhan_viens_mysql.GioiTinh = gioi_tinh
            nhan_viens_mysql.DiaChi = dia_chi
            nhan_viens_mysql.SoDienThoai = so_dien_thoai
            nhan_viens_mysql.Email = email
            nhan_viens_mysql.NgayVaoLam = ngay_vao_lam
            nhan_viens_mysql.PhongBan = phong_ban
            nhan_viens_mysql.ChucVu = chuc_vu
            
            db.session.commit()
            
        return redirect(url_for("in_danh_sach")) # Quay về trang chủ sau khi cập nhật
    
    return render_template("cap_nhat_nhan_vien.html", nv_sql=nhan_viens_sql, nv_mysql=nhan_viens_mysql)
    
    
#XÓA NHÂN VIÊN
@app.route("/xoa-nhan-vien/<int:manv>", methods=["POST"])
def xoa_nhan_vien(manv):
    # Kiểm tra nếu nhân viên có bảng lương trong MySQL
    luong_nhan_vien = LuongNhanVien.query.filter_by(MaNV=manv).first()
    if luong_nhan_vien:
        return "Không thể xóa! Nhân viên có dữ liệu trong bảng lương.", 400
    
    # Xóa nhân viên từ SQL Server
    nhan_vien_sql = HoSoNhanVienSQL.query.get(manv)
    if nhan_vien_sql:
        db.session.delete(nhan_vien_sql)
        db.session.commit()
        
    # Xóa nhân viên từ MySQL
    nhan_vien_mysql = HoSoNhanVienMySQL.query.get(manv)
    if nhan_vien_mysql:
        db.session.delete(nhan_vien_mysql)
        db.session.commit()
        
    return redirect(url_for("index"))



if __name__ == "__main__":
    app.run(debug=True)
