document.getElementById("msmsgblock").innerHTML = '<div class="h6 py-2 fw-bold" style="text-align: center; margin-bottom: 0px;">Robot Configuration</div>'
// Adjust msmsgblock to the center
document.getElementById("msmsgblock").style.position = "relative";
dif = (document.getElementById("userLogout").offsetWidth - document.getElementById("sideToggle").offsetWidth) / 2
document.getElementById("msmsgblock").style.left = dif + "px";
//Set sideCfgBtn active
document.getElementById("sideCfgBtn").classList.add("active");

function rip_listener(td_rip) {
  td_rip.addEventListener("blur", function (event) {
    var target = event.target;
    const row = event.target.parentNode;
    const rid = row.querySelector(".rid");
    console.log("rid: " + rid.innerHTML + " rip: " + target.innerHTML);
    
    var form = document.createElement("form");
    form.method = "POST";
    form.action = "/configuration";

    var inputRip = document.createElement("input");
    inputRip.type = "hidden";
    inputRip.name = "rip";
    inputRip.value = target.innerHTML;

    var inputRid = document.createElement("input");
    inputRid.type = "hidden";
    inputRid.name = "rid";
    inputRid.value = rid.innerHTML;

    form.appendChild(inputRip);
    form.appendChild(inputRid);
    document.body.appendChild(form);
    // form.submit();

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
      if (text == "Robot IP updated successfully"){
        addNotification(text, "success");
      }
      else {
        addNotification(text, "warning");
      }
    }).catch(function(error) {
      console.error("Error sending request:", error);
      addNotification("Update unsuccessful! Error sending request!", "warning");
    });

  });
}

// const tds_rip = document.querySelectorAll('td:nth-child(4)');
const tds = document.getElementsByClassName("rip");
const tdArray=Array.from(tds);
tdArray.forEach(rip_listener);



//register robot form listener
const regRbtForm = document.querySelector('#regRbtForm');
regRbtForm.addEventListener('submit', (event) => {
    event.preventDefault(); // Disable default form submission behavior
    fetch(regRbtForm.action, {
      method: regRbtForm.method,
      body: new FormData(regRbtForm)
    })
    .then(response => response.json())
    .then(function(data) {
      //console show response
      console.log("Response from server:", data.message);
      
      //show notification
      if (data.message == "Robot successfully registered!") {
        //reset form
        regRbtForm.reset();
        addNotification(data.message, "success");
        //update table
        tableBody = document.getElementById("rbtListTBody");
        const newRow =
          `<tr>
            <td class="rid">${data.rbtInfo.rbtID}</td>
            <td>${data.rbtInfo.rbtAlias}</td>
            <td>${data.rbtInfo.chrgThres}%</td>
            <td contenteditable="true" class="rip">${data.rbtInfo.rbtIP}</td>
          </tr>`;
        tableBody.insertAdjacentHTML('beforeend', newRow);
        rip_listener(document.querySelectorAll(".rip")[document.querySelectorAll(".rip").length-1])
      } else {
        addNotification(data.message, "warning");
      }

      
    })
  });