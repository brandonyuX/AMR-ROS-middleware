// var topSpace = 0;

document.getElementById('registration_form').addEventListener('submit', function (event) {
    event.preventDefault();
    //Code to handle the form submission
    // console.log('Registration Event Listener Triggered');
    const username = document.getElementById("username").value;
    const password = document.getElementById("password").value;
    const confirmPassword = document.getElementById("confirmPassword").value;
    const xhr = new XMLHttpRequest();
    xhr.open("POST", "/register", true);
    xhr.setRequestHeader("Content-Type", "application/x-www-form-urlencoded");
    xhr.onreadystatechange = function () {
        if (this.readyState === XMLHttpRequest.DONE && this.status === 200) {
            // console.log(this.getAllResponseHeaders());
            // console.log(this.responseURL);
            console.log(this.status);
            if (this.responseText == 'Account successfully registered!') {
                addNotification(this.responseText, "success");
                window.location = "http://127.0.0.1:5000/login?msg=sc";
                // var form = document.createElement("form");
                // form.method = "POST";
                // form.action = "http://127.0.0.1:5000/login";

                // var input = document.createElement("input");
                // input.type = "hidden";
                // input.name = "msg";
                // input.value = "sc";

                // form.appendChild(input);
                // document.body.appendChild(form);
                // form.submit();
            } else {
                addNotification(this.responseText, "warning");
            }
        }
    };
    xhr.send(`username=${username}&password=${password}&confirmPassword=${confirmPassword}`);
    // console.log('Loaded register.js.');
});

// function addNotification(message, type) {
//     // var notificationContainer = document.createElement("div");
//     // notificationContainer.setAttribute("id", "notificationContainer");
//     // notificationContainer.setAttribute("style", "position: fixed; top: 0; left: 0; right: 0;");
//     // document.body.appendChild(notificationContainer);
  
//     var notificationContainer = document.getElementById("notificationContainer");

//     var notification = document.createElement("div");
//     notification.setAttribute("class", "alert alert-" + type + " alert-dismissible fade show");
//     notification.setAttribute("role", "alert");
//     notification.setAttribute("style", "display: none; top: " + topSpace + "px;");
//     notification.innerHTML = message;
  
//     var button = document.createElement("button");
//     button.setAttribute("type", "button");
//     button.setAttribute("class", "close");
//     button.setAttribute("data-dismiss", "alert");
//     button.setAttribute("aria-label", "Close");
  
//     var span = document.createElement("span");
//     span.setAttribute("aria-hidden", "true");
//     span.innerHTML = "&times;";
//     button.appendChild(span);
  
//     notification.appendChild(button);
  
//     notificationContainer.appendChild(notification);

//     topSpace += notification.offsetHeight;

//     console.log(topSpace);
  
//     $(notification).slideDown();
//   };