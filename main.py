import usocket as socket
import json
from dht import DHT22
from machine import Pin, Timer, RTC, PWM
import gc

gc.collect()

# Create real time clock object
rtc = RTC()
# Create DHT22 sensor object
temp_sensor = DHT22(Pin(23))
# Create light relay
light_relay = Pin(22, Pin.OUT)
# Create thermo relay
thermal_relay = Pin(25, Pin.OUT)
# Create watering relay
water_relay = Pin(2, Pin.OUT)
# Create fan PWM channel
fan = PWM(Pin(27), 25000)

# Create light and termo timer
light_termo_timer = Timer(-1)


def web_page():
    with open('index.html', 'r') as f:
        content = f.read()

    with open('styles.css', 'r') as f:
        content = content.replace('<link rel="stylesheet" href="styles.css" type="text/css">', f.read())

    with open('script.js', 'r') as f:
        content = content.replace('<script src="ajax_client.js"></script>', f.read())

    return content


def create_response():
    with open('config.json', 'r') as file:
        data = json.load(file)
        # Add current date and time
        data.update(current_datetime())
        # Add temperature and humidity object
        temp = temp_sensor.temperature()
        humid = temp_sensor.humidity()
        data.update({"sensors": {"temperature": '%3.1f' % temp, "humidity": '%3.1f' % humid}})

    return json.dumps(data)


def read_config():
    with open('config.json', 'r') as file:
        data = json.load(file)

    return data


def write_config(obj):
    with open('config.json', 'r') as in_file:
        data = json.load(in_file)

    if obj != '':
        obj = json.loads(obj)

        if 'stage' in obj.keys() and 'water' in obj.keys():
            data['stage'] = obj['stage']
            data['water'] = obj['water']
            data['start_light'] = obj['start_light']

            with open('config.json', 'w') as out_file:
                json.dump(data, out_file)


def to_str(n):
    if n < 10:
        return '0' + str(n)
    else:
        return str(n)


def current_datetime():
    dt = rtc.datetime()

    return {"date_time": {"year": to_str(dt[0]),
                          "month": to_str(dt[1]),
                          "day": to_str(dt[2]),
                          "hours": to_str(dt[4]),
                          "minutes": to_str(dt[5]),
                          "seconds": to_str(dt[6])}
            }


def change_datetime(obj):
    y = int(obj[7:11])
    m = int(obj[4:6])
    d = int(obj[1:3])
    h = int(obj[13:15])
    mn = int(obj[16:18])
    sc = int(obj[19:-1])
    rtc.datetime((y, m, d, 0, h, mn, sc, 0))


def run_server():
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind(('', 80))
    s.listen(5)

    while True:
        # Socket accept()
        conn, addr = s.accept()
        print("Got connection from %s" % str(addr))
        # Socket receive()
        request = str(conn.recv(2048), 'utf-8')

        if '/get_data' in request:
            # Create a socket reply if web page loaded.
            conn.send('HTTP/1.1 200 OK\n')
            conn.send('Content-Type: application/json\n')
            conn.send('Connection: close\n\n')
            conn.sendall(create_response())

        elif '/post_data' in request:
            # if method is post write changes to config file.
            obj = request.splitlines()[-1]
            write_config(obj)
            # Create a socket reply
            conn.send('HTTP/1.1 200 OK\n')
            conn.send('Content-Type: application/json\n')
            conn.send('Connection: close\n\n')
            conn.sendall(create_response())

        elif '/change_time' in request:
            change_datetime(request.splitlines()[-1])
            # Create a socket reply.
            conn.send('HTTP/1.1 200 OK\n')
            conn.send('Content-Type: application/json\n')
            conn.send('Connection: close\n\n')
            conn.sendall(create_response())

        else:
            # Create a socket reply
            conn.send('HTTP/1.1 200 OK\n')
            conn.send('Content-Type: text/html\n')
            conn.send('Connection: close\n\n')
            conn.sendall(web_page())

        conn.close()


def control_light_temperature_humidity():    
    obj = read_config()

    check_fan_and_termo(obj['stage'])
    check_light(obj['start_light'])
    check_water(obj['start_light'], obj['water'])

    gc.collect()
    

def check_light(start):
    hours = []
    start_hour = int(start.split(":")[0])

    if start_hour == 5:
        duration = 18
    else:
        duration = 12

    for i in range(duration + 1):
        hours.append(start_hour)
        start_hour += 1
        if start_hour > 23:
            start_hour = 0

    hours = tuple(hours)
    cur_h = rtc.datetime()[4]

    if cur_h in hours[:-1]:
        light_relay.on()
    else:
        light_relay.off()


def check_fan_and_termo(stage):
    temp_sensor.measure()
    cur_temp = temp_sensor.temperature()
    cur_hum = temp_sensor.humidity()
    if stage == 'Flowering':
        min_temp = 18
        set_hum = 40
    else:
        min_temp = 22
        set_hum = 60

    max_temp = 27
    cycle = fan.duty()
    if cur_temp > max_temp:
        if cycle > 0:
            cycle -= 1
        thermal_relay.off()

    elif min_temp < cur_temp < max_temp and cur_hum <= set_hum:
        if cycle < 512:
            cycle += 1
        thermal_relay.on()

    elif min_temp < cur_temp < max_temp and cur_hum > set_hum:
        if cycle > 0:
            cycle -= 1
        thermal_relay.on()

    elif cur_temp < min_temp:
        thermal_relay.on()
        if cycle < 512:
            cycle += 1

    fan.duty(cycle)


def check_water(start, water):
    start = int(start.split(":")[0])
    if water == '1':
        hours = (start,)

    elif water == '2':
        if start == 8:
            hours = (start, start + 6)
        else:
            hours = (start, start + 9)

    elif water == '3':
        if start == 8:
            hours = (start, start + 4, start + 8)
        else:
            hours = (start, start + 6, start + 12)
    else:
        hours = tuple()

    cur_h = rtc.datetime()[4]
    cur_m = rtc.datetime()[5]

    if cur_h in hours and cur_m == 0:
        water_relay.on()
    else:
        water_relay.off()


if __name__ == '__main__':
    temp_sensor.measure()
    # Initiate light and thermal timer
    light_termo_timer.init(period=5000, mode=Timer.PERIODIC, callback=lambda l: control_light_temperature_humidity())
    run_server()
    print('print after run server')
