import sys
import time
import multiprocessing.dummy as mp
import requests
from rich.console import Console
import colorama
from colorama import Fore, Style
from datetime import datetime
import os
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
    change_title(f"Bot - Message Scraper / Successful: {str(SUCCESSFUL)} - Failed: {str(FAILED)}")


class Scraper:
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
        self.url = self.task.split(";")[2]
        self.channel_id = self.url.split("/")[5]


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

        self.scrape()


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
        self.success("Successful Scraped")
        updateStatusBar(success=True)
        return

    def scrape(self):
        try:
            self.status('Scraping Messages')
            get_messages_url = f"https://discord.com/api/v9/channels/{self.channel_id}/messages?limit=100"

            r = self.s.get(get_messages_url, headers=self.headers)
            if r.status_code == 200:
                data = r.json()

                messages = []
                for i in data:
                    if i["content"]:
                        try:
                            messages.append(f'{i["content"]}\n')
                        except:
                            pass

                now = datetime.now()
                dt_string = now.strftime("%d-%m-%Y-%H-%M-%S")
                filename = f"Utils/Message Scraper/Scraped-{dt_string}.txt"
                with open(get_path(filename), 'a', ) as f_object:
                    f_object.writelines(messages)
                    f_object.close()

                self.SuccessfulTask()

            elif "40002" in r.text:
                self.error(f"This token got clipped - {self.token}")
            elif r.status_code == 401:
                self.error(f"This token got clipped - {self.token}")
            else:
                self.error(f"Error while scraping messages")

        except ProxyError:
            self.error("Proxy Error, retrying")
            self.scrape()
        except Exception as e:
            self.exitTask("Error while scraping messages - {}, stopping".format(str(e)))


def main():
    change_title("Bot - Message Scraper")
    global counter
    counter = 0

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

        # row = random.choice(x)
        # for row in x:
        # if row not in tasks:
        tasks.append(x[0] + ";" + url)
        # y += 1
    except IndexError:
        print("Not enough tokens")
        return
    except Exception as e:
        print(f"Error while getting tokens - {e}")
        time.sleep(2)
        sys.exit()

    p = mp.Pool(1)
    p.map(worker, tasks)
    p.close()
    p.join()


    print()
    print(f'{Fore.MAGENTA}Message Scraper / Successful: {SUCCESSFUL} - Failed: {FAILED}')
    input(f'{Fore.LIGHTGREEN_EX}Entering done, press Enter to go back ')
    time.sleep(1)


def worker(tasks):
    global counter
    counter += 1
    Scraper(tasks, counter)





#if __name__ == "__main__":
#    main()

    #print()
    #print(f'{Fore.MAGENTA}Invite Joiner / Successful: {SUCCESSFUL} - Failed: {FAILED}')
    #input(f'{Fore.LIGHTGREEN_EX}Entering done, press Enter to go back ')
    #time.sleep(1)
