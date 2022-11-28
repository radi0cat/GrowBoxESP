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
                    document.getElementById("day").innerHTML = `${receiveData.day}`;
                    document.getElementById("month").innerHTML = `${receiveData.month}`;
                    document.getElementById("year").innerHTML = `${receiveData.year}`;
                    document.getElementById("hours").innerHTML = `${receiveData.hours}`;
                    document.getElementById("minutes").innerHTML = `${receiveData.minutes}`;
                    document.getElementById("seconds").innerHTML = `${receiveData.seconds}`;
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
        } else {
            sendRequest('GET', '/get_data')
                .then(() => {
                    if(Object.keys(sendData).length !== 0){
                        console.log(`Method get, data: ${JSON.stringify(sendData)}`)
                    }})
                .catch(err => console.log(err));
        }
    }

    form.addEventListener('submit', checkState);
    setInterval(updateData, 5000);
</script>

