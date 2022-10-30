import discum
import re
import sys
import time
import multiprocessing.dummy as mp
from traceback import print_tb
import requests
from rich.console import Console
import colorama
from colorama import Fore, Style
from datetime import datetime
import os
from dhooks import Webhook, Embed
from requests.exceptions import ProxyError
from utils import change_title
from utils import Config
from utils import check_user_proxy
from utils import get_path
from multiprocessing import Lock

print_lock = Lock()

cwd = os.getcwd()

colorama.init(autoreset=True)

console = Console()


SUCCESSFUL = 0
FAILED = 0


def updateStatusBar(success=False):
    global SUCCESSFUL
    global FAILED
    SUCCESSFUL = 0
    FAILED = 0

    if success == True:
        SUCCESSFUL += 1
    elif success == False:
        FAILED += 1
    change_title(f"Bot - AIO Monitor / Successful: {str(SUCCESSFUL)} - Failed: {str(FAILED)}")


class Joiner:
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
                http_proxy = self.proxy
            else:
                split = self.proxy.split(':')
                good_format = (f'{split[2]}:{split[3]}@{split[0]}:{split[1]}')
                http_proxy = f"{good_format}"
            proxies = {
                "http": f"http://{http_proxy}",
                "https": f"http://{http_proxy}"
            }
        except:
            self.error("Please check your Proxy")
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
        self.urls = self.task.split(";")[2]
        self.guild_id = self.urls.split("/")[4]
        self.channel_id = self.urls.split("/")[5]
        try:
            self.status("Scraping...")
            discord = discum.Client(token=self.token, log=False, proxy=f"http://{http_proxy}")
            discord.gateway.log = False

            def close(resp, guild_id):
                if discord.gateway.finishedMemberFetching(guild_id):
                    discord.gateway.removeCommand({'function': close, 'params': {'guild_id': guild_id}})
                    discord.gateway.close()

            def fetch(guild_id, channel_id):
                discord.gateway.fetchMembers(guild_id, channel_id, keep='all', wait=.1)
                discord.gateway.command({'function': close, 'params': {'guild_id': guild_id}})
                discord.gateway.run()
                discord.gateway.resetSession()
                return discord.gateway.session.guild(guild_id).members

            members_list = fetch(str(self.guild_id), str(self.channel_id))
            read = []

            i = 0


            for IDS in members_list:
                i += 1
                if IDS not in read:
                    if members_list[IDS]["bot"] == False:
                        read.append(IDS)
                        user_id = IDS
                        avatar = members_list[IDS]["avatar"]
                        username = members_list[IDS]["username"]
                        usernames = open(get_path("Data/Usernames/usernames.txt"), "r", encoding='utf-8').readlines()
                        if username.replace("\n", "")+"\n" not in usernames:
                            save_user = open(get_path("Data/Usernames/usernames.txt"), "a", encoding='utf-8')
                            save_user.write(username.replace("\n", "")+"\n")
                            save_user.close()


                        user_information = self.s.get(f"https://discord.com/api/v9/users/{user_id}/profile", headers=self.headers).json()
                        try:
                            bio = user_information['user']['bio']
                            bios = open(get_path("Data/Bios/bios.txt"), "r", encoding='utf-8').readlines()
                            if bio != "":
                                if bio.replace("\n", "")+"\n" not in bios:
                                    save_bio = open(get_path("Data/Bios/bios.txt"), "a", encoding='utf-8')
                                    save_bio.write(bio.replace("\n", "")+"\n")
                                    save_bio.close()
                        except:
                            pass
                        try:
                            if os.path.exists(get_path(f"Data/Images/{user_id}.png")) == False:
                                open(get_path(f"Data/Images/{user_id}.png"), "wb").write(self.s.get(f"https://cdn.discordapp.com/avatars/{user_id}/{avatar}.png?size=512").content)
                                import cv2

                                image = cv2.imread(get_path(f"Data/Images/{user_id}.png"))
                            
                                if image is None:
                                    try: 
                                        os.remove(get_path(f"Data/Images/{user_id}.png"))
                                    except: 
                                        pass
                                else:
                                    pass
                        except:
                            pass
                        self.success(f"[{i}/{len(members_list)}] Scraped info")
            self.SuccessfulTask()       
        except Exception as e:
            if "Access denied" in str(e):
                self.exitTask(f"Error while scraping - Cloudflare Rate Limited")
            else:
                self.exitTask("Error while scraping")
            




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

    def delete_clipped(self):
        old_row = self.task.split(";")[0] + ";" + self.task.split(";")[1]
        with open(get_path("tokens.txt"), "r") as f:
            lines = f.readlines()
        with open(get_path("tokens.txt"), "w") as f:
            for line in lines:
                if line.strip("\n") != old_row:
                    f.write(line)
        f.close()

    def exitTask(self, error):
        self.error(error)
        updateStatusBar(success=False)
        return

    def SuccessfulTask(self):
        self.success("Successful Scraped")
        updateStatusBar(success=True)
        return

def main():
    change_title("Bot - Scraper")
    global counter
    counter = 0
    config = Config()

    url = input(" Link: ")

    x = check_user_proxy()
    tasks = []
    try:
        if int(len(x)) == 0:
            print("Not enough tokens")
            time.sleep(2)
            sys.exit()
        else:
            pass

 
        tasks.append(x[0]+";"+url)


    except IndexError:
        print("Not enough tokens")
    except Exception as e:
        print(f"Error while getting tokens - {e}")
        time.sleep(2)
        sys.exit()
    
    worker(tasks)

    print()
    print(f'{Fore.MAGENTA}Scraper / Successful: {SUCCESSFUL} - Failed: {FAILED}')
    input(f'{Fore.LIGHTGREEN_EX}Scraping done, press Enter to go back ')
    time.sleep(1)


def worker(tasks):
    global counter
    counter += 1
    Joiner(tasks, counter)