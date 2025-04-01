function toggle_reaveal_password(){
    const password_field = document.getElementById("password");
    const icon_reveal = document.getElementById("eyeIcon");

    if (password_field.type === "password"){
        password_field.type = "text";
        icon_reveal.classList.remove("fa-eye");
        icon_reveal.classList.add("fa-eye-slash");
    }
    else{
        password_field.type = "password";
        icon_reveal.classList.remove("fa-eye-slash");
        icon_reveal.classList.add("fa-eye");
    }
}

document.addEventListener("DOMContentLoaded", () => {
    toggle_reaveal_password();
})