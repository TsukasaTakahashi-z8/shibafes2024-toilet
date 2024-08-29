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

def status2message(status):
    # 1000
    if status == network.STAT_IDLE: return "STAT_IDLE"
    # 1001
    if status == network.STAT_CONNECTING: return "STAT_CONNECTING"
    # 202
    if status == network.STAT_WRONG_PASSWORD: return "STAT_WRONG_PASSWORD"
    # 201
    if status == network.STAT_NO_AP_FOUND: return "STAT_NO_AP_FOUND"
    # 1010
    if status == network.STAT_GOT_IP: return "STAT_GOT_IP"
    # 203
    if status == network.STAT_ASSOC_FAIL: return "STAT_ASSOC_FAIL"
    # 200
    if status == network.STAT_BEACON_TIMEOUT: return "STAT_BEACON_TIMEOUT"
    # 204
    if status == network.STAT_HANDSHAKE_TIMEOUT: return "STAT_HANDSHAKE_TIMEOUT"
    # :(
    return "UNKNOWN_STATUS"

def start_ap():
    rp2.country("JP")
    print("startAP")
    ap = network.WLAN(network.AP_IF)
    ap.config(ssid=SSID, key=PWD, channel=CH)
    ap.ifconfig(('192.168.4.1', '255.255.255.0', '192.168.4.1', '192.168.4.1'))
    ap.active(True)

    while True:
        print(ap.ifconfig())
        print(ap.status())
        status = ap.status()
        if ap.active():
            return ap
        if status == network.STAT_IDLE:
            time.sleep(1)
            continue
        if status == network.STAT_CONNECTING:
            time.sleep(1)
            continue

        print(f"something went wrong. {status2message(status)}")
        break


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
