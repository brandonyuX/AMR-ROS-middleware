// Adjust msmsgblock to the center
document.getElementById("msmsgblock").innerHTML = '<div class="h6 py-2 fw-bold" style="text-align: center; margin-bottom: 0px;">Master Scheduler <br /><div id="msmsg"></div></div>'
document.getElementById("msmsgblock").style.position = "relative";
dif = (document.getElementById("userLogout").offsetWidth - document.getElementById("sideToggle").offsetWidth) / 2
document.getElementById("msmsgblock").style.left = dif + "px";
document.getElementById("sideWOBtn").classList.add("active");


const woRadioBtns = document.querySelectorAll('input[type="radio"][name="woRadioBtns"]');
let selectedWOStn = 1;

woRadioBtns.forEach((button) => {
  button.addEventListener('change', (event) => {
    selectedWOStn = event.target.value;
    // console.log('Selected WO station:', selectedWOStn);
    get_wo_table();
  });
});

//Function to pause all stations
function pauseStation(){
  fetch("stations/Pause")
}

//Function to start all stations
function startStation(){
  fetch("stations/Start")
}

//Function to stop all stations
function stopStation(){
  fetch("stations/Stop")
}

//Function to stop all stations
function abortTask(){
  var confirmresult=confirm("This will complete current request and abort task!! Please confirm this action!");
  if (confirmresult==true){
  fetch("task/abort")
  }
}
//Get all data table from flask server
var get_all_table = function getInfo() {
  let myRequest = new Request('/get_list_all');
  fetch(myRequest).then(response => response.json()).then(function (data) {
    // console.log(data);
    var availno = 0;
    var charging='Not Charging';
    var location='Not Specified';
    
    //Build robot information table from array
    var rbtarr = JSON.parse(data['rbtarr']);
    var HTML = "";
    for (let i = 0; i < rbtarr.rbtinfo.length; i++) {
      if(rbtarr.rbtinfo[i].charging == true){
        charging='Charging'
      }else{
        charging='Not Charging'
      }
      if(rbtarr.rbtinfo[i].currloc=="CHR"){
        location='Charging Station'
      }else{
        location=rbtarr.rbtinfo[i].currloc;
      }

      HTML += "<tr><td>" + rbtarr.rbtinfo[i].rid + "</td>";
      HTML += "<td>" + location + "</td>";
      HTML += "<td>" + rbtarr.rbtinfo[i].x + "</td>";
      HTML += "<td>" + rbtarr.rbtinfo[i].y + "</td>";
      HTML += "<td>" + rbtarr.rbtinfo[i].battlvl + "</td>";
      HTML += "<td>" +charging + "</td></tr>";
      
      if (rbtarr.rbtinfo[i].avail == true) {
        availno += 1
      }
    }
    // document.getElementById("curRbtStatus").innerHTML = HTML;

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
      HTML += "<td>" + cusreqarr.cusreqarr[i].priority + "</td>";
      HTML += "<td>" + cusreqarr.cusreqarr[i].status + "</td>";
      HTML += "<td>" + cusreqarr.cusreqarr[i].datetime + "</td></tr>";
    }
    document.getElementById("cusReq").innerHTML = HTML;

    get_wo_table();

    document.getElementById("msmsg").innerHTML = data['msinfo'];
    document.getElementById("numRbtAvail").innerHTML = '<small>Robot Available: ' + availno + '</small>';
    document.getElementById("numProductionTask").innerHTML = "<small>In Queue: " + taskarr.taskinfo.length + '</small>';
    document.getElementById("numCusTsk").innerHTML = "<small>In Queue: " + custskarr.custskarr.length + '</small>';
    document.getElementById("numCusReq").innerHTML = "<small>In Queue: " + cusreqarr.cusreqarr.length + '</small>';
  });
}

//Get WO data table from flask server
var get_wo_table = function getWO() {
  let myRequest = new Request('/get_wo?WOStn=' + selectedWOStn);
  fetch(myRequest).then(response => response.json()).then(function (data) {
    //Build WO table
    var woarr = JSON.parse(data['woperstnarr']);
    var HTML = "";
    for (let i = 0; i < woarr.woperstnarr.length; i++) {
      HTML += "<tr><td>" +   woarr.woperstnarr[i].state + "</td>";
      HTML += "<td>" +      woarr.woperstnarr[i].batchNum + "</td>";
      HTML += "<td>" +      woarr.woperstnarr[i].woNum + "</td>";
      HTML += "<td>" +      woarr.woperstnarr[i].manufactureDate + "</td>";
      HTML += "<td>" +      woarr.woperstnarr[i].fnpDate + "</td>";
      HTML += "<td>" +      woarr.woperstnarr[i].initSerialNum + "</td>";
      HTML += "<td>" +      woarr.woperstnarr[i].requireQty + "</td>";
      HTML += "<td>" +      woarr.woperstnarr[i].processedQty + "</td>";
      HTML += "<td>" +      woarr.woperstnarr[i].startTime + "</td>";
      HTML += "<td>" +      woarr.woperstnarr[i].endTime + "</td>";
      HTML += "<td>" +      woarr.woperstnarr[i].fillVol + "</td>";
      HTML += "<td>" +      woarr.woperstnarr[i].targetTor + "</td>";
      HTML += "<td>" +      woarr.woperstnarr[i].status + "</td>";
      HTML += "<td>" +      woarr.woperstnarr[i].orderNum + "</td>";
      HTML += "<td>" +      woarr.woperstnarr[i].expDate + "</td></tr>";
    }
    document.getElementById("WO").innerHTML = HTML;
    document.getElementById("numWO").innerHTML = "<small>In Queue: " + woarr.woperstnarr.length + '</small>';

    function hideColumn(colIndex) {
      var table = document.querySelector("#woTable");
      table.getElementsByTagName('thead')[0].getElementsByTagName('th')[colIndex-1].style.display = "none";
      var rows = table.getElementsByTagName('tbody')[0].getElementsByTagName('tr');
      for (var i = 0; i < rows.length; i++) {
        rows[i].getElementsByTagName('td')[colIndex-1].style.display = "none";
      }
    }


    function showColumn(colIndex) {
			var table = document.querySelector("#woTable");
			table.getElementsByTagName('thead')[0].getElementsByTagName('th')[colIndex-1].style.display = "table-cell";
			var rows = table.getElementsByTagName('tbody')[0].getElementsByTagName('tr');
			for (var i = 0; i < rows.length; i++) {
				rows[i].getElementsByTagName('td')[colIndex-1].style.display = "table-cell";
			}
		}

    // // Get the table header row and all cells in it
    // var headerRow = document.querySelector("#woTable thead tr");
    // var cells = headerRow.cells;

    // Hide columns
    if(selectedWOStn == 1){
      showColumn(14);
      hideColumn(15);
    }
    else if(selectedWOStn == 4){
      hideColumn(14);
      showColumn(15);
    }
    else{
      hideColumn(14);
      hideColumn(15);
    }
  });
}


setInterval(get_all_table, 5000);
get_all_table();