import base64
import random
import sys
import time
import multiprocessing.dummy as mp
import uuid
import websocket, json
import requests
from base64 import b64encode as encoder
from rich.console import Console
import colorama
from colorama import Fore, Style
from datetime import datetime
import os
from utils import change_title
from utils import Config
from utils import check_user_proxy
from multiprocessing import Lock
from test import getheaders
from utils import get_path

print_lock = Lock()

cwd = os.getcwd()

colorama.init(autoreset=True)

console = Console()

task_log_list = []




SUCCESSFUL = 0
FAILED = 0

def updateStatusBar(success=False):
    global SUCCESSFUL
    global FAILED

    if success == True:
        SUCCESSFUL += 1
    elif success == False:
        FAILED += 1
    change_title(f"Bot - Avatar Changer / Successful: {str(SUCCESSFUL)} - Failed: {str(FAILED)}")


class Changer:
    def __init__(self, task, i):
        config = Config()
        self.task = task
        self.taskId = f"Task-{i}"

        self.webhook_url = config["webhook_url"]

        if ":" in task.split(";")[0]:
            self.token = self.task.split(";")[0].split(":")[2]
        else:
            self.token = self.task.split(";")[0]
        self.password = self.task.split(";")[0].split(":")[1]

        self.proxy = self.task.split(";")[1]



        try:
            if "@" in self.proxy:
                self.http_proxy = self.proxy
            else:
                self.split = self.proxy.split(':')
                good_format = (f'{self.split[2]}:{self.split[3]}@{self.split[0]}:{self.split[1]}')
                self.http_proxy = f"{good_format}"
            proxies = {
                "http": f"http://{self.http_proxy}",
                "https": f"http://{self.http_proxy}"
            }
        except:
            print("Please check your Proxy", flush=True)
            time.sleep(2)
            sys.exit()

        self.s = requests.Session()
        self.s.proxies.update(proxies)

        try:

            r = self.s.get("https://discord.com/ios/129.0/manifest.json", headers={
                "Host": "discord.com",
                "Accept": "*/*",
                "User-Agent": "Discord/129.0 (iPhone; iOS 15.4.1; Scale/3.00)",
                "Accept-Language": "de-DE;q=1, en-GB;q=0.9",
                "Accept-Encoding": "gzip",
                "Connection": "keep-alive"
            })
            
            self.cookies = r.cookies.get_dict()


            self.headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/102.0.0.0 Safari/537.36",
                "Accept": "*/*",
                "Accept-Language": "en-US,en;q=0.5",
                "Authorization": self.token,
                "X-Super-Properties": "eyJvcyI6IldpbmRvd3MiLCJicm93c2VyIjoiQ2hyb21lIiwiZGV2aWNlIjoiIiwic3lzdGVtX2xvY2FsZSI6ImVuLVVTIiwiYnJvd3Nlcl91c2VyX2FnZW50IjoiTW96aWxsYS81LjAgKFdpbmRvd3MgTlQgMTAuMDsgV2luNjQ7IHg2NCkgQXBwbGVXZWJLaXQvNTM3LjM2IChLSFRNTCwgbGlrZSBHZWNrbykgQ2hyb21lLzEwMi4wLjAuMCBTYWZhcmkvNTM3LjM2IiwiYnJvd3Nlcl92ZXJzaW9uIjoiMTAyLjAuMC4wIiwib3NfdmVyc2lvbiI6IjEwIiwicmVmZXJyZXIiOiJodHRwczovL3d3dy5nb29nbGUuY29tLyIsInJlZmVycmluZ19kb21haW4iOiJ3d3cuZ29vZ2xlLmNvbSIsInNlYXJjaF9lbmdpbmUiOiJnb29nbGUiLCJyZWZlcnJlcl9jdXJyZW50IjoiIiwicmVmZXJyaW5nX2RvbWFpbl9jdXJyZW50IjoiIiwicmVsZWFzZV9jaGFubmVsIjoic3RhYmxlIiwiY2xpZW50X2J1aWxkX251bWJlciI6MTMyMzIwLCJjbGllbnRfZXZlbnRfc291cmNlIjpudWxsfQ==",
                "X-Discord-Locale": "en-US",
                "X-Debug-Options": "bugReporterEnabled",
                "Origin": "https://discord.com",
                "Referer": "https://discord.com/channels/@me/",
                "Content-Type": "application/json",
                "Sec-Fetch-Dest": "empty",
                "Sec-Fetch-Mode": "cors",
                "Sec-Fetch-Site": "same-origin",
            }
        except Exception as e:
            self.exitTask(f"Error while building headers - {e}")

        self.changer()


    def error(self, text):
        spaces = 3 - len(self.taskId)
        MESSAGE = '[{}] [{}{}] {}'.format(Fore.MAGENTA + datetime.now().strftime('%H:%M:%S.%f') + Style.RESET_ALL,
                                          ' ' * spaces, Fore.RED + self.taskId + Style.RESET_ALL, Fore.RED + text)
        print_lock.acquire()
        print(MESSAGE, Style.RESET_ALL)
        print_lock.release()


    def success(self, text):
        spaces = 3 - len(self.taskId)
        MESSAGE = '[{}] [{}{}] {}'.format(Fore.MAGENTA + datetime.now().strftime('%H:%M:%S.%f') + Style.RESET_ALL,
                                          ' ' * spaces, Fore.GREEN + self.taskId + Style.RESET_ALL, Fore.GREEN + text)
        print_lock.acquire()
        print(MESSAGE, Style.RESET_ALL)
        print_lock.release()

    def status(self, text):
        spaces = 3 - len(self.taskId)
        MESSAGE = '[{}] [{}{}] {}'.format(Fore.MAGENTA + datetime.now().strftime('%H:%M:%S.%f') + Style.RESET_ALL,
                                          ' ' * spaces, self.taskId, text)
        print_lock.acquire()
        print(MESSAGE, Style.RESET_ALL)
        print_lock.release()


    def exitTask(self, error):
        self.error(error)
        updateStatusBar(success=False)
        return

    def SuccessfulTask(self):
        self.success("Successful changed avatar")
        updateStatusBar(success=True)
        return

    def delete_clipped(self):
        old_row = self.task.split(";")[0] + ";" + self.task.split(";")[1]
        with open(get_path("tokens.txt"), "r") as f:
            lines = f.readlines()
        with open(get_path("tokens.txt"), "w") as f:
            for line in lines:
                if line.strip("\n") != old_row:
                    f.write(line)
        f.close()



    def changer(self):
        def send_json_request(ws, request):
            try:
                ws.send(json.dumps(request))
            except Exception as e:
                self.error(f"Error while sending - {str(e)}")
                sys.exit()

        def receive_json_response(ws):
            try:
                response = ws.recv()
                if response:
                    return json.loads(response)
            except websocket._exceptions.WebSocketConnectionClosedException:
                self.error(f"Error while receiving - Check if your token is valid.")
                sys.exit()
            except Exception as e:
                self.error(f"Error while receiving - {str(e)}")
                sys.exit()

        def heartbeat(ws, interval):
            heartbeatJSON = {"op": 1, "d": "null"}
            send_json_request(ws, heartbeatJSON)



        ws = websocket.WebSocket()

        try:

            ws.connect("wss://gateway.discord.gg/?v=6&encording=json", http_proxy_host=self.split[0],
                        http_proxy_port=self.split[1],
                        proxy_type="http",
                        http_proxy_auth=(self.split[2], self.split[3]))
            # this is the username and password
        except websocket._exceptions.WebSocketAddressException:
            self.error("Error while connecting - Check your internet connection.")
        except Exception as e:
            self.error(f"Error while connecting - {str(e)}")

        event = receive_json_response(ws)

        payload_event = {"op": 2,
                            "d": {"token": self.token, "properties": {"$os": "linux", "$browser": "chrome", "$device": "pc"}}}

        heartbeat_interval = event["d"]["heartbeat_interval"] / 1000 - 5

        heartbeat(ws, heartbeat_interval)
        send_json_request(ws, payload_event)


        from base64 import b64encode
        avatars = [f for f in os.listdir(get_path('Data\Images')) if os.path.isfile(os.path.join("Data\Images", f))]
        with open(get_path(f'Data\Images\{random.choice(avatars)}'), "rb") as image_file:
            encoded_string = str(base64.b64encode(image_file.read())).replace("b'", "").replace("'", "")
        avatar = f"data:image/png;base64,{encoded_string}"
        r = self.s.patch("https://discord.com/api/v9/users/@me", headers=self.headers, json={"avatar": avatar}, cookies=self.cookies)
        if r.status_code == 200:
            self.SuccessfulTask()
        elif "USERNAME_RATE_LIMIT" in r.text:
            self.exitTask("Rate limit - you are changing too fast")
        elif "Unauthorized" in r.text:
            self.delete_clipped()
            self.exitTask("Token Clipped")
        else:
            print(r.text)
            self.exitTask("Error while changing avatar")


