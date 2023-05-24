var username = document.getElementById("username");
var contact = document.getElementById("contact");
var email = document.getElementById("email");
var warn = document.getElementById("warn");
var button = document.getElementById("submit");
var password1 = document.getElementById("p1");
var password2 = document.getElementById("p2");

contact.onblur = function () {
  if (contact.value.length == 0) {
    warn.style.display = "none";
  } else if (contact.value.length != 10) {
    warn.style.display = "block";
    warn.innerHTML = "Contact number should be of 10 digits";
  } else {
    warn.style.display = "none";
  }
};
username.oninput = function () {
  var name_pattern = /[a-zA-Z0-9]+$/;
  if (name_pattern.test(username.value) == true) {
    warn.style.display = "none";
  } else {
    warn.style.display = "block";
    warn.innerHTML = "Username should not contain special characters";
  }
};

email.onblur = function () {
  var email_pattern = /^\w+([\.-]?\w+)*@\w+([\.-]?\w+)*(\.\w{2,3})+$/;
  if (email.value.length == 0) {
    return true;
  } else if (email_pattern.test(email.value) == true) {
    warn.style.display = "none";
  } else {
    warn.style.display = "block";
    warn.innerHTML = "Invalid Email Address";
  }
};
password1.onblur = function () {
  var password_pattern =
    /^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]{8,}$/;
  if (password1.value.length == 0) {
    warn.style.display = "none";
  } else if (password_pattern.test(password1.value) != true) {
    warn.style.display = "block";
    warn.innerHTML = "Weak password";
  } else {
    warn.style.display = "none";
  }
};
password2.oninput = function () {
  if (password1.value.length === password2.value.length) {
    if (password1.value === password2.value) {
      warn.style.display = "none";
      return true;
    } else {
      warn.style.display = "block";
      warn.innerHTML = "Passwords Do not match";
    }
  } else {
    warn.innerHTML = "Passwords do not match";
  }
};
