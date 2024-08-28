import time
from machine import Pin


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


def get_restroom_status() -> bool:
    sw: bool = Pin(0, Pin.IN, Pin.PULL_UP)  # ==1: vacant, ==0: occupied
    return sw


def main():
    return 0


if __name__ == "__main__":
    main()
