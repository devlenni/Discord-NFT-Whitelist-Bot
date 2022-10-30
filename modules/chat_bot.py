import random
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


SUCCESSFUL = 0
FAILED = 0


def updateStatusBar(success=False):
    global SUCCESSFUL
    global FAILED

    if success == True:
        SUCCESSFUL += 1
    elif success == False:
        FAILED += 1
    change_title(f"Bot - Invite Joiner / Successful: {str(SUCCESSFUL)} - Failed: {str(FAILED)}")

def level_data():
    level_data = {
        "1": {"level_1": 7},
        "2": {"level_2": 17},
        "3": {"level_3": 32},
        "4": {"level_4": 52},
        "5": {"level_5": 77},
        "6": {"level_6": 109},
        "7": {"level_7": 147},
        "8": {"level_8": 194},
        "9": {"level_9": 248},
        "10": {"level_10": 312},
        "11": {"level_11": 334},
        "12": {"level_12": 352},
        "13": {"level_13": 423},
        "14": {"level_14": 503},
        "15": {"level_15": 592},
        "16": {"level_16": 690},
        "17": {"level_17": 800},
        "18": {"level_18": 919},
        "19": {"level_19": 1050},
        "20": {"level_20": 1193},
        "21": {"level_21": 1348},
        "22": {"level_22": 1516},
        "23": {"level_23": 1697},
        "24": {"level_24": 1891},
        "25": {"level_25": 2101},
        "26": {"level_26": 2324},
        "27": {"level_27": 2563},
        "28": {"level_28": 2818},
        "29": {"level_29": 3089},
        "30": {"level_30": 3377}
    }
    return level_data


