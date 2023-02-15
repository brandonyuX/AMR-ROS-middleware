var top = 0;

function addNotification(message, type) {
    // var notificationContainer = document.createElement("div");
    // notificationContainer.setAttribute("id", "notificationContainer");
    // notificationContainer.setAttribute("style", "position: fixed; top: 0; left: 0; right: 0; z-index: 10;");
    // document.body.appendChild(notificationContainer);
  
    var notificationContainer = document.getElementById("notificationContainer");

    var notification = document.createElement("div");
    notification.setAttribute("class", "alert alert-" + type + " alert-dismissible fade show");
    notification.setAttribute("role", "alert");
    notification.setAttribute("style", "display: none; top: " + top + "px; height: auto;");
    
    var messageHeading = document.createElement("p");
    messageHeading.setAttribute("class", "m-0");
    messageHeading.innerHTML = message;
    
    var button = document.createElement("button");
    button.setAttribute("type", "button");
    button.setAttribute("class", "btn-close");
    button.setAttribute("data-bs-dismiss", "alert");
    button.setAttribute("aria-label", "Close");
    
    notification.appendChild(messageHeading);
    notification.appendChild(button);
    
    notificationContainer.appendChild(notification);

    top += notification.offsetHeight;

    if(type == "danger"){
        $(notification).slideDown();
    } else {
        $(notification).slideDown(function() {
            setTimeout(function() {
                $(notification).fadeOut();
            }, 3000);
        });
    }
};