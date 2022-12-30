<script>
    var sendData = {};
    var receiveData;
    const form = document.getElementById('formId');

    const modal = document.querySelector(".modal");
    const trigger = document.querySelector(".trigger");
    const closeButton = document.querySelector(".close-button");

    function checkState() {
        event.preventDefault();

        let found0 = false;
        let found1 = false;

        for(i=0; i<9; i++) {
            if (document.forms.changes[i].checked) {
                let value = document.forms.changes[i].value;
                if (i < 4) {
                    document.getElementById("stage_title").innerHTML = `Growth Stage: ${value}`;
                    sendData.stage = value;
                    found0 = true;
                    console.log(`Now ${sendData.stage} is activated`);
                    document.forms.changes[i].checked = false;
                } else if (i > 3) {
                    document.getElementById("water").innerHTML = `Watering per Day: ${value}`;
                    sendData.water = value;
                    found1 = true;
                    console.log(`Now ${sendData.water} is activated`);
                    document.forms.changes[i].checked = false;
                    break;
                }
            }
        }

        if(!found0) {
            sendData.stage = receiveData.stage;
        }

        if(!found1) {
            sendData.water = receiveData.water;
        }

        console.log(sendData);
    }


    function sendRequest(method, url, body=null) {
        return new Promise((resolve, reject) => {
            const xhr = new XMLHttpRequest();
            
            xhr.open(method, url);

            xhr.responseType = 'json';
            xhr.setRequestHeader('Content-Type', 'application/json');

            xhr.onload = () => {
                if (xhr.status >= 400){
                    reject(xhr.response);
                } else {
                    resolve(xhr.response);
                    receiveData = xhr.response;
                    // Date and time
                    document.getElementById("day").innerHTML = `${receiveData.date_time.day}`;
                    document.getElementById("month").innerHTML = `${receiveData.date_time.month}`;
                    document.getElementById("year").innerHTML = `${receiveData.date_time.year}`;
                    document.getElementById("hours").innerHTML = `${receiveData.date_time.hours}`;
                    document.getElementById("minutes").innerHTML = `${receiveData.date_time.minutes}`;
                    document.getElementById("seconds").innerHTML = `${receiveData.date_time.seconds}`;
                    // Temperature and humidity
                    // State stage and watering
                    document.getElementById("water").innerHTML = `Watering per Day: ${receiveData.water}`;
                    document.getElementById("stage_title").innerHTML = `Growth Stage: ${receiveData.stage}`;
                }
            }
            xhr.onerror = () => {
                reject(xhr.response);
            }
            xhr.send(JSON.stringify(body))
        })
    }

    function updateData(){
        if (Object.keys(sendData).length !== 0) {
            sendRequest('POST', '/post_data', sendData)
                .then(sendData = {})
                .catch(err => console.log(err));
        } else if (document.getElementById("year").innerHTML == 2000) {
            dt = new Date().toLocaleString();
            sendRequest('POST', '/change_time', dt)
            
        } else {
            sendRequest('GET', '/get_data')
                .then(() => {
                    if(Object.keys(sendData).length !== 0){
                        console.log(`Method get, data: ${JSON.stringify(sendData)}`)
                    }})
                .catch(err => console.log(err));
        }
    }

    function toggleModal() {
        modal.classList.toggle("show-modal");
    }

    function windowOnClick(event) {
        if (event.target === modal) {
            toggleModal();
        }
    }

    function clearInput() {
        document.querySelector(".add-note-form").reset();
        toggleModal();
    }

    trigger.addEventListener("click", toggleModal);
    closeButton.addEventListener("click", toggleModal);
    window.addEventListener("click", windowOnClick);
    form.addEventListener('submit', checkState);
    setInterval(updateData, 1000);
</script>
