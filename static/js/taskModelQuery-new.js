document.getElementById("msmsgblock").innerHTML = '<div class="h6 py-2 fw-bold" style="text-align: center; margin-bottom: 0px;">Query Task Model</div>'
// Adjust msmsgblock to the center
document.getElementById("msmsgblock").style.position = "relative";
dif = (document.getElementById("userLogout").offsetWidth - document.getElementById("sideToggle").offsetWidth) / 2
document.getElementById("msmsgblock").style.left = dif + "px";
//Set sideTskModelBtn and sideQueryBtn active
document.getElementById("sideTskModelBtn").classList.add("active");
document.getElementById("sideQueryBtn").classList.add("active");


//register robot form listener
const tskQueryForm = document.querySelector('#tskQueryForm');
tskQueryForm.addEventListener('submit', (event) => {
    event.preventDefault(); // Disable default form submission behavior
    console.log("Task query event listener triggered.");
    fetch(tskQueryForm.action, {
      method: tskQueryForm.method,
      body: new FormData(tskQueryForm),
    })
    .then(response => response.json())
    .then(function(data) {
        tableBody = document.getElementById("tskModelTable");
        let row = "";
        let rowList = "";
        console.log(data);
        for (let task of JSON.parse(data).sbList){
            row =   `<tr>
                        <td class="rid">${task.tmid}</td>
                        <td>${task.stid}</td>
                        <td>${task.at}</td>
                        <td>${task.currstep}</td>
                        <td>${task.endstep}</td>
                        <td contenteditable="true" class="rip">${task.cmd}</td>
                    </tr>`;
            rowList += row;
        }
        tableBody.innerHTML = "";
        tableBody.insertAdjacentHTML('afterbegin', rowList);
    })
  });




