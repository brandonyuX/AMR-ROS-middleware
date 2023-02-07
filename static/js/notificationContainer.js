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
    notification.setAttribute("style", "display: none; top: " + top + "px;");
    notification.innerHTML = message;
  
    var button = document.createElement("button");
    button.setAttribute("type", "button");
    button.setAttribute("class", "close");
    button.setAttribute("data-dismiss", "alert");
    button.setAttribute("aria-label", "Close");
  
    var span = document.createElement("span");
    span.setAttribute("aria-hidden", "true");
    span.innerHTML = "&times;";
    button.appendChild(span);
  
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