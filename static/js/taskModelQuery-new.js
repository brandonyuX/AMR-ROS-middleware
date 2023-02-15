document.getElementById("msmsgblock").innerHTML = '<div class="h6 py-2 fw-bold" style="text-align: center; margin-bottom: 0px;">Query Task Model</div>'
// Adjust msmsgblock to the center
document.getElementById("msmsgblock").style.position = "relative";
dif = (document.getElementById("userLogout").offsetWidth - document.getElementById("sideToggle").offsetWidth) / 2
document.getElementById("msmsgblock").style.left = dif + "px";
//Set sideTskModelBtn and sideQueryBtn active
document.getElementById("sideTskModelBtn").classList.add("active");
document.getElementById("sideQueryBtn").classList.add("active");