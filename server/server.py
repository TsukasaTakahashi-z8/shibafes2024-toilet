from http.server import HTTPServer
from http.server import BaseHTTPRequestHandler
import subprocess
import csv
import time
import datetime
import threading


TOILET_NUM: int = 8
REPORT_TIME = datetime.timedelta(minutes=30)
# REPORT_TIME = datetime.timedelta(seconds=1)
g_lastused_time: list[list[datetime.datetime, int]] = [[datetime.datetime.now(), 1]] * TOILET_NUM
lock = threading.Lock()


class CustomHTTPRequestHandler(BaseHTTPRequestHandler):

    def do_GET(self):
        print("Do GET")
        self.send_response(200)
        self.send_header('Content-type', 'text/plain; charset=utf-8')
        self.end_headers()
        content = "No data"
        try:
            with open("toilet_log.csv", "r") as f:
                content = f.read()
        except Exception as e:
            content = "Error cannot read to toilet_log"
        content += "\n==="
        with lock:
            for i in range(TOILET_NUM):
                content += "\n"
                content += g_lastused_time[i][0].isoformat()
                content += "\n"
                content += str(g_lastused_time[i][1])

        self.wfile.write(content.encode())

    def do_POST(self):
        print("Do POST")
        body = self.rfile.read(12).decode('utf-8')
        id = body[-9]
        state = body[-1]
        try:
            with open("toilet_log.csv", "a") as f:
                writer = csv.writer(f)
                now = datetime.datetime.now().isoformat()

                writer.writerow([now, id, state])
        except:
            print("Logging Error")

        with lock:
            g_lastused_time[int(id)-1] = [datetime.datetime.now(), int(state)]
        print(subprocess.run(["curl", "-X", "POST", "http://192.168.4.1/", "-d", body, "-m", "5"], capture_output=True))
        print(subprocess.run(["curl", "-X", "POST", "http://192.168.4.2/", "-d", body, "-m", "5"], capture_output=True))
        print(body)
        self.send_response(200)
        self.send_header('Content-type', 'text/plain; charset=utf-8')
        self.end_headers()
        self.wfile.write('Good Job!'.encode())


def check_time():
    while True:
        time.sleep(60)
        # time.sleep(10)
        print("Check")
        now = datetime.datetime.now()

        for i in range(8):
            with lock:
                if now >= g_lastused_time[i][0] + REPORT_TIME and g_lastused_time[i][1] == 0:
                    body = f"id={i+1}&state=2"
                    print(subprocess.run(["curl", "-X", "POST", "http://192.168.4.1/", "-d", body, "-m", "5"], capture_output=True))
                    print(subprocess.run(["curl", "-X", "POST", "http://192.168.4.2/", "-d", body, "-m", "5"], capture_output=True))
                    g_lastused_time[i][1] = 2


threading.Thread(target=check_time, daemon=True).start()

server_address = ('', 80)
httpd = HTTPServer(server_address, CustomHTTPRequestHandler)
httpd.serve_forever()
