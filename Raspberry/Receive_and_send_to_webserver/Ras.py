import RPi.GPIO as GPIO
GPIO.setwarnings(False)
from time import sleep
from SX127x.LoRa import *
from SX127x.board_config import BOARD
import paho.mqtt.client as mqtt
username = "b4ebd1b0-bb76-11ea-b767-3f1a8f1211ba"
password = "2f3fc93858a942c7b322807af500261714c789cb"
clientid = "338bf370-bbc6-11ea-b767-3f1a8f1211ba"
mqttc = mqtt.Client(client_id=clientid)
mqttc.username_pw_set(username, password=password)
mqttc.connect("mqtt.mydevices.com", port=1883, keepalive=60)
mqttc.loop_start()
topic_dht11_temp = "v1/" + username + "/things/" + clientid + "/data/1"
topic_dht11_humidity = "v1/" + username + "/things/" + clientid + "/data/2"
BOARD.setup()
class LoRaRcvCont(LoRa):
    def __init__(self, verbose=False):
        super(LoRaRcvCont, self).__init__(verbose)
        self.set_mode(MODE.SLEEP)
        self.set_dio_mapping([0] * 6)
    def start(self):
        self.reset_ptr_rx()
        self.set_mode(MODE.RXCONT)
        while True:
            sleep(.5)
            rssi_value = self.get_rssi_value()
            status = self.get_modem_status()
            sys.stdout.flush()         
    def on_rx_done(self):
        print ("\nReceived: ")
        self.clear_irq_flags(RxDone=1)
        payload = self.read_payload(nocheck=True)
        #print (bytes(payload).decode("utf-8",'ignore'))
        data = bytes(payload).decode("utf-8",'ignore')
        #print (data)
        temp = (data[2:4])
        humidity = (data[5:6])
        print ("Temperature:",temp,"*C")
        #print (temp)
        print ("Humidity:",humidity,"%")
        #print (humidity)
        mqttc.publish(topic_dht11_temp, payload=temp, retain=True)
        mqttc.publish(topic_dht11_humidity, payload=humidity, retain=True)
        print ("Sent to Cayenne")
        self.set_mode(MODE.SLEEP)
        self.reset_ptr_rx()
        self.set_mode(MODE.RXCONT) 
lora = LoRaRcvCont(verbose=False)
lora.set_mode(MODE.STDBY)
#  Medium Range  Defaults after init are 434.0MHz, Bw = 125 kHz, Cr = 4/5, Sf = 128chips/symbol, CRC on 13 dBm
lora.set_pa_config(pa_select=1)
try:
    lora.start()
except KeyboardInterrupt:
    sys.stdout.flush()
    print ("")
    sys.stderr.write("KeyboardInterrupt\n")
finally:
    sys.stdout.flush()
    print ("")
    lora.set_mode(MODE.SLEEP)
    BOARD.teardown()