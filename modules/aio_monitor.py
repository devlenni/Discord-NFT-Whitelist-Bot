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

        if config["giveaway_webhook"] != "":
            self.webhook_url = config["giveaway_webhook"]
        else:
            self.webhook_url = config["webhook_url"]

        if config["giveaway_delay"] != "":
            self.delay = config["giveaway_delay"]
        else:
            self.delay = config["delay"]

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

        self.last_message = []

        self.monitor()


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
        self.success("Successful Joined Giveaway")
        updateStatusBar(success=True)
        return

    
    def check_game_winner(self, data, profile_username):

        try:
            giveaway_link = re.search("(?P<url>https?://[^\s]+)",
                                      data["embeds"][0]["description"]).group(
                "url").replace(">)", "")
        except:
            giveaway_link = "/"
        hook = Webhook(self.webhook_url)
        embed = Embed(
            description='\n',
            color=7484927,
            timestamp='now',
            title="You won a game!"
        )
        embed.add_field(name='**Content**', value=data["content"], inline=False)
        embed.add_field(name='**Message Link**', value=f"[LINK]({giveaway_link})",
                        inline=True)
        embed.add_field(name='**Token**', value="||" + self.token + "||",
                        inline=False)
        embed.add_field(name='**Username**', value="||" + profile_username + "||",
                        inline=False)
        embed.set_footer(text=f'Bot',
                         icon_url='')
        try:
            hook.send(embed=embed)
        except:
            self.error("Error while sending webhook")




    def join_game(self, data, guild_name, channel_name):
        reaction = data["reactions"][0]["emoji"]["name"] + ":" + data["reactions"][0]["emoji"]["id"]
        channel_id = data["channel_id"]
        message_id = data["id"]
        r = self.s.put(
            f"https://discord.com/api/v9/channels/{channel_id}/messages/{message_id}/reactions/{reaction}/@me?location=Message",
            headers=self.headers)
        if r.status_code == 204:
            self.success(f"[{guild_name}] [{channel_name}] Successful joined game")

        elif "40002" in r.text:
            self.delete_clipped()
            self.exitTask(f"This token got clipped - {self.token}")
        else:
            self.error(f"[{guild_name}] [{channel_name}] Error while joining game")


    def check_winner(self, data, profile_username):
        try:
            giveaway_link = re.search("(?P<url>https?://[^\s]+)",
                                      data["embeds"][0]["description"]).group(
                "url").replace(">)", "")
        except:
            giveaway_link = "/"
        hook = Webhook(self.webhook_url)
        embed = Embed(
            description='\n',
            color=7484927,
            timestamp='now',
            title="You won a giveaway!"
        )
        embed.add_field(name='**Content**', value=data["content"], inline=False)
        embed.add_field(name='**Message Link**', value=f"[LINK]({giveaway_link})",
                        inline=True)
        embed.add_field(name='**Token**', value="||" + self.token + "||",
                        inline=False)
        embed.add_field(name='**Username**', value="||" + profile_username + "||",
                        inline=False)
        embed.set_footer(text=f'Bot',
                         icon_url='')
        try:
            hook.send(embed=embed)
        except:
            self.error("Error while sending webhook")


    def join(self, data, guild_name, channel_name):
        try: 
            reaction = data["reactions"][0]["emoji"]["name"]
            channel_id = data["channel_id"]
            message_id = data["id"]
            r = self.s.put(
                f"https://discord.com/api/v9/channels/{channel_id}/messages/{message_id}/reactions/{reaction}/@me",
                headers=self.headers)
            if r.status_code == 204:
                self.success(f"[{guild_name}] [{channel_name}] Successful joined giveaway")

            elif "40002" in r.text:
                self.exitTask(f"This token got clipped - {self.token}")
            else:
                self.error(f"[{guild_name}] [{channel_name}] Error while joining giveaway")
        except:
            pass

    def join_button_based(self, i, guild_name, channel_name, guild_id):
        try:
            options = i['components'][0]['components']
            for option in options:
                if "enter" in str(option["custom_id"]).lower():
                    custom_id = option["custom_id"]
                    message_id = i["id"]
                    channel_id = i["channel_id"]
                    application_id = i["author"]["id"]
                    click_payload = {
                        "type": 3,
                        "nonce": None,
                        "guild_id": guild_id,
                        "channel_id": channel_id,
                        "message_flags": 0,
                        "message_id": message_id,
                        "application_id": application_id,
                        "session_id": "6158c76c341e1e0773db7d1d1eb36c31",
                        "data": {
                            "component_type": 2,
                            "custom_id": custom_id
                        }
                    }

                    url = "https://discord.com/api/v9/interactions"

                    r = self.s.post(url, headers=self.headers, json=click_payload)
                    if r.status_code == 204:
                        self.success(f"[{guild_name}] [{channel_name}] Successful joined giveaway")
                    elif "40002" in r.text:
                        self.exitTask(f"This token got clipped - {self.token}")
                    else:
                        self.error(f"[{guild_name}] [{channel_name}] Error while joining giveaway")
        except:
            pass



    def monitor(self):
        already_read = []
        already_read.append([23234234234, 234234234234])
        self.status("Started monitoring")

        guilds = self.s.get('https://discord.com/api/v9/users/@me/guilds', headers=self.headers)
        while True:
            try:
                for guild in guilds.json():
                    guild_name = guild["name"]
                    guild_id = guild["id"]
                    channels = self.s.get(f'https://discord.com/api/v9/guilds/{guild["id"]}/channels', headers=self.headers)
                    for channel in channels.json():
                        channel_name = channel["name"]
                        channel_id = channel["id"]
                        messages = self.s.get(f"https://discord.com/api/v9/channels/{channel_id}/messages?limit=10", headers=self.headers)
                        for message in messages.json():
                            if message["id"] not in already_read:
                                try:
                                    if message["author"]["username"] == "GiveawayBot":
                                    #if "giveaway" in str(message["author"]["username"]).lower():
                                        if message["embeds"] and "react with" and "to enter!" in str(message["embeds"][0]["description"]).lower():
                                            already_read.append(message["id"])
                                            self.status(f"[{guild_name}] [{channel_name}] Found a giveaway")
                                            self.join(message, guild_name, channel_name)
                                        elif message["embeds"] and message["components"]:
                                            if "entries" and "winners" in str(message["embeds"][0]["description"]).lower():
                                                already_read.append(message["id"])
                                                self.status(f"[{guild_name}] [{channel_name}] Found a giveaway")
                                                self.join_button_based(message, guild_name, channel_name, guild_id)
                                        elif "congratulations" or "you won" in str(message).lower():
                                            already_read.append(message["id"])
                                            profile_url = "https://discord.com/api/v9/users/@me"
                                            try:
                                                r = self.s.get(profile_url, headers=self.headers)
                                                profile_id = r.json()["id"]
                                                profile_username = r.json()["username"]
                                                for mention in message["mentions"]:
                                                    if profile_id in mention["id"]:
                                                        self.success(f"[{guild_name}] [{channel_name}] You won a giveaway - {profile_username}")
                                                    self.check_winner(message, profile_username)
                                            except:
                                                pass

                                        else:
                                            already_read.append(message["id"])
                                except KeyError:
                                    pass

                                try:
                                    if message["author"]["username"] == "Rumble Royale":
                                        if message["embeds"] and "Click the emoji below to join" in message["embeds"][0]["description"]:
                                            already_read.append(message["id"])
                                            self.status(f"[{guild_name}] [{channel_name}] Found a game")
                                            self.join_game(message, guild_name, channel_name)
                                        elif "winner" in str(message).lower():
                                            already_read.append(message["id"])
                                            profile_url = "https://discord.com/api/v9/users/@me"
                                            try:
                                                r = self.s.get(profile_url, headers=self.headers)
                                                profile_id = r.json()["id"]
                                                profile_username = r.json()["username"]
                                                for mention in message["mentions"]:
                                                    if profile_id in mention["id"]:
                                                        self.success(f"[{guild_name}] [{channel_name}] You won a game - {profile_username}")
                                                    self.check_winner(message, profile_username)
                                            except:
                                                pass
                                        else:
                                            already_read.append(message["id"])
                                except KeyError:
                                    pass
                time.sleep(self.delay)
            except TypeError:
                print(channels.text)
                if "You are being rate limited" in channels.json():
                    retry_delay = channels.json()["retry_after"]
                    time.sleep(retry_delay)

def main():
    change_title("WHITELISTERZ - AIO Monitor")
    global counter
    counter = 0
    config = Config()
    if config["giveaway_threads"] != "":
        threads = config["giveaway_threads"]
    else:
        threads = config["threads"]


    amount = int(input(" Amount: "))

    x = check_user_proxy()
    tasks = []
    try:
        if int(amount) > int(len(x)):
            print("Not enough tokens")
            time.sleep(2)
            sys.exit()
        else:
            pass

        for row in x:
            if row not in tasks:
                tasks.append(row)
            else:
                pass

    except IndexError:
        print("Not enough tokens")
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
    print(f'{Fore.MAGENTA}AIO Monitor / Successful: {SUCCESSFUL} - Failed: {FAILED}')
    input(f'{Fore.LIGHTGREEN_EX}Entering done, press Enter to go back ')
    time.sleep(1)


def worker(tasks):
    global counter
    counter += 1
    Joiner(tasks, counter)