class ChatBot:
    def __init__(self, task, i):
        self.config = Config()
        self.task = task
        self.taskId = f"Task-{i}"

        if self.config["chatbot_webhook"] != "":
            self.webhook_url = self.config["chatbot_webhook"]
        else:
            self.webhook_url = self.config["webhook_url"]

        if self.config["chatbot_delay"] != "":
            self.delay = self.config["chatbot_delay"]
        else:
            self.delay = self.config["delay"]

        self.cap_provider = self.config["cap_provider"]
        self.cap_api_key = self.config["cap_api_key"]

        if ":" in task.split(";")[0]:
            self.token = self.task.split(";")[0].split(":")[2]
        else:
            self.token = self.task.split(";")[0]

        self.proxy = self.task.split(";")[1]
        self.url = self.task.split(";")[2]
        self.guild_id = self.url.split("/")[4]
        self.channel_id = self.url.split("/")[5]

        self.send_messages = self.task.split(";")[3]

        self.chat_name = self.task.split(";")[4]

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
            print("Please check your Proxy")
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

        if self.config["chatbot_dialog_mode"] == "true":
            self.status("Starting Dialog Mode")
            self.dialog_mode_delay = self.config["chatbot_dialog_mode_delay"]
            self.dialog_mode_messages = self.config["chatbot_dialog_mode_messages"]
            self.send_once = self.config["chatbot_dialog_mode_send_once"]
            if self.send_once == "true":
                self.send_once = True
            else:
                self.send_once = False
            self.dialog_mode()
        else:
            self.status("Starting Chat Bot")
            self.chat_bot()


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
        #self.sendToDiscord(isSuccess=False)
        sys.exit()

    def SuccessfulTask(self):
        updateStatusBar(success=True)
        #self.sendToDiscord(isSuccess=True)
        return

    def retry(self, timeout, payload, answer, last_message):
        send_message_url = f"https://discord.com/api/v9/channels/{self.channel_id}/messages"
        try:
            time.sleep(timeout)
            r = self.s.post(send_message_url, headers=self.headers, json=payload)

            if r.status_code == 200:
                last_message.append(f"{answer} - My Message")
                self.status("Successful sent message")
                self.messages_sent += 1
            elif r.json()["code"] == 10008:
                self.error("Unknown Message")
            elif r.json()["code"] == 40002:
                self.error("Account got clipped!")
            elif r.json()["code"] == 20016:
                retry = r.json()["retry_after"]
                self.status(f"Slowmode rate limit, waiting {retry}")
                time.sleep(retry)
            else:
                self.error("Error while sending message")
        except Exception as e:
            self.error(f"Error while retry - {e}")
            pass

    def dialog_mode_send_message(self, url, payload):
        r = self.s.post(url, headers=self.headers, json=payload)
        if r.status_code == 200:
            self.status("Successful sent message")
            self.messages_sent += 1

        elif r.json()["code"] == 10008:
            self.error("Unknown Message")
        elif r.json()["code"] == 40002:
            self.error("Account got clipped!")
        elif r.json()["code"] == 20016:
            timeout = r.json()["retry_after"]
            time.sleep(timeout)
            while r.status_code != 200:
                r = self.s.post(url, headers=self.headers, json=payload)
                if r.status_code == 200:
                    self.status("Successful sent message")
                    self.messages_sent += 1
                    break

                elif r.json()["code"] == 10008:
                    self.error("Unknown Message")
                    break
                elif r.json()["code"] == 40002:
                    self.error("Account got clipped!")
                    break
                elif r.json()["code"] == 20016:
                    timeout = r.json()["retry_after"]
                    self.status(f"Slowmode rate limit, waiting {timeout}")
                    time.sleep(timeout)
                else:
                    self.error(f"Error while sending message - {r.text}")
                    break
        else:
            self.error(f"Error while sending message - {r.text}")


    def dialog_mode(self):
        self.messages_sent = 0
        last_messages = []
        reached_level = []
        messages_sent = []
        get_messages_url = f"https://discord.com/api/v9/channels/{self.channel_id}/messages?limit={self.dialog_mode_messages}"
        send_message_url = f"https://discord.com/api/v9/channels/{self.channel_id}/messages"

        first_run = 0

        while self.messages_sent < int(self.send_messages):
            try:
                for level in level_data().keys():
                    if self.messages_sent == level_data()[level]["level_" + level]:
                        if "level_"+level not in reached_level:
                            self.success(f"This account is now level {level}")
                            reached_level.append("level_"+level)

                r = self.s.get(get_messages_url, headers=self.headers)
                if r.status_code == 401:
                    self.delete_clipped()
                    self.exitTask(f"This token got clipped - {self.token}")
                    break
                elif "Missing Access" in r.text:
                    self.exitTask("Make sure you joined the server or verified correctly")
                    break
                if first_run == 0:
                    for data in r.json():
                        last_messages.append(data)
                    first_run += 1
                else:
                    pass
                for data in r.json():
                    if data["content"] not in last_messages:
                        content = data["content"]

                        last_messages.append(content)

                        import csv

                        with open(get_path(f"Chats\{self.chat_name}.csv")) as csv_file:
                            csv_reader = csv.reader(csv_file, delimiter=',')
                            line_count = 0
                            for row in csv_reader:
                                if line_count == 0:
                                    line_count += 1
                                else:
                                    line_count += 1

                                    if ";" in row[1]:
                                        answer_list = row[1].split(";")
                                        answer = random.choice(answer_list)
                                    else:
                                        answer = row[1]

                                    if "<USER>" in answer:
                                        author_id = data["user"]["id"]
                                        answer = answer.replace("<USER>", f"<@{author_id}>")

                                    # if str(row[0]).lower() == content.lower():
                                    if str(row[0]).lower() == content.lower():
                                        if row[3] != "":
                                            if data["author"]["id"] == str(row[3]):
                                                if row[2] == "true":

                                                    p1 = {
                                                        "content": answer,
                                                        "nonce": None,
                                                        "tts": False,
                                                        "message_reference": {
                                                            "guild_id": self.guild_id,
                                                            "channel_id": data["channel_id"],
                                                            "message_id": data["id"]
                                                        },
                                                        "allowed_mentions": {
                                                            "parse": ["users", "roles", "everyone"],
                                                            "replied_user": False
                                                        }
                                                    }
                                                    if self.send_once == True:
                                                        if answer not in messages_sent:
                                                            self.dialog_mode_send_message(send_message_url, p1)
                                                            last_messages.append(answer)
                                                            time.sleep(self.dialog_mode_delay)
                                                        else:
                                                            pass
                                                    else:
                                                        self.dialog_mode_send_message(send_message_url, p1)
                                                        time.sleep(self.dialog_mode_delay)

                                                else:
                                                    payload = {"content": answer, "nonce": None, "tts": False}

                                                    if self.send_once == True:
                                                        if answer not in messages_sent:
                                                            self.dialog_mode_send_message(send_message_url, payload)
                                                            last_messages.append(answer)
                                                            time.sleep(self.dialog_mode_delay)
                                                        else:
                                                            pass
                                                    else:
                                                        self.dialog_mode_send_message(send_message_url, payload)
                                                        time.sleep(self.dialog_mode_delay)



                                        else:
                                            if row[2] == "true":

                                                p2 = {
                                                    "content": answer,
                                                    "nonce": None,
                                                    "tts": False,
                                                    "message_reference": {
                                                        "guild_id": self.guild_id,
                                                        "channel_id": data["channel_id"],
                                                        "message_id": data["id"]
                                                    },
                                                    "allowed_mentions": {
                                                        "parse": ["users", "roles", "everyone"],
                                                        "replied_user": False
                                                    }
                                                }
                                                if self.send_once == True:
                                                    if answer not in messages_sent:
                                                        self.dialog_mode_send_message(send_message_url, p2)
                                                        last_messages.append(answer)
                                                        time.sleep(self.dialog_mode_delay)
                                                    else:
                                                        pass
                                                else:
                                                    self.dialog_mode_send_message(send_message_url, p2)
                                                    time.sleep(self.dialog_mode_delay)
                                            else:
                                                payload = {"content": answer, "nonce": None, "tts": False}
                                                if self.send_once == True:
                                                    if answer not in messages_sent:
                                                        self.dialog_mode_send_message(send_message_url, payload)
                                                        last_messages.append(answer)
                                                        time.sleep(self.dialog_mode_delay)
                                                    else:
                                                        pass
                                                else:
                                                    self.dialog_mode_send_message(send_message_url, payload)
                                                    time.sleep(self.dialog_mode_delay)
                                    else:
                                        last_messages.append(data["content"])
            except ProxyError:
                self.error("Proxy Error, retrying")
                self.dialog_mode()
            except Exception as e:
                self.exitTask("Error - {}, stopping".format(str(e)))
            time.sleep(self.delay)


    def chat_bot(self):
        self.messages_sent = 0
        get_messages_url = f"https://discord.com/api/v9/channels/{self.channel_id}/messages?limit=100"

        send_message_url = f"https://discord.com/api/v9/channels/{self.channel_id}/messages"

        last_message = []

        r = self.s.get(get_messages_url, headers=self.headers)
        if r.status_code == 401:
            self.delete_clipped()
            self.exitTask(f"This token got clipped - {self.token}")
        elif "Missing Access" in r.text:
            self.exitTask("Make sure you joined the server or verified correctly")
        content = r.json()[0]["content"]
        last_message.append(content)
        # x = 0
        # from extra.utils import q_and_a
        reached_level = []

        while self.messages_sent < int(self.send_messages):
            for level in level_data().keys():
                if self.messages_sent == level_data()[level]["level_" + level]:
                    if "level_"+level not in reached_level:
                        self.success(f"This account is now level {level}")
                        reached_level.append("level_"+level)


            r = self.s.get(get_messages_url, headers=self.headers)
            data = r.json()[0]
            content = data["content"]

            if self.config["chatbot_message_log"]:
                if self.config["chatbot_message_log"] == "true":
                    self.status(f"Last message: {last_message[-1]}")
                else:
                    pass
            else:
                pass

            try:
                if content != last_message[-1]:
                    if self.config["chatbot_message_log"]:
                        if self.config["chatbot_message_log"] == "true":
                            self.status(f"New Message: {content}")
                        else:
                            pass
                    else:
                        pass

                    last_message.append(content)

                    # for i in q_and_a():
                    #    q = list(i.keys())[0]
                    #    qs = q.split(",")
                    #    a = list(i.values())[0]
                    # if x == 0:

                    import csv

                    with open(get_path(f"Chats\{self.chat_name}.csv")) as csv_file:
                        csv_reader = csv.reader(csv_file, delimiter=',')
                        line_count = 0
                        for row in csv_reader:
                            if line_count == 0:
                                line_count += 1
                            else:
                                line_count += 1

                                if ";" in row[1]:
                                    answer_list = row[1].split(";")
                                    answer = random.choice(answer_list)
                                else:
                                    answer = row[1]

                                if "<USER>" in answer:
                                    author_id = data["user"]["id"]
                                    answer = answer.replace("<USER>", f"<@{author_id}>")

                                # if str(row[0]).lower() == content.lower():
                                if str(row[0]).lower() == content.lower():
                                    if row[3] != "":
                                        if data["author"]["id"] == str(row[3]):
                                            if row[2] == "true":

                                                url = f"https://discord.com/api/v9/channels/{self.channel_id}/messages"
                                                p1 = {
                                                    "content": answer,
                                                    "nonce": None,
                                                    "tts": False,
                                                    "message_reference": {
                                                        "guild_id": self.guild_id,
                                                        "channel_id": data["channel_id"],
                                                        "message_id": data["id"]
                                                    },
                                                    "allowed_mentions": {
                                                        "parse": ["users", "roles", "everyone"],
                                                        "replied_user": False
                                                    }
                                                }
                                                r = self.s.post(url, headers=self.headers, json=p1)

                                                if r.status_code == 200:
                                                    last_message.append(f"{answer} - My Message")
                                                    self.status("Successful sent message")
                                                    self.messages_sent += 1
                                                elif r.json()["code"] == 10008:
                                                    self.error("Unknown Message")
                                                elif r.json()["code"] == 40002:
                                                    self.error("Account got clipped!")
                                                elif r.json()["code"] == 20016:
                                                    timeout = r.json()["retry_after"]
                                                    self.status(f"Slowmode rate limit, waiting {timeout}")
                                                    self.retry(timeout, p1, answer, last_message)
                                                else:
                                                    self.error("Error while sending message")
                                                time.sleep(2)


                                            else:

                                                payload = {"content": answer, "nonce": None, "tts": False}
                                                r = self.s.post(send_message_url, headers=self.headers, json=payload)
                                                if r.status_code == 200:
                                                    last_message.append(f"{answer} - My Message")
                                                    self.status("Successful sent message")
                                                    self.messages_sent += 1
                                                elif r.json()["code"] == 10008:
                                                    self.error("Unknown Message")
                                                elif r.json()["code"] == 40002:
                                                    self.error("Account got clipped!")
                                                elif r.json()["code"] == 20016:
                                                    timeout = r.json()["retry_after"]
                                                    self.status(f"Slowmode rate limit, waiting {timeout}")
                                                    self.retry(timeout, payload, answer, last_message)
                                                else:
                                                    self.error("Error while sending message")
                                                time.sleep(2)




                                    else:
                                        if row[2] == "true":

                                            url = f"https://discord.com/api/v9/channels/{self.channel_id}/messages"
                                            p2 = {
                                                "content": answer,
                                                "nonce": None,
                                                "tts": False,
                                                "message_reference": {
                                                    "guild_id": self.guild_id,
                                                    "channel_id": data["channel_id"],
                                                    "message_id": data["id"]
                                                },
                                                "allowed_mentions": {
                                                    "parse": ["users", "roles", "everyone"],
                                                    "replied_user": False
                                                }
                                            }
                                            r = self.s.post(url, headers=self.headers, json=p2)

                                            if r.status_code == 200:
                                                last_message.append(f"{answer} - My Message")
                                                self.status("Successful sent message")
                                                self.messages_sent += 1
                                            elif r.json()["code"] == 10008:
                                                self.error("Unknown Message")
                                            elif r.json()["code"] == 40002:
                                                self.error("Account got clipped!")
                                            elif r.json()["code"] == 20016:
                                                timeout = r.json()["retry_after"]
                                                self.status(f"Slowmode rate limit, waiting {timeout}")
                                                self.retry(timeout, p2, answer, last_message)
                                            else:
                                                self.error("Error while sending message")
                                            time.sleep(1)

                                        else:
                                            payload = {"content": answer, "nonce": None, "tts": False}
                                            r = self.s.post(send_message_url, headers=self.headers, json=payload)
                                            if r.status_code == 200:
                                                last_message.append(f"{answer} - My Message")
                                                self.status("Successful sent message")
                                                self.messages_sent += 1
                                            elif r.json()["code"] == 10008:
                                                self.error("Unknown Message")
                                            elif r.json()["code"] == 40002:
                                                self.error("Account got clipped!")
                                            elif r.json()["code"] == 20016:
                                                timeout = r.json()["retry_after"]
                                                self.status(f"Slowmode rate limit, waiting {timeout}")
                                                self.retry(timeout, payload, answer, last_message)
                                            else:
                                                self.error("Error while sending message")
                                            time.sleep(1)

                                else:
                                    pass



            except ProxyError:
                self.exitTask("Proxy Error, stopping task")
                self.chat_bot()
            except Exception as e:
                self.exitTask("Error - {}, stopping".format(str(e)))
            time.sleep(self.delay)





