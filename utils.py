import json
import platform, os
#from pypresence import Presence
import time
import sys
import random
from datetime import datetime

import requests


def activity_webhook(module, license, user):
    try:
        x = dict(db.child("Licenses").get().val())
        for i in x:
            if x[i]["license"] == license:
                user = x[i]["user"]
    except:
        user = "/"

    webhook = "https://discord.com/api/webhooks/..."

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/93.0.4577.82 Safari/537.36",
        "Accept": "application/json"
    }

    webhookData = {
        "content": None,
        "embeds": [
            {
                "title": f"User Started {module}",
                "color": 3447003,
                "fields": [
                    {
                        "name": "Module",
                        "value": f"{module}"
                    },
                    {
                        "name": "User",
                        "value": user
                    },
                    {
                        "name": "License",
                        "value": f"||{license}||"
                    }
                ]
            }
        ]
    }
    requests.post(webhook, json=webhookData, headers=headers)


def get_path(file):
    if getattr(sys, 'frozen', False):
        application_path = os.path.dirname(sys.executable)
    elif __file__:
        application_path = os.path.dirname(__file__)

    path = os.path.join(application_path, file)
    return path


def delay_split(delay):
    if delay == "":
        return ""
    elif "-" in delay:
        delay_list = delay.split("-")
        inf = delay_list[0]
        sup = delay_list[1]
        try:
            inf = int(inf)
            sup = int(sup)
            delay = int(random.randint(inf, sup))
        except:
            print("Error while getting delays, stopping")
            time.sleep(10)
            sys.exit()
    else:
        delay = int(delay)
    return delay

def Config():
    try:
        import json

        with open(get_path("config.json"), "r") as config_file:
            data = json.load(config_file)

        delay = delay_split(data["user_settings"]["delay"])
        license = data["user_settings"]["license_key"]
        webhook = data["user_settings"]["webhook_url"]
        threads = data["user_settings"]["thread_count"]

        provider = data["captcha_settings"]["provider"]
        api_key = data["captcha_settings"]["api_key"]

        giveaway_webhook = data["giveaway_joiner_settings"]["webhook_url"]
        giveaway_delay = delay_split(data["giveaway_joiner_settings"]["delay"])
        giveaway_threads = data["giveaway_joiner_settings"]["thread_count"]

        joiner_webhook = data["invite_joiner_settings"]["webhook_url"]
        joiner_delay = delay_split(data["invite_joiner_settings"]["delay"])
        joiner_threads = data["invite_joiner_settings"]["thread_count"]

        chatbot_webhook = data["chat_bot_settings"]["webhook_url"]
        chatbot_delay = delay_split(data["chat_bot_settings"]["delay"])
        chatbot_threads = data["chat_bot_settings"]["thread_count"]
        chatbot_message_log = data["chat_bot_settings"]["show_message_log"]
        chatbot_dialog_mode = data["chat_bot_settings"]["dialog_mode"]["use_mode"]
        chatbot_dialog_mode_delay = delay_split(data["chat_bot_settings"]["dialog_mode"]["delay"])
        chatbot_dialog_mode_messages = data["chat_bot_settings"]["dialog_mode"]["messages"]
        chatbot_dialog_mode_send_once = data["chat_bot_settings"]["dialog_mode"]["send_once"]

        return {
            "delay": delay, "webhook_url": webhook, "license": license, "threads": threads,
            "cap_provider": provider, "cap_api_key": api_key,
            "giveaway_webhook": giveaway_webhook, "giveaway_delay": giveaway_delay, "giveaway_threads": giveaway_threads,
            "joiner_webhook": joiner_webhook, "joiner_delay": joiner_delay, "joiner_threads": joiner_threads,
            "chatbot_webhook": chatbot_webhook, "chatbot_delay": chatbot_delay, "chatbot_threads": chatbot_threads,
            "chatbot_message_log": chatbot_message_log, "chatbot_dialog_mode": chatbot_dialog_mode,
            "chatbot_dialog_mode_delay": chatbot_dialog_mode_delay, "chatbot_dialog_mode_messages": chatbot_dialog_mode_messages,
            "chatbot_dialog_mode_send_once": chatbot_dialog_mode_send_once
        }
    except Exception as e:
        print(f"Error while reading config file, stopping - {e}")
        time.sleep(10)
        sys.exit()


class Logger:
    def invite_joiner_logger(self, log_list):
        now = datetime.now()
        dt_string = now.strftime("%d-%m-%Y-%H-%M-%S")
        filename = f"Log/Invite Joiner/InviteJoiner-{dt_string}.json"
        with open(get_path(filename), 'a') as file:
            json.dump(log_list, file, indent=4)


#def change_title(title):
#    if platform.system().lower() != "darwin":
#        os.system("title " + title)
#    else:
#        pass

def change_title(title):
	if (os.name == "nt"):
		os.system("title " + title)
	else:
		print(f"\33]0;{title}\a", end='', flush=True)

"""
	clearConsole()
		clear Console
"""

def clear():
	if (os.name == "nt"):
		os.system("cls")
	else:
		os.system("clear")


def delete_proxy(proxy):
    with open(get_path("proxies.txt"), "r") as f:
        lines = f.readlines()
    with open(get_path("proxies.txt"), "w") as f:
        for line in lines:
            if line.strip("\n") != proxy:
                f.write(line)
    f.close()


def read_tokens():
    try:
        with open(get_path("tokens.txt"), "r", encoding="utf-8") as file:
            accounts = [line.strip() for line in file.readlines() if bool(line.strip())]
            return accounts
    except FileNotFoundError:
        print("Cannot find tokens.txt")
        return None


def write_fixed_tokens(accounts: list[str]) -> None:
    with open(get_path("tokens.txt"), "w", encoding="utf-8") as file:
        for account in accounts:
            file.write(account + "\n")


def read_proxies():
    try:
        with open(get_path("proxies.txt"), "r", encoding="utf-8") as file:
            proxies = [line.strip() for line in file.readlines() if bool(line.strip())]
            return proxies
    except FileNotFoundError:
        print("Cannot find proxies.txt")
        return None

def check_if_proxy_in_use(proxy: str, accounts: list[str], fixed_accounts: list[str]) -> bool:
    for account in accounts and fixed_accounts:
        if proxy in account:
            return True
    return False

def check_user_proxy() -> None:
    accounts = read_tokens()
    proxies = read_proxies()
    fixed_accounts = []
    for account in accounts:
        if ";" in account:
            to_append = account
        elif len(account) > 32:
            while 1:
                try:
                    proxy = random.choice(proxies)
                    delete_proxy(proxy)
                except IndexError:
                    print("Not enough proxies...")
                    return sys.exit()
                if check_if_proxy_in_use(proxy, accounts, fixed_accounts):
                    proxies.remove(proxy)
                    continue
                break
            to_append = f"{account};{proxy}"
        elif len(account.split(":")) == 3:
            while 1:
                try:
                    proxy = random.choice(proxies)
                    delete_proxy(proxy)
                except IndexError:
                    print("Not enough proxies...")
                    return sys.exit()
                if check_if_proxy_in_use(proxy, accounts, fixed_accounts):
                    proxies.remove(proxy)
                    continue
                break
            to_append = f"{account};{proxy}"
        else:
            to_append = account
        fixed_accounts.append(to_append)
    write_fixed_tokens(fixed_accounts)

    return read_tokens()


#def change_title(title):
#    if platform.system().lower() != "darwin":
#        title = title + " - Solana balance : {}".format(get_solana_balance())
#        os.system("title {}".format(title))
#    else:
#        pass












