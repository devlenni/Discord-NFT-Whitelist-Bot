import sys
import time
import multiprocessing.dummy as mp
import requests
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
    change_title(f"Bot - Manual Browser / Successful: {str(SUCCESSFUL)} - Failed: {str(FAILED)}")


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

        self.manual_browser()


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


    def manual_browser(self):
        try:
            from seleniumwire import webdriver
            options = {
                'proxy': {
                    'http': f'http://{self.http_proxy}',
                    'https': f'https://{self.http_proxy}',
                }
            }
            from test import getheaders

            j = self.s.get("https://discord.com/api/v9/users/@me", headers=getheaders(self.token)).json()
            user = j["username"] + "#" + str(j["discriminator"])
            script = """
                                                            document.body.appendChild(document.createElement `iframe`).contentWindow.localStorage.token = `"%s"`
                                                            location.reload();
                                                        """ % (self.token)


            opts = webdriver.ChromeOptions()
            opts.add_experimental_option('excludeSwitches', ['disable-logging'])
            opts.add_experimental_option("excludeSwitches", ["enable-automation"])
            opts.add_experimental_option("detach", True)
            opts.add_experimental_option('useAutomationExtension', False)
            opts.add_argument(
                "user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/101.0.4951.64 Safari/537.36")
            opts.add_argument("--disable-blink-features")
            opts.add_argument("--disable-blink-features=AutomationControlled")
            try:
                driver = webdriver.Chrome(options=opts, seleniumwire_options=options)
                driver.delete_all_cookies()
            except common.exceptions.SessionNotCreatedException as e:
                self.exitTask("Proxy Error, stopping task")
                return


            self.status(f"Logging into - {user}")
            driver.get("https://discord.com/login")
            driver.execute_script(script)

            input("Press any key for next token")
            driver.close()
            driver.delete_all_cookies()


        except Exception as e:
            self.exitTask("Error - {}, stopping".format(str(e)))


def main():
    change_title("Bot - Manual Browser")
    global counter
    counter = 0

    config = Config()
    threads = config["threads"]

    x = check_user_proxy()
    tasks = []
    y = 0


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

    p = mp.Pool(int(threads))
    p.map(worker, tasks)
    p.close()
    p.join()




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

