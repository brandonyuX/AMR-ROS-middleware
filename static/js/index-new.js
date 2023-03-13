// Adjust msmsgblock to the center
document.getElementById("msmsgblock").innerHTML = '<div class="h6 py-2 fw-bold" style="text-align: center; margin-bottom: 0px;">Master Scheduler <br /><div id="msmsg"></div></div>'
document.getElementById("msmsgblock").style.position = "relative";
dif = (document.getElementById("userLogout").offsetWidth - document.getElementById("sideToggle").offsetWidth) / 2
document.getElementById("msmsgblock").style.left = dif + "px";
document.getElementById("sideDbBtn").classList.add("active");

//Get data table from flask server
var get_table = function getInfo() {
  // var stnRadioBtn = document.getElementsByName("stnRadioBtn");
  // var checkedBtn;
  // console.log(stnRadioBtn.length);
  // for (var i = 0; i < stnRadioBtn.length; i++) {
  //   if (stnRadioBtn[i].checked) {
  //     checkedBtn = stnRadioBtn[i];
  //     break;
  //   }
  // }
  // var WOSelected = document.querySelector(checkedBtn.id).textContent;
  // console.log(WOSelected);
  let WOStn = 1;  
  let myRequest = new Request('/get_list?WOStn=' + WOStn);
  fetch(myRequest).then(response => response.json()).then(function (data) {
    // console.log(data);
    var availno = 0;
    var charging='Not Charging';
   
    //Build robot information table from array
    var rbtarr = JSON.parse(data['rbtarr']);
    var HTML = "";
    for (let i = 0; i < rbtarr.rbtinfo.length; i++) {
      if(rbtarr.rbtinfo[i].charging == true){
        charging='Charging'
      }else{
        charging='Not Charging'
      }
      HTML += "<tr><td>" + rbtarr.rbtinfo[i].rid + "</td>";
      HTML += "<td>" + rbtarr.rbtinfo[i].currloc + "</td>";
      HTML += "<td>" + rbtarr.rbtinfo[i].x + "</td>";
      HTML += "<td>" + rbtarr.rbtinfo[i].y + "</td>";
      HTML += "<td>" + rbtarr.rbtinfo[i].battlvl + "</td>";
      HTML += "<td>" +charging + "</td></tr>";
      
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
    document.getElementById("productionTask").innerHTML = HTML;

    //Build request information table from array
    var custskarr = JSON.parse(data['custskarr'])
    var HTML = "";
    for (let i = 0; i < custskarr.custskarr.length; i++) {
      HTML += "<tr><td>" + custskarr.custskarr[i].tid + "</td>";
      HTML += "<td>" + custskarr.custskarr[i].rid + "</td>";
      HTML += "<td>" + custskarr.custskarr[i].reqid + "</td>";
      HTML += "<td>" + custskarr.custskarr[i].destloc + "</td>";
      HTML += "<td>" + custskarr.custskarr[i].hsmsg + "</td>";
      HTML += "<td>" + custskarr.custskarr[i].tskmodno + "</td>";
      HTML += "<td>" + custskarr.custskarr[i].completed + "</td></tr>";
    }
    document.getElementById("cusTsk").innerHTML = HTML;


    //Build custom request table
    var cusreqarr = JSON.parse(data['cusreqarr']);
    var HTML = "";
    for (let i = 0; i < cusreqarr.cusreqarr.length; i++) {
      HTML += "<tr><td>" + cusreqarr.cusreqarr[i].cid + "</td>";
      HTML += "<td>" + cusreqarr.cusreqarr[i].reqid + "</td>";
      HTML += "<td>" + cusreqarr.cusreqarr[i].dest + "</td>";
      HTML += "<td>" + cusreqarr.cusreqarr[i].priority + "</td>";
      HTML += "<td>" + cusreqarr.cusreqarr[i].status + "</td>";
      HTML += "<td>" + cusreqarr.cusreqarr[i].datetime + "</td></tr>";
    }
    document.getElementById("cusReq").innerHTML = HTML;

    //Build WO table


    var woarr = JSON.parse(data['woperstnarr']);
    var HTML = "";
    for (let i = 0; i < woarr.woperstnarr.length; i++) {
      HTML += "<tr><td>" +  woarr.woperstnarr[i].woid + "</td>";
      HTML += "<td>" +      woarr.woperstnarr[i].batchNum + "</td>";
      HTML += "<td>" +      woarr.woperstnarr[i].woNum + "</td>";
      HTML += "<td>" +      woarr.woperstnarr[i].manufactureDate + "</td>";
      HTML += "<td>" +      woarr.woperstnarr[i].fnpDate + "</td>";
      HTML += "<td>" +  woarr.woperstnarr[i].initSerialNum + "</td>";
      HTML += "<td>" +      woarr.woperstnarr[i].requireQty + "</td>";
      HTML += "<td>" +      woarr.woperstnarr[i].processedQty + "</td>";
      HTML += "<td>" +      woarr.woperstnarr[i].startTime + "</td>";
      HTML += "<td>" +      woarr.woperstnarr[i].endTime + "</td>";
      HTML += "<td>" +  woarr.woperstnarr[i].status + "</td>";
      HTML += "<td>" +      woarr.woperstnarr[i].fillVol + "</td>";
      HTML += "<td>" +      woarr.woperstnarr[i].targetTor + "</td>";
      HTML += "<td>" +      woarr.woperstnarr[i].orderNum + "</td></tr>";
    }
    document.getElementById("WO").innerHTML = HTML;
    

    document.getElementById("msmsg").innerHTML = data['msinfo'];
    document.getElementById("numRbtAvail").innerHTML = '<small>Robot Available: ' + availno + '</small>';
    document.getElementById("numProductionTask").innerHTML = "<small>In Queue: " + taskarr.taskinfo.length + '</small>';
    document.getElementById("numCusTsk").innerHTML = "<small>In Queue: " + custskarr.custskarr.length + '</small>';
    document.getElementById("numCusReq").innerHTML = "<small>In Queue: " + cusreqarr.cusreqarr.length + '</small>';
    document.getElementById("numWO").innerHTML = "<small>In Queue: " + woarr.woperstnarr.length + '</small>';
  });
}

setInterval(get_table, 3000);
get_table();