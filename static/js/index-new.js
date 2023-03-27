// Adjust msmsgblock to the center
document.getElementById("msmsgblock").innerHTML = '<div class="h6 py-2 fw-bold" style="text-align: center; margin-bottom: 0px;">Master Scheduler <br /><div id="msmsg"></div></div>'
document.getElementById("msmsgblock").style.position = "relative";
dif = (document.getElementById("userLogout").offsetWidth - document.getElementById("sideToggle").offsetWidth) / 2
document.getElementById("msmsgblock").style.left = dif + "px";
document.getElementById("sideDbBtn").classList.add("active");


const woRadioBtns = document.querySelectorAll('input[type="radio"][name="woRadioBtns"]');
let selectedWOStn = 1;

woRadioBtns.forEach((button) => {
  button.addEventListener('change', (event) => {
    selectedWOStn = event.target.value;
    // console.log('Selected WO station:', selectedWOStn);
    get_wo_table();
  });
});

//Get all data table from flask server
var get_all_table = function getInfo() {
  let myRequest = new Request('/get_list');
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
      HTML += "<td>" +rbtarr.rbtinfo[i].msg + "</td></tr>";
      
      if (rbtarr.rbtinfo[i].avail == true) {
        availno += 1
      }
    }
    document.getElementById("curRbtStatus").innerHTML = HTML;

    //Build Station State
    var HTML = "";
    HTML += "<tr><td>" + data['stn1state'] + "</td>";
    HTML += "<td>" + data['stn2state'] + "</td>";
    HTML += "<td>" + data['stn3state'] + "</td>";
    HTML += "<td>" + data['stn4state'] + "</td>";
    HTML += "<td>" + data['stn5state'] + "</td>";
    HTML += "<td>" +data['stn6state'] + "</td></tr>";
    document.getElementById("curStnState").innerHTML = HTML;

    //Build task information table from array
    var taskarr = JSON.parse(data['taskarr'])
    var HTML = "";
    for (let i = 0; i < taskarr.taskinfo.length; i++) {
      HTML += '<tr><td><input type="button" id="taskRow-' + i + '" value="Delete" class="btn btn-primary"></td>';
      HTML += "<td>" + taskarr.taskinfo[i].tid + "</td>";
      HTML += "<td>" + taskarr.taskinfo[i].currstep + "/" + taskarr.taskinfo[i].endstep + "</td>";
      HTML += "<td>" + taskarr.taskinfo[i].destloc + "</td>";
      HTML += "<td>" + taskarr.taskinfo[i].completed + "</td></tr>";
    }
    document.getElementById("productionTask").innerHTML = HTML;

    //Build request information table from array
    var custskarr = JSON.parse(data['custskarr'])
    var HTML = "";
    for (let i = 0; i < custskarr.custskarr.length; i++) {
      HTML += '<tr><td><input type="button" id="cusTaskRow-' + i + '" value="Delete" class="btn btn-primary"></td>';
      HTML += "<td>" + custskarr.custskarr[i].tid + "</td>";
      HTML += "<td>" + custskarr.custskarr[i].currstep + "/" + custskarr.custskarr[i].endstep + "</td>";
      HTML += "<td>" + custskarr.custskarr[i].destloc + "</td>";
      HTML += "<td>" + custskarr.custskarr[i].completed + "</td></tr>";
    }
    document.getElementById("cusTsk").innerHTML = HTML;


    //Build custom request table
    var cusreqarr = JSON.parse(data['cusreqarr']);
    var HTML = "";
    for (let i = 0; i < cusreqarr.cusreqarr.length; i++) {
      HTML += '<tr><td><input type="button" id="cusReqRow-' + i + '" value="Delete" class="btn btn-primary"></td>';
      HTML += "<td>" + cusreqarr.cusreqarr[i].cid + "</td>";
      HTML += "<td>" + cusreqarr.cusreqarr[i].reqid + "</td>";
      HTML += "<td>" + cusreqarr.cusreqarr[i].priority + "</td>";
      HTML += "<td>" + cusreqarr.cusreqarr[i].status + "</td>";
      HTML += "<td>" + cusreqarr.cusreqarr[i].datetime + "</td></tr>";
    }
    document.getElementById("cusReq").innerHTML = HTML;

    document.getElementById("msmsg").innerHTML = data['msinfo'];
    document.getElementById("numRbtAvail").innerHTML = '<small>Robot Available: ' + rbtarr.rbtinfo.length + '</small>';
    document.getElementById("numProductionTask").innerHTML = "<small>In Queue: " + taskarr.taskinfo.length + '</small>';
    document.getElementById("numCusTsk").innerHTML = "<small>In Queue: " + custskarr.custskarr.length + '</small>';
    document.getElementById("numCusReq").innerHTML = "<small>In Queue: " + cusreqarr.cusreqarr.length + '</small>';

    //Attach button listener for all the four tables
    // attach_btn_listener(rbtarr.rbtinfo.length, "#robotTable","#rbtRow-", "numRbtAvail", "/", "robotID", "td:nth-child(2)", undefined, undefined, "Robot Successfully Deleted!");
    attach_btn_listener(taskarr.taskinfo.length, "#productionTaskTable","#taskRow-", "numProductionTask", "/", "productionTaskID", "td:nth-child(2)", undefined, undefined, "Production Task Successfully Deleted!");
    attach_btn_listener(custskarr.custskarr.length, "#cusTaskTable","#cusTaskRow-", "numCusTsk", "/", "cusTaskID", "td:nth-child(2)", undefined, undefined, "Custom Task Successfully Deleted!");
    attach_btn_listener(cusreqarr.cusreqarr.length, "#cusReqTable","#cusReqRow-", "numCusReq", "/", "cusReqID", "td:nth-child(2)", undefined, undefined, "Custom Request Successfully Deleted!");

    get_wo_table();
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
      HTML += '<tr><td><input type="button" id="woRow-' + i + '" value="Delete" class="btn btn-primary"></td>';
      HTML += "<td>" +      woarr.woperstnarr[i].status + "</td>";
      HTML += "<td>" +       woarr.woperstnarr[i].state + "</td>";
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
      HTML += "<td>" +      woarr.woperstnarr[i].orderNum + "</td>";
      HTML += "<td>" +      woarr.woperstnarr[i].expDate + "</td></tr>";
    }

    document.getElementById("WO").innerHTML = HTML;
    document.getElementById("numWO").innerHTML = "<small>In Queue: " + woarr.woperstnarr.length + '</small>';

    attach_btn_listener(woarr.woperstnarr.length, "#woTable","#woRow-", "numWO", "/", "woid", "td:nth-child(2)", "wostn", selectedWOStn, "Work Order Successfully Deleted!");
    // for (let i = 0; i < woarr.woperstnarr.length; i++) {
    //   var table = document.querySelector("#woTable");
    //   var deleteBtn = document.querySelector("#woRow-" + i.toString());
      
    //   //Attach listener for each delete button
    //   deleteBtn.addEventListener("click", function(event) {
    //     rowIndex = event.target.parentNode.parentNode.rowIndex;
        
    //     //Delete row in backend
    //     var form = document.createElement("form");
    //     form.method = "POST";
    //     form.action = "/";
        
    //     var inputwostn = document.createElement("input");
    //     inputwostn.type = "hidden";
    //     inputwostn.name = "wostn";
    //     inputwostn.value = selectedWOStn;

    //     var inputwoid = document.createElement("input");
    //     inputwoid.type = "hidden";
    //     inputwoid.name = "woid";
    //     inputwoid.value = event.target.parentNode.parentNode.querySelector('td:nth-child(2)').textContent;
        
    //     form.appendChild(inputwostn);
    //     form.appendChild(inputwoid);
    //     document.body.appendChild(form);
        
    //     fetch(form.action, {
    //       method: form.method,
    //       body: new FormData(form)
    //     }).then(function(response) {
    //       if (response.ok) {
    //         return response.text();
    //       }
    //       throw new Error("Network response was not ok.");
    //     }).then(function(text) {
    //       console.log("Response from server:", text);
    //       if (text == "Work Order Successfully Deleted!"){
    //         //Delete row on webpage & update count for queue
    //         table.deleteRow(rowIndex);
    //         str = document.getElementById("numWO").innerHTML;
    //         updatedCount = parseInt(str.split(": ")[1]) - 1;
    //         document.getElementById("numWO").innerHTML = "<small>In Queue: " + updatedCount + '</small>'
    //         addNotification(text, "success");
    //       }
    //       else {
    //         addNotification(text, "warning");
    //       }
    //     }).catch(function(error) {
    //       console.error("Error sending request:", error);
    //       addNotification("WO delete unsuccessful! Error sending request!", "warning");
    //     });
    //   });
    // }

    

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

    // Hide/Show columns
    if(selectedWOStn == 1){
      showColumn(15);
      hideColumn(16);
    }
    else if(selectedWOStn == 4){
      hideColumn(15);
      showColumn(16);
    }
    else{
      hideColumn(15);
      hideColumn(16);
    }
  });
}

