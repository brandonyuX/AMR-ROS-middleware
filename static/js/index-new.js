// Adjust msmsgblock to the center
document.getElementById("msmsgblock").innerHTML = '<div class="h6 py-2 fw-bold" style="text-align: center; margin-bottom: 0px;">Master Scheduler <br /><div id="msmsg"></div></div>'
document.getElementById("msmsgblock").style.position = "relative";
dif = (document.getElementById("userLogout").offsetWidth - document.getElementById("sideToggle").offsetWidth) / 2
document.getElementById("msmsgblock").style.left = dif + "px";
document.getElementById("sideDbBtn").classList.add("active");

//Get data table from flask server
var get_table = function getInfo() {
  let myRequest = new Request('/get_list');
  fetch(myRequest).then(response => response.json()).then(function (data) {
    // console.log(data);
    var availno = 0;

    //Build robot information table from array
    var rbtarr = JSON.parse(data['rbtarr']);
    var HTML = "";
    for (let i = 0; i < rbtarr.rbtinfo.length; i++) {
      HTML += "<tr><td>" + rbtarr.rbtinfo[i].rid + "</td>";
      HTML += "<td>" + rbtarr.rbtinfo[i].currloc + "</td>";
      HTML += "<td>" + rbtarr.rbtinfo[i].x + "</td>";
      HTML += "<td>" + rbtarr.rbtinfo[i].y + "</td>";
      HTML += "<td>" + rbtarr.rbtinfo[i].r + "</td>";
      HTML += "<td>" + rbtarr.rbtinfo[i].msg + "</td></tr>";
      if (rbtarr.rbtinfo[i].avail == true) {
        availno += 1
      }
    }
    document.getElementById("curRbtStatus").innerHTML = HTML;

    //Build task information table from array
    var taskarr = JSON.parse(data['taskarr'])
    var HTML = "";
    for (let i = 0; i < taskarr.taskinfo.length; i++) {
      HTML += "<tr><td>" + taskarr.taskinfo[i].tid + "</td>";
      HTML += "<td>" + taskarr.taskinfo[i].rid + "</td>";
      HTML += "<td>" + taskarr.taskinfo[i].reqid + "</td>";
      HTML += "<td>" + taskarr.taskinfo[i].currstep + "</td>";
      HTML += "<td>" + taskarr.taskinfo[i].endstep + "</td>";
      HTML += "<td>" + taskarr.taskinfo[i].completed + "</td></tr>";
    }
    document.getElementById("curTask").innerHTML = HTML;

    //Build request information table from array
    var reqarr = JSON.parse(data['reqarr'])
    var HTML = "";
    for (let i = 0; i < reqarr.reqinfo.length; i++) {
      HTML += "<tr><td>" + reqarr.reqinfo[i].plcid + "</td>";
      HTML += "<td>" + reqarr.reqinfo[i].reqid + "</td>";
      HTML += "<td>" + reqarr.reqinfo[i].destloc + "</td>";
      HTML += "<td>" + reqarr.reqinfo[i].tskmodno + "</td>";
      HTML += "<td>" + reqarr.reqinfo[i].status + "</td></tr>";
    }
    document.getElementById("curCustomRequest").innerHTML = HTML;

    document.getElementById("msmsg").innerHTML = data['msinfo'];
    document.getElementById("numRbtAvail").innerHTML = '<small>Robot Available: ' + availno + '</small>';
    document.getElementById("numCurTask").innerHTML = "<small>In Queue: " + taskarr.taskinfo.length + '</small>';
    document.getElementById("numPLCReq").innerHTML = "<small>In Queue: " + reqarr.reqinfo.length + '</small>';
  });
}

setInterval(get_table, 3000);
get_table();