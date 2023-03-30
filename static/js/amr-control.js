// Adjust msmsgblock to the center
document.getElementById("msmsgblock").innerHTML = '<div class="h6 py-2 fw-bold" style="text-align: center; margin-bottom: 0px;">Master Scheduler <br /><div id="msmsg"></div></div>'
document.getElementById("msmsgblock").style.position = "relative";
dif = (document.getElementById("userLogout").offsetWidth - document.getElementById("sideToggle").offsetWidth) / 2
document.getElementById("msmsgblock").style.left = dif + "px";
document.getElementById("sideAMRBtn").classList.add("active");


function savepoint(){
     //location.reload();
	const selectElement = document.getElementById("exampleFormControlSelect1");
	if(selectElement.value!=""){

	//document.getElementById("stat").innerHTML = "Marking STN1" ;
	var confirmresult=confirm("Save "+selectElement.value);
    if (confirmresult==true){
        
        fetch("/amr/save/"+selectElement.value)
	
	}
    }

}

function locpoint(){
  //location.reload();
const selectElement = document.getElementById("exampleFormControlSelect1");
if(selectElement.value!=""){

//document.getElementById("stat").innerHTML = "Marking STN1" ;
var confirmresult=confirm("Localize AMR to "+selectElement.value);
 if (confirmresult==true){
     
     fetch("/amr/localize/"+selectElement.value)

}
 }

}
function moveFun(){
    //location.reload();
	const selectElement = document.getElementById("exampleFormControlSelect1");
	if(selectElement.value!=""){

	//document.getElementById("stat").innerHTML = "Marking STN1" ;
	var confirmresult=confirm("Please confirm you want to move AMR to "+selectElement.value);
    if (confirmresult==true){
        
        fetch("/amr/move/"+selectElement.value)
	
	}
    }
	
	
}
//Function to reset AMR
function resetMotor(){
    fetch("amr/action/reset")
}

//FUnction to go charge
function tocharge(){
  var confirmresult=confirm("Please confirm you want to charge AMR ");
    if (confirmresult==true){
    fetch("amr/action/tocharge")
    }
}

//FUnction to stop charging
function stopcharge(){
  var confirmresult=confirm("Please confirm you want to stop charging AMR ");
  if (confirmresult==true){
    fetch("amr/action/stopcharge")
  }
}

function cancelnav(){
    fetch("amr/action/cancelnav")
}

// document.getElementById("rbtpos").innerHTML = 'Charging Station';

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

      document.getElementById("msmsg").innerHTML = data['msinfo'];
    });
}


setInterval(get_all_table, 5000);
get_all_table();