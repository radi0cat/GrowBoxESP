try:
    import usocket as socket
except:
    import socket

import json
from dht import DHT22
from machine import Pin, Timer, RTC

import gc

gc.collect()

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.bind(('', 80))
s.listen(1)

# Create real time clock object
rtc = RTC()

# Create DHT22 sensor object
temp_sensor = DHT22(Pin(23))

# Initiate termo timer
thermo_timer = Timer(1)



def web_page():
    with open('index.html', 'r') as f:
        content = f.read()

    with open('styles.css', 'r') as f:
        content = content.replace('<link rel="stylesheet" href="styles.css" type="text/css">', f.read())

    with open('script.js', 'r') as f:
        content = content.replace('<script src="script.js"></script>', f.read())

    return content


def read_config():
    with open('config.json', 'r') as file:
        data = json.load(file)
        data.update(current_datetime())
        data.update(receive_temperature_and_humidity())
    return data


def write_config(obj):
    with open('config.json', 'r') as in_file:
        data = json.load(in_file)

    if obj != '':
        obj = json.loads(obj)

        if 'stage' in obj.keys() and 'water' in obj.keys():
            data['stage'] = obj['stage']
            data['water'] = obj['water']

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


def receive_temperature_and_humidity():
#    temp_sensor.measure()
    temp = temp_sensor.temperature()
    humid = temp_sensor.humidity()

    return {"sensors": {"temperature": '%3.1f' % temp, "humidity": '%3.1f' % humid}}


temp_sensor.measure()
thermo_timer.init(period=5000, mode=Timer.PERIODIC, callback=lambda t:temp_sensor.measure())

while True:
    # Socket accept()
    conn, addr = s.accept()
    print("Got connection from %s" % str(addr))
    # Socket receive()
    request = str(conn.recv(1024), 'utf-8')

    if '/get_data' in request:
        # Create a socket reply
        response = read_config()
        conn.send('HTTP/1.1 200 OK\n')
        conn.send('Content-Type: application/json\n')
        conn.send('Connection: close\n\n')
        conn.sendall(json.dumps(response))

    elif '/post_data' in request:
        # Create a socket reply
        obj = request.splitlines()[-1]
        write_config(obj)

        response = read_config()
        conn.send('HTTP/1.1 200 OK\n')
        conn.send('Content-Type: application/json\n')
        conn.send('Connection: close\n\n')
        conn.sendall(json.dumps(response))

    elif '/change_time' in request:
        dt_string = request.splitlines()[-1]
        change_datetime(dt_string)

        response = read_config()
        conn.send('HTTP/1.1 200 OK\n')
        conn.send('Content-Type: application/json\n')
        conn.send('Connection: close\n\n')
        conn.sendall(json.dumps(response))

    else:
        response = web_page()
        # Create a socket reply
        conn.send('HTTP/1.1 200 OK\n')
        conn.send('Content-Type: text/html\n')
        conn.send('Connection: close\n\n')
        conn.sendall(response)

    # Socket close
    conn.close()
    gc.collect()
