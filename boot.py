# This file is executed on every boot (including wake-boot from deepsleep)
#import esp
#esp.osdebug(None)
def do_connect():
    import network
    wlan = network.WLAN(network.AP_IF)
    wlan.active(True)
    if not wlan.isconnected():
        print('connecting to network...')
        wlan.config(essid='esp', password='51-eSoram', max_clients=3, authmode=network.AUTH_WPA_WPA2_PSK)
        while not wlan.isconnected():
            pass
    print('network config:', wlan.ifconfig())
    
do_connect()

