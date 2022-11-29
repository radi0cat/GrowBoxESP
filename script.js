<script>
    var sendData = {};
    var receiveData;
    const form = document.getElementById('formId');

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
                    document.forms.changes[i].checked = false;
                } else if (i > 3) {
                    document.getElementById("water").innerHTML = `Watering per Day: ${value}`;
                    sendData.water = value;
                    found1 = true;
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
                    document.getElementById("temperature").innerHTML = `${receiveData.sensors.temperature}`;
                    document.getElementById("humidity").innerHTML = `${receiveData.sensors.humidity}`;
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
                .catch(err => console.log(err));
        }
    }

    form.addEventListener('submit', checkState);
    setInterval(updateData, 1000);
</script>