def main():
    change_title("Bot - Avatar Changer")
    global counter
    counter = 0

    config = Config()
    threads = config["threads"]
    amount = int(input(" Amount: "))

    x = check_user_proxy()
    tasks = []
    y = 1


    try:
        if int(len(x)) == 0:
            console.print("Not enough tokens")
            time.sleep(2)
            sys.exit()
        else:
            pass

        # row = random.choice(x)
        for row in x:
            if row not in tasks:
                tasks.append(f"{row}")
    except IndexError:
        print("Not enough tokens")
        return
    except Exception as e:
        print(f"Error while getting tokens - {e}")
        time.sleep(2)
        sys.exit()

    task_list = tasks[:amount]


    p = mp.Pool(int(threads))
    p.map(worker, task_list)
    p.close()
    p.join()

    print()
    print(f'{Fore.MAGENTA}Avatar Changer / Successful: {SUCCESSFUL} - Failed: {FAILED}')
    input(f'{Fore.LIGHTGREEN_EX}Entering done, press Enter to go back ')
    time.sleep(1)



def worker(tasks):
    global counter
    counter += 1
    Changer(tasks, counter)





#if __name__ == "__main__":
#    main()

    #print()
    #print(f'{Fore.MAGENTA}Invite Joiner / Successful: {SUCCESSFUL} - Failed: {FAILED}')
    #input(f'{Fore.LIGHTGREEN_EX}Entering done, press Enter to go back ')
    #time.sleep(1)

