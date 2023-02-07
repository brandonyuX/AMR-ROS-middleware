document.getElementById('login_form').addEventListener('submit', function (event) {
    event.preventDefault();
    //Code to handle the form submission
    console.log('Submit Event Listener Triggered');
    const username = document.getElementById("username").value;
    const password = document.getElementById("password").value;
    const xhr = new XMLHttpRequest();
    xhr.open("POST", "/login", true);
    xhr.setRequestHeader("Content-Type", "application/x-www-form-urlencoded");
    xhr.onreadystatechange = function () {
        if (this.readyState === XMLHttpRequest.DONE && this.status === 200) {
            // console.log(this.getAllResponseHeaders());
            // console.log(this.responseURL);
            console.log(this.status);
            if (this.responseURL == "http://127.0.0.1:5000/"){
                window.location = xhr.responseURL;
            } else {
                addNotification(this.responseText, "warning");
            }
        }
    };
    xhr.send(`username=${username}&password=${password}`);
    // console.log('Loaded login.js.');
});