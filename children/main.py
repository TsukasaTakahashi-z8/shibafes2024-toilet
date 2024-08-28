import network
import time
from machine import Pin
import _thread

TOILET_ID = 0  # 各個室のID(1~)
SSID = ""
PWD = ""
MY_IP = "192.168.1.x"  # xにトイレのID


class PicoStatus:
    RUNNING = 0
    WIFI_CONNECTING = 1
    WIFI_CONECT_FAIL = 2


g_restroom_status: int = 1


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


def get_restroom_status() -> int:
    sw: int = Pin(0, Pin.IN, Pin.PULL_UP)  # ==1: vacant, ==0: occupied
    return sw


def connect_network():
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    while True:
        wlan.connect(SSID, PWD)
        for _ in range(30):  # 3sec
            indicate_statusled(PicoStatus.WIFI_CONNECTING)

        if wlan.isconnected():
            wlan_status = wlan.ifconfig
            wlan.ifconfig((MY_IP, wlan_status[1], wlan_status[2], wlan_status[3]))
            return wlan.status()


def send_status(status):
    pass  # TODO


def core0():
    global g_restroom_status
    while True:
        new_restroom_status = get_restroom_status()

        if new_restroom_status != g_restroom_status:
            with _thread.allocate_lock:
                new_restroom_status = g_restroom_status

            send_status(new_restroom_status)


def core1():
    while True:
        indicate_statusled(PicoStatus.RUNNING)


def main():
    if connect_network() == network.STAT_GOT_IP:
        _thread.start_new_thread(core1, ())
        core0()
    else:
        while True:
            indicate_statusled(PicoStatus.WIFI_CONECT_FAIL)


if __name__ == "__main__":
    main()
