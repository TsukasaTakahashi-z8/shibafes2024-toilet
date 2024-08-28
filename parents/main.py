import network
import time
import urequests as requests

# https://micropython-docs-ja.readthedocs.io/ja/latest/library/network.WLAN.html
# https://makeblock-micropython-api.readthedocs.io/en/latest/public_library/Third-party-libraries/urequests.html
# https://note.com/nagisa_hoshimori/n/nd621ae39fc55
# https://qiita.com/IoriGunji/items/7ed9a09c03d5a9693ca0

SSID: str = ""
PWD: str = ""
ADDRS: list[str] = []  # e.g. ["192.168.1.1", "192.168.1.2"]; あらかじめ子機で固定しておく。


def start_ap():
    ap = network.WLAN(network.AP_IF)
    ap.config(essid=SSID, password=PWD)
    ap.active(True)
    ap.config(pm=network.WLAN.PM_POWERSAVE)
    if ap.isconnected():
        return 0
    else:
        start_ap()  # 無限ループ良くないかも


def get_sensor_data(ipaddr: str) -> str:
    # TODO 各子機にリクエスト送って、レスポンスを返却
    return ""

def generate_html():
    html = '''
    aiu{}
    '''.format(utime.localtime())

    return html

# TODO 表示ロジック
# TODO 記録ロジック


def main():
    start_ap()

    while True:
        time.sleep(1)
        for i in range(len(ADDRS)):
            get_sensor_data(ADDRS[i])


if __name__ == "__main__":
    main()
