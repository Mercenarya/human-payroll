const { json } = require("body-parser");


// tính lương ròng, lương hàng tháng
function salary_caculate(event){
    if (event){
        event.preventDefault();
        // không tải lại trang 
    }
    // Phần dữ liệu đầu vào
    const baseSalary = document.getElementById("basesalaries");
    const deduction = document.getElementById("deduction");
    const bonus = document.getElementById("bonus");

    // phần lấy kết quả
    const monthSalary = document.getElementById("monthsalary");
    const netsalaries = document.getElementById("netsalaries");
    // lấy dữ liệu được hiển thị nhập giao diện người dùng
    
    // kiểm tra giá trị đầu vào của lương bổng
    if (baseSalary.value == "" || bonus,value == ""){
        alert("Base value or Bonus must be added first")
    }
    // trả về kết quả của 2 dữ liệu
    const summary_month_salary = parseFloat(baseSalary.value) + parseFloat(bonus.value);
    const summary_net_salary = summary_month_salary - parseFloat(deduction.value);
    
    // hiển thị kết quả sau khi ép kiểu Float
    monthSalary.value = parseFloat(summary_month_salary);
    netsalaries.value = parseFloat(summary_net_salary);
    
    
    // callback
    output_reveal();
}

// kiểm tra giá trị output của 2 đợn vị lương
function output_reveal(){
    const monthSalary = document.getElementById("monthsalary");
    const netsalaries = document.getElementById("netsalaries");
    // trả về kết quả 
    return{
        "Salary-per-month":monthSalary,
        "net-Salary":netsalaries
    }
    
}

function clear_data(event){
    if(event){
        event.preventDefault();
        // Lương bổng nhân viên
    }
    const form = document.getElementById("emp-mng");
    // truy xuất tất cả các thuộc tính ở trong form
    form.querySelectorAll("input").forEach(
        element => element.value = ""
        // trả về kết quả rỗng
    );
    alert("Information have been removed");

}


