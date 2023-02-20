document.getElementById("msmsgblock").innerHTML = '<div class="h6 py-2 fw-bold" style="text-align: center; margin-bottom: 0px;">Create Task Model</div>'
// Adjust msmsgblock to the center
document.getElementById("msmsgblock").style.position = "relative";
dif = (document.getElementById("userLogout").offsetWidth - document.getElementById("sideToggle").offsetWidth) / 2
document.getElementById("msmsgblock").style.left = dif + "px";
//Set sideTskModelBtn and sideQueryBtn active
document.getElementById("sideTskModelBtn").classList.add("active");
document.getElementById("sideCreateBtn").classList.add("active");

var radios = document.querySelectorAll('[name=gridRadios]');
  Array.from(radios).forEach(function (r) {
    r.addEventListener('click', function () {
      var cmdtxt = document.getElementById('custCmd');
      if (this.id == 'gridRadios4')
        cmdtxt.removeAttribute('disabled');
      else
        cmdtxt.setAttribute('disabled', 'disabled');
    });
  });

  