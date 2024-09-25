import network
import time
import socket
from machine import Pin
import gc
import _thread


SSID: str = ""
PWD: str = ""
CH: int = 6
g_LED = {
    "1": [Pin(17, Pin.OUT), Pin(16, Pin.OUT)],
    "2": [Pin(13, Pin.OUT), Pin(12, Pin.OUT)],
    "3": [Pin(9, Pin.OUT), Pin(8, Pin.OUT)],
    "4": [Pin(5, Pin.OUT), Pin(4, Pin.OUT)],
    "5": [Pin(1, Pin.OUT), Pin(0, Pin.OUT)],
    "6": [Pin(28, Pin.OUT), Pin(27, Pin.OUT)],
    "7": [Pin(26, Pin.OUT), Pin(22, Pin.OUT)],
    "8": [Pin(21, Pin.OUT), Pin(20, Pin.OUT)]
}
g_emergency_ids: list[bool] = [False]*8
lock = _thread.allocate_lock()


class PicoStatus:
    RUNNING = 0
    WIFI_CONNECTING = 1
    WIFI_CONECT_FAIL = 2


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


def check_display_led():
    for i in range(1, 8+1):
        g_LED[str(i)][0].on()
        g_LED[str(i)][1].on()

    time.sleep(2)

    for i in range(1, 8+1):
        g_LED[str(i)][0].off()
        g_LED[str(i)][1].on()

    time.sleep(1)

    for i in range(1, 8+1):

        g_LED[str(i)][0].on()
        g_LED[str(i)][1].off()

    time.sleep(1)

    for i in range(1, 8+1):
        g_LED[str(i)][0].off()
        g_LED[str(i)][1].off()

    time.sleep(1)

    for i in range(1, 8+1):
        g_LED[str(i)][0].on()
        g_LED[str(i)][1].off()
        time.sleep(0.1)
        g_LED[str(i)][0].off()
        g_LED[str(i)][1].on()
        time.sleep(0.1)
        g_LED[str(i)][0].off()
        g_LED[str(i)][1].off()
        time.sleep(0.1)


def connect_network():
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    # TODO add wlan.conf() to set my IPaddr(192.168.4.1)
    while True:
        wlan.connect(SSID, PWD)
        wlan.ifconfig(('192.168.4.1', '255.255.255.0', '192.168.4.200', '192.168.4.200'))
        for _ in range(30):  # 3sec
            indicate_statusled(PicoStatus.WIFI_CONNECTING)

            if wlan.isconnected():
                return wlan


def open_socket(addr):
    con = socket.socket()
    con.bind(addr)
    con.listen(1)
    return con


def handle_request(con):
    gc.collect()
    client = con.accept()[0]
    request = client.recv(256).decode()

    # 文字数から無理やりパラメータ取得
    id = request[-9]
    state = request[-1]

    if change_state(id, state) == 0:
        client.send("200")
    else:
        client.send("500")

    client.close()


def change_state(id: str, state: str):
    if state == "2":
        with lock:
            g_emergency_ids[int(id)-1] = True

    elif state == "0" or state == "1":
        g_LED[id][int(state)].on()
        g_LED[id][1 - int(state)].off()
        with lock:
            g_emergency_ids[int(id)-1] = False
    else:
        g_LED[id][0].on()
        g_LED[id][1].on()

    return 0


def emergency_led(g_emergency_ids: list[int]):
    while True:
        with lock:
            emergency_ids = g_emergency_ids

        for i in range(1, 8+1):
            if emergency_ids[i-1]:
                g_LED[str(i)][0].on()
                g_LED[str(i)][1].off()
        time.sleep(0.2)

        for i in range(1, 8+1):
            if emergency_ids[i-1]:
                g_LED[str(i)][0].off()
                g_LED[str(i)][1].off()
        time.sleep(0.2)


def main():
    check_display_led()
    wlan = connect_network()
    con = open_socket((wlan.ifconfig()[0], 80))

    while True:
        handle_request(con)


_thread.start_new_thread(emergency_led, (g_emergency_ids,))
main()