function attach_btn_listener(nRows, tableName, rowIDPrefix, inQueueID, formAction, input1Name, input1Value, input2Name, input2Value, expectedRes){
  for (let i = 0; i < nRows; i++) {
    var table = document.querySelector(tableName);
    var deleteBtn = document.querySelector(rowIDPrefix + i.toString());
    
    //Attach listener for each delete button
    deleteBtn.addEventListener("click", function(event) {
      rowIndex = event.target.parentNode.parentNode.rowIndex;
      
      //Delete row in backend
      var form = document.createElement("form");
      form.method = "POST";
      form.action = formAction;
      
      var input1 = document.createElement("input");
      input1.type = "hidden";
      input1.name = input1Name;
      input1.value = event.target.parentNode.parentNode.querySelector(input1Value).textContent;
      form.appendChild(input1);

      if (input2Name !== undefined && input2Value !== undefined){
        var input2 = document.createElement("input");
        input2.type = "hidden";
        input2.name = input2Name;
        input2.value = input2Value;
        form.appendChild(input2);
      }
      
      document.body.appendChild(form);
      
      fetch(form.action, {
        method: form.method,
        body: new FormData(form)
      }).then(function(response) {
        if (response.ok) {
          return response.text();
        }
        throw new Error("Network response was not ok.");
      }).then(function(text) {
        console.log("Response from server:", text);
        if (text == expectedRes){
          //Delete row on webpage & update count for queue
          table.deleteRow(rowIndex);
          str = document.getElementById(inQueueID).innerHTML;
          updatedCount = parseInt(str.split(": ")[1]) - 1;
          document.getElementById(inQueueID).innerHTML = "<small>In Queue: " + updatedCount + '</small>'
          addNotification(text, "success");
        }
        else {
          addNotification(text, "warning");
        }
      }).catch(function(error) {
        console.error("Error sending request:", error);
        addNotification("WO delete unsuccessful! Error sending request!", "warning");
      });
    });
  }
}


get_all_table()
//Set refresh rate
setInterval(get_all_table, 3000);
get_all_table();