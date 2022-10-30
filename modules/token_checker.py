import sys
import time
import multiprocessing.dummy as mp
import requests
from Crypto.SelfTest.Hash import common
from selenium import common
from rich.console import Console
import colorama
from colorama import Fore, Style
from datetime import datetime
import os
from utils import change_title
from utils import Config
from utils import check_user_proxy
from multiprocessing import Lock
from utils import get_path
from test import getheaders


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
    change_title(f"Bot - Token Checker / Successful: {str(SUCCESSFUL)} - Failed: {str(FAILED)}")


class Checker:
    def __init__(self, task, i):
        config = Config()
        self.task = task
        self.taskId = f"Task-{i}"

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

        self.headers = {
            "Authorization": self.token,
            "accept": "*/*",
            "accept-language": "en-US",
            "connection": "keep-alive",
            "cookie": f'__cfduid={os.urandom(43).hex()}; __dcfduid={os.urandom(32).hex()}; locale=en-US',
            "DNT": "1",
            "origin": "https://discord.com",
            "sec-fetch-dest": "empty",
            "sec-fetch-mode": "cors",
            "sec-fetch-site": "same-origin",
            "referer": "https://discord.com/channels/@me",
            "TE": "Trailers",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) discord/1.0.9001 Chrome/83.0.4103.122 Electron/9.3.5 Safari/537.36",
            "X-Super-Properties": "eyJvcyI6IldpbmRvd3MiLCJicm93c2VyIjoiRGlzY29yZCBDbGllbnQiLCJyZWxlYXNlX2NoYW5uZWwiOiJzdGFibGUiLCJjbGllbnRfdmVyc2lvbiI6IjEuMC45MDAxIiwib3NfdmVyc2lvbiI6IjEwLjAuMTkwNDIiLCJvc19hcmNoIjoieDY0Iiwic3lzdGVtX2xvY2FsZSI6ImVuLVVTIiwiY2xpZW50X2J1aWxkX251bWJlciI6ODMwNDAsImNsaWVudF9ldmVudF9zb3VyY2UiOm51bGx9"
        }

        self.checker()


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
        self.success("Token Working")
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



    def checker(self):
        try:
            self.status("Checking Token")

            headers = {"authorization": self.token}
            r = self.s.get("https://discordapp.com/api/v6/auth/login", headers=headers)
            if r.status_code in [200, 201, 204]:
                self.SuccessfulTask()
            else:
                self.delete_clipped()
                self.exitTask("Token Clipped")
        except Exception as e:
            self.exitTask("Error - {}, stopping".format(str(e)))


def main():
    change_title("Bot - Token Checker")
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




def worker(tasks):
    global counter
    counter += 1
    Checker(tasks, counter)





#if __name__ == "__main__":
#    main()

    #print()
    #print(f'{Fore.MAGENTA}Invite Joiner / Successful: {SUCCESSFUL} - Failed: {FAILED}')
    #input(f'{Fore.LIGHTGREEN_EX}Entering done, press Enter to go back ')
    #time.sleep(1)

