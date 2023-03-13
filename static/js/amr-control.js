// Adjust msmsgblock to the center
document.getElementById("msmsgblock").innerHTML = '<div class="h6 py-2 fw-bold" style="text-align: center; margin-bottom: 0px;">Master Scheduler <br /><div id="msmsg"></div></div>'
document.getElementById("msmsgblock").style.position = "relative";
dif = (document.getElementById("userLogout").offsetWidth - document.getElementById("sideToggle").offsetWidth) / 2
document.getElementById("msmsgblock").style.left = dif + "px";
document.getElementById("sideDbBtn").classList.add("active");


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
function moveFun(){
    //location.reload();
	const selectElement = document.getElementById("exampleFormControlSelect1");
	if(selectElement.value!=""){

	//document.getElementById("stat").innerHTML = "Marking STN1" ;
	var confirmresult=confirm("Move to "+selectElement.value);
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
    fetch("amr/action/tocharge")
}

//FUnction to stop charging
function stopcharge(){
    fetch("amr/action/stopcharge")
}

function cancelnav(){
    fetch("amr/action/cancelnav")
}

document.getElementById("rbtpos").innerHTML = 'Charging Station';