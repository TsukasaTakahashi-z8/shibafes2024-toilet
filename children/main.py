import network
import time
from machine import Pin
import _thread
import gc
import urequests

TOILET_ID = 0  # 各個室のID(1~)
SSID = ""
PWD = ""
BLUE_PIN = 10
RED_PIN = 9
HOST = "192.168.4.200"
PORT = 80


class PicoStatus:
    RUNNING = 0
    WIFI_CONNECTING = 1
    WIFI_CONECT_FAIL = 2


g_restroom_state: int = 1


def indicate_statusled(status):
    led = Pin("LED", Pin.OUT)

    # may be not support match-case statement
    if status == PicoStatus.RUNNING:
        led.on()
        time.sleep(1)
        led.off()
        time.sleep(1)

    elif status == PicoStatus.WIFI_CONNECTING:
        led.on()
        time.sleep(0.1)
        led.off()
        time.sleep(0.1)

    elif status == PicoStatus.WIFI_CONECT_FAIL:
        led.on()
        time.sleep(0.1)
        led.off()
        time.sleep(0.1)
        led.on()
        time.sleep(0.1)
        led.off()
        time.sleep(0.5)

    else:
        led.off()


def get_restroom_state() -> int:
    sw: int = Pin(0, Pin.IN, Pin.PULL_UP).value()  # ==1: vacant, ==0: occupied
    return sw


def connect_network():
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    while True:
        wlan.connect(SSID, PWD)
        for _ in range(30):  # 3sec
            indicate_statusled(PicoStatus.WIFI_CONNECTING)

            if wlan.isconnected():
                return wlan.status()


def change_led(state):
    blue_led = Pin(BLUE_PIN, Pin.OUT)
    red_led  = Pin(RED_PIN,  Pin.OUT)

    if state == 0:
        blue_led.off()
        red_led .on()
    elif state == 1:
        blue_led.on()
        red_led .off()
    elif state == -1:
        blue_led.on()
        red_led .on()
    else:
        blue_led.off()
        red_led .off()


def send_state(state):
    print("sender")
    date = "id="+str(TOILET_ID)+"&state="+str(state)
    print(date)
    headers = {'Content-Type': 'application/x-www-form-urlencoded'}
    res = urequests.post("http://" + HOST, data=date, headers=headers)
    gc.collect()
    print(res)
   

def core0():
    global g_restroom_state
    change_led(1)  # default
    lock = _thread.allocate_lock()
    while True:
        new_restroom_state = get_restroom_state()
        print('new_restroom_state')

        if g_restroom_state != new_restroom_state:
            with lock:
                g_restroom_state = new_restroom_state

            change_led(new_restroom_state)
            print('change_led')
            x = send_state(new_restroom_state)
            print(x)

        time.sleep_ms(100)


def core1():
    while True:
        indicate_statusled(PicoStatus.RUNNING)


def main():
    change_led(-1)
    res = connect_network()
    if res == network.STAT_GOT_IP:
        _thread.start_new_thread(core1, ())
        core0()
    else:
        change_led(2)
        while True:
            indicate_statusled(PicoStatus.WIFI_CONECT_FAIL)


if __name__ == "__main__":
    main()
