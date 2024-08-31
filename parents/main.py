import network
import time
import socket
from machine import Pin
import rp2
import gc


SSID: str = ""
PWD: str = ""
CH: int = 6
g_state_log: dict[str, dict[int, int]] = {
    "1": {"state": 1, "time": time.time()},
    "2": {"state": 1, "time": time.time()},
    "3": {"state": 1, "time": time.time()},
    "4": {"state": 1, "time": time.time()},
    "5": {"state": 1, "time": time.time()},
    "6": {"state": 1, "time": time.time()},
}  # "ID": {state, lastchanged time}


def start_ap():
    rp2.country("JP")
    print("startAP")
    ap = network.WLAN(network.AP_IF)
    ap.config(essid=SSID, password=PWD, channel=CH)
    ap.ifconfig(('192.168.4.1', '255.255.255.0', '192.168.4.1', '192.168.4.1'))
    ap.active(True)

    while True:
        print(ap.ifconfig())
        print(ap.status())
        if ap.active():
            return ap
        time.sleep(1)


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
    g_state_log[id] = {"state": int(state), "time": time.time()}
    print(g_state_log)
    return 0

# TODO 表示ロジック
# TODO 記録ロジック


def main():
    ap = start_ap()
    con = open_socket((ap.ifconfig()[0], 80))

    while True:
        handle_request(con)


if __name__ == "__main__":
    main()