def main():
    change_title("Bot - Chat Bot")
    global counter
    counter = 0
    config = Config()
    if config["chatbot_threads"] != "":
        threads = config["chatbot_threads"]
    else:
        threads = config["threads"]


    url = input(" Link: ")
    level_messages = input(" Level: ")
    for level in level_data().keys():
        if level_messages == level:
            send_messages = str(level_data()[level]["level_" + level])
    amount = int(input(" Amount: "))

    x = check_user_proxy()
    tasks = []
    y = 1


    try:
        if amount > int(len(x)):
            print("Not enough tokens")
            time.sleep(2)
            sys.exit()
        else:
            pass

        for row in x:
            if row not in tasks:
                tasks.append(f"{row};{url};{send_messages}")
            else:
                pass

    except IndexError:
        print("Not enough tokens")
    except Exception as e:
        print(f"Error while getting tokens - {e}")
        time.sleep(2)
        sys.exit()

    new_list = []
    task_list = tasks[:amount]
    for i in task_list:
        chat_name = input(f" Token-{y} Chatname: ")
        new_list.append(f"{i};{chat_name}")
        y += 1


    p = mp.Pool(int(threads))
    p.map(worker, new_list)
    p.close()
    p.join()




def worker(tasks):
    global counter
    counter += 1
    ChatBot(tasks, counter)







