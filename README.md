# GrowBoxESP
This is an ESP32 powered, automated grow box with a local access point and adress http://192.168.4.1/. 
Light relay starts at stated time 5:00 vegetation and 8:00 pre-flowering and flowering stage, you can change this value in ajax_client.js if you wish.
Temperature and humidity are maintained within depending on the stage of growth with fan speed and temprature relay. 
The values is 60% humidity at vegetation and pre-flowering, 40% at flowering.
Watering relay moisturizes the hydroponics substrate a few times a day depending at setted quantity of times and growing stage.

Light relay(pin-22)
temprature relay(pin-25)
water_relay(pin-)
PWM fan speed(pin-27)
