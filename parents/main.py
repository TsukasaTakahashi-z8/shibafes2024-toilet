import network
import time
import socket
from machine import Pin
import rp2

# https://micropython-docs-ja.readthedocs.io/ja/latest/library/network.WLAN.html
# https://makeblock-micropython-api.readthedocs.io/en/latest/public_library/Third-party-libraries/urequests.html
# https://note.com/nagisa_hoshimori/n/nd621ae39fc55
# https://qiita.com/IoriGunji/items/7ed9a09c03d5a9693ca0

SSID: str = ""
PWD: str = ""
CH: int = 6
g_state_log: dict[str, dict[int, int]] = {
    "0": {1, time.time()},
    "1": {1, time.time()},
    "2": {1, time.time()},
    "3": {1, time.time()},
    "4": {1, time.time()},
    "5": {1, time.time()},
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
    client = con.accept()[0]
    request = client.recv(256).decode()

    # 文字数から無理やりパラメータ取得
    id = request[-9]
    state = request[-1]

    if change_state(id, state) == 0:
        client.send("HTTP/1.1 200 OK\n\nGood Job!")
    else:
        client.send("HTTP/1.1 500 Internal Server Error\n\nI'm so sorry...")

    client.close()


def change_state(id: str, state: str):
    g_state_log[id] = [int(state), time.time()]
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
