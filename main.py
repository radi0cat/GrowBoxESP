try:
  import usocket as socket
except:
  import socket
  
import json

import gc
gc.collect()

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.bind(('', 80))
s.listen(1)


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
    return data


def write_config(obj):
    data = read_config()

    if obj != '':
        obj = json.loads(obj)

        if 'stage' in obj.keys() and 'water' in obj.keys():
            data['stage'] = obj['stage']
            data['water'] = obj['water']

            with open('config.json', 'w') as file:
                json.dump(data, file)
       
    return data

    
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
        
        response = write_config(obj)

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

