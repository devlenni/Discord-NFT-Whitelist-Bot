import sys
import uuid
from base64 import b64encode as encoder
import time
import multiprocessing.dummy as mp
import websocket, json
import requests
from PIL import Image
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
from utils import Logger
from utils import get_path
from multiprocessing import Lock

print_lock = Lock()

cwd = os.getcwd()

colorama.init(autoreset=True)

console = Console()

task_log_list = []


def log_list(invite):
    log_list = {
        "Invite": invite,
        "Tasks": task_log_list
    }
    return log_list

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


class Joiner:
    def __init__(self, task, i):
        config = Config()
        self.task = task
        self.taskId = f"Task-{i}"

        if config["joiner_webhook"] != "":
            self.webhook_url = config["joiner_webhook"]
        else:
            self.webhook_url = config["webhook_url"]

        if config["joiner_delay"] != "":
            self.delay = config["joiner_delay"]
        else:
            self.delay = config["delay"]

        self.cap_provider = config["cap_provider"]
        self.cap_api_key = config["cap_api_key"]

        if ":" in task.split(";")[0]:
            self.token = self.task.split(";")[0].split(":")[2]
        else:
            self.token = self.task.split(";")[0]

        self.proxy = self.task.split(";")[1]
        self.invite = self.task.split(";")[2]

        try:
            if "@" in self.proxy:
                http_proxy = self.proxy
            else:
                self.split = self.proxy.split(':')
                good_format = (f'{self.split[2]}:{self.split[3]}@{self.split[0]}:{self.split[1]}')
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
            fingerprint = self.s.get("https://discord.com/api/v9/experiments", headers={
                "Host": "discord.com",
                "x-debug-options": "bugReporterEnabled",
                "Accept": "*/*",
                "x-discord-locale": "de",
                "Accept-Encoding": "gzip, deflate, br",
                "Accept-Language": "de-DE,en-GB;q=0.9",
                "x-context-properties": "eyJsb2NhdGlvbiI6Ii8ifQ==",
                "User-Agent": "Discord/32871 CFNetwork/1331.0.7 Darwin/21.4.0",
                "x-super-properties": "eyJvcyI6ImlPUyIsImJyb3dzZXIiOiJEaXNjb3JkIGlPUyIsImRldmljZSI6ImlQaG9uZTE0LDUiLCJzeXN0ZW1fbG9jYWxlIjoiZGUtREUiLCJjbGllbnRfdmVyc2lvbiI6IjEyOS4wIiwicmVsZWFzZV9jaGFubmVsIjoic3RhYmxlIiwiZGV2aWNlX3ZlbmRvcl9pZCI6IkZFNERCQzVFLTE5QzUtNEEzQi05QTg2LTBBQzY3N0I0Mzk1NiIsImJyb3dzZXJfdXNlcl9hZ2VudCI6IiIsImJyb3dzZXJfdmVyc2lvbiI6IiIsIm9zX3ZlcnNpb24iOiIxNS40LjEiLCJjbGllbnRfYnVpbGRfbnVtYmVyIjozMzAwOCwiY2xpZW50X2V2ZW50X3NvdXJjZSI6bnVsbH0=",
                "Connection": "keep-alive",
                "Cookie": f"__dcfduid={dcfduid}; __sdcfduid={sdcfduid}"
            }).json()["fingerprint"]

            self.headers = {
                "Host": "discord.com",
                "x-debug-options": "bugReporterEnabled",
                "Accept": "*/*",
                "Authorization": self.token,
                "x-discord-locale": "de",
                "Accept-Encoding": "gzip, deflate, br",
                "Accept-Language": "de-DE,en-GB;q=0.9",
                "x-context-properties": "eyJsb2NhdGlvbiI6IkFjY2VwdCBJbnZpdGUgUGFnZSJ9",
                "x-fingerprint": fingerprint,
                "User-Agent": "Discord/32871 CFNetwork/1331.0.7 Darwin/21.4.0",
                "x-super-properties": "eyJvcyI6ImlPUyIsImJyb3dzZXIiOiJEaXNjb3JkIGlPUyIsImRldmljZSI6ImlQaG9uZTE0LDUiLCJzeXN0ZW1fbG9jYWxlIjoiZGUtREUiLCJjbGllbnRfdmVyc2lvbiI6IjEyOS4wIiwicmVsZWFzZV9jaGFubmVsIjoic3RhYmxlIiwiZGV2aWNlX3ZlbmRvcl9pZCI6IkZFNERCQzVFLTE5QzUtNEEzQi05QTg2LTBBQzY3N0I0Mzk1NiIsImJyb3dzZXJfdXNlcl9hZ2VudCI6IiIsImJyb3dzZXJfdmVyc2lvbiI6IiIsIm9zX3ZlcnNpb24iOiIxNS40LjEiLCJjbGllbnRfYnVpbGRfbnVtYmVyIjozMzAwOCwiY2xpZW50X2V2ZW50X3NvdXJjZSI6bnVsbH0=",
                "Connection": "keep-alive",
                "Cookie": f"__dcfduid={dcfduid}; __sdcfduid={sdcfduid}"
            }
        except Exception as e:
            self.exitTask(f"Error while building headers - {e}")

        print("""
        1. Auto Joiner
        2. Normal Joiner
        3. Exit 
        """)
        choice = int(input("Select >>> "))
        if choice == 3:
            sys.exit()
        elif choice == 1:
            self.join()
        elif choice == 2:
            links = input("Link(s): ")
            self.join_normal(links)


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


    def sendToDiscord(self, isSuccess):
        if self.webhook_url != "":
            hook = Webhook(self.webhook_url)
            embed = Embed(
                description='\n',
                color=7484927 if isSuccess else 16724787,
                timestamp='now',
                title="Successful Join" if isSuccess else "Failed Join"
            )
            embed.add_field(name='**Invite**', value="||" + self.invite + "||", inline=False)
            embed.add_field(name='**Token**', value="||" + self.token + "||", inline=False)
            embed.add_field(name='**Proxy**', value="||" + self.proxy + "||", inline=False)
            # embed.add_field(name='', value="")
            embed.set_footer(text=f'Bot',
                             icon_url='')
            try:
                self.status("Sending webhook")
                hook.send(embed=embed)
            except:
                self.error("Error while sending webhook")

    def exitTask(self, error, e=None):
        self.error(error)
        self.end = time.time()
        self.time = self.end - self.start
        self.log = {
            self.taskId: {
                "Time": f"Task took {round(self.time, 2)} seconds",
                "Token": self.token,
                "Proxy": self.proxy,
                "Status": "Failed",
                "Reason": e
            }
        }
        task_log_list.append(self.log)
        updateStatusBar(success=False)
        self.sendToDiscord(isSuccess=False)
        return

    def SuccessfulTask(self):
        self.end = time.time()
        self.time = self.end - self.start
        self.log = {
            self.taskId: {
                "Time": f"Task took {round(self.time, 2)} seconds",
                "Token": self.token,
                "Proxy": self.proxy,
                "Status": "Successful"
            }
        }
        task_log_list.append(self.log)
        updateStatusBar(success=True)
        self.sendToDiscord(isSuccess=True)
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

    def captcha(self):
        #self.status('Waiting for Captcha')
        #from modules.nocap import NoCap

        #solver = NoCap(api_key="96ec2f83b53874b66e0f285435eee7302009e11")
        #try:
        #    solution = solver.hcaptcha(mode=3, host="discord.com", sitekey="4c672d35-0701-42b2-88c3-78380b0db560",
        #                               proxy=f"http://{self.http_proxy}")
        #    print(solution)
        #    self.status('Successful solved captcha')
        #    return solution
        #except Exception as e:
        #    print(e)

        self.status('Waiting for Captcha')
        import captchatools
        solver = captchatools.captcha_harvesters(solving_site=self.cap_provider, api_key=self.cap_api_key,
                                                 sitekey="4c672d35-0701-42b2-88c3-78380b0db560",
                                                 captcha_type="hcaptcha",
                                                 captcha_url="www.discord.com")
        self.captcha_answer = solver.get_token()
        self.status('Successful solved captcha')
        return self.captcha_answer

    def captcha_bot_captcha(self):
        self.status('Waiting for Captcha')
        import captchatools
        solver = captchatools.captcha_harvesters(solving_site=self.cap_provider, api_key=self.cap_api_key,
                                                 sitekey="8223d1d4-b37a-46cc-b0e6-f9bf43658d5d",
                                                 captcha_type="hcaptcha",
                                                 captcha_url="https://captcha.bot/verify")
        self.captcha_answer = solver.get_token()
        self.status('Successful solved captcha')
        return self.captcha_answer

    def server_verify(self, r):
        try:
            if r.json()["show_verification_form"]:
                if r.json()["show_verification_form"] == True:
                    guild_id = r.json()["guild"]["id"]

                    r = self.s.get(f"https://discord.com/api/v9/guilds/{guild_id}/member-verification?with_guild=false&invite_code={self.invite}",headers=self.headers)
                    form_values = r.json()["form_fields"][0]["values"]
                    version = r.json()["version"]
                    description = r.json()["form_fields"][0]["description"]
                    field_type = r.json()["form_fields"][0]["field_type"]
                    label = r.json()["form_fields"][0]["label"]
                    automations = r.json()["form_fields"][0]["automations"]
                    required = r.json()["form_fields"][0]["required"]

                    payload = {"version": version, "form_fields": [
                        {"field_type": field_type, "label": label, "description": description,
                         "automations": automations, "required": required, "values": form_values,
                         "response": True}]}
                    r = self.s.put(f"https://discord.com/api/v9/guilds/{guild_id}/requests/@me", headers=self.headers,json=payload)
                    if "APPROVED" in r.text:
                        self.status("Accepted server rules")
                    elif "This user is already a member" in r.text:
                        pass
                    else:
                        self.error("Error while accepting server rules")
        except:
            pass

    def captcha_bot_verification(self, message, message_id, channel_id, guild_id):
        verified = 0

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

        try:
            if message['embeds']:
                if "verification required" in str(message['embeds'][0]['title']).lower():
                    custom_id = "panel_verify"
                    application_id = message["author"]["id"]


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

                    click_payload = {
                        "type": 3,
                        "nonce": None,
                        "guild_id": guild_id,
                        "channel_id": channel_id,
                        "message_flags": 0,
                        "message_id": message_id,
                        "application_id": application_id,
                        "session_id": "637f3bc722ac0a2f64d7b2cbfb0dd396",
                        "data": {
                            "component_type": 2,
                            "custom_id": custom_id
                        }
                    }

                    url = "https://discord.com/api/v9/interactions"

                    r = self.s.post(url, headers=self.headers, json=click_payload)
                    while True:
                        event = receive_json_response(ws)
                        try:
                            if str(event['d']['attachments']) == "[]":
                                if event['d']['author']['username'] == "Captcha.bot":
                                    if event['d']['embeds']:
                                        verify_url = event['d']['embeds'][0]['description'].split("(")[1].replace(")", "")
                                        server_id = verify_url.split("/")[5]
                                        url_hash = str(verify_url).split("/")[6]
                                        self.s.get(verify_url)

                                        r = self.s.get(f"https://captcha.bot/api/v1/captcha/{server_id}/{url_hash}", headers={
                                            "authorization": "null",
                                            "referer": verify_url,
                                            "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/101.0.4951.64 Safari/537.36",
                                        })

                                        r = self.s.get(
                                            "https://discord.com/api/oauth2/authorize?client_id=512333785338216465&redirect_uri=https://captcha.bot/callback&response_type=code&scope=identify",
                                            headers={
                                                "Upgrade-Insecure-Requests": "1",
                                                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/102.0.0.0 Safari/537.36"
                                            })

                                        r = self.s.get(
                                            "https://discord.com/api/v9/oauth2/authorize?client_id=512333785338216465&response_type=code&redirect_uri=https://captcha.bot/callback&scope=identify",
                                            headers=self.headers)

                                        r = self.s.post(
                                            "https://discord.com/api/v9/oauth2/authorize?client_id=512333785338216465&response_type=code&redirect_uri=https://captcha.bot/callback&scope=identify",
                                            headers=self.headers, json={"permissions": "0", "authorize": True})
                                        if r.status_code == 200:
                                            callback_url = r.json()["location"]
                                            callback_code = str(callback_url).split("=")[1]

                                            r = self.s.get(f"https://captcha.bot/callback?code={callback_code}", headers={
                                                "Upgrade-Insecure-Requests": "1",
                                                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/102.0.0.0 Safari/537.36"

                                            })

                                            r = self.s.post(f"https://captcha.bot/api/v1/oauth/callback?code={callback_code}", headers={
                                                "Connection": "keep-alive",
                                                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/102.0.0.0 Safari/537.36",
                                                "Authorization": "null"
                                            })
                                            if r.status_code == 200:
                                                login_token = r.json()["token"]

                                                r = self.s.get(f"https://captcha.bot/api/v1/captcha/{server_id}/{url_hash}", headers={
                                                    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/102.0.0.0 Safari/537.36",
                                                    "Authorization": login_token
                                                })

                                                cap_resp = self.captcha_bot_captcha()

                                                r = self.s.post("https://captcha.bot/api/v1/captcha/verify", headers={
                                                    "Authorization": login_token,
                                                    "Referer": verify_url,
                                                    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/102.0.0.0 Safari/537.36"
                                                }, json={
                                                    "guildID": server_id,
                                                    "hash": url_hash,
                                                    "token": cap_resp
                                                })

                                                if "ACKNOWLEDGED" in r.text:
                                                    self.success("Successful verified")
                                                    return
                                                elif "TRY_AGAIN" in r.text:
                                                    r = self.s.post("https://captcha.bot/api/v1/captcha/verify", headers={
                                                        "Authorization": login_token,
                                                        "Referer": verify_url,
                                                        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/102.0.0.0 Safari/537.36"
                                                    }, json={
                                                        "guildID": server_id,
                                                        "hash": url_hash,
                                                        "token": cap_resp
                                                    })

                                                    if "ACKNOWLEDGED" in r.text:
                                                        self.success("Successful verified")
                                                        return



                            else:
                                pass
                            continue
                        except:
                            pass
                        continue
        except Exception as e:
            self.error(f"Error while verification - Captcha.bot - {e}")

    def sledgehammer_verification(self, message, message_id, channel_id, guild_id):
        verified = 0

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


        try:
            if message['embeds']:
                if "verification required" in str(message['embeds'][0]['title']).lower():
                    custom_id = "startVerification.en"
                    application_id = message["author"]["id"]

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
                                     "d": {"token": self.token,
                                           "properties": {"$os": "linux", "$browser": "chrome",
                                                          "$device": "pc"}}}

                    heartbeat_interval = event["d"]["heartbeat_interval"] / 1000 - 5

                    heartbeat(ws, heartbeat_interval)
                    send_json_request(ws, payload_event)


                    click_payload = {
                        "type": 3,
                        "nonce": None,
                        "guild_id": guild_id,
                        "channel_id": channel_id,
                        "message_flags": 0,
                        "message_id": message_id,
                        "application_id": application_id,
                        "session_id": "5ed030d084797406de7fd7a602cf8f96",
                        "data": {
                            "component_type": 2,
                            "custom_id": custom_id
                        }
                    }

                    url = "https://discord.com/api/v9/interactions"

                    time.sleep(3)
                    r = self.s.post(url, headers=self.headers, json=click_payload)

                    while True:
                        event = receive_json_response(ws)
                        try:
                            if str(event['d']['attachments']) == "[]":
                                if event['d']['author']['username'] == "Sledgehammer":
                                    if event['d']['embeds']:
                                        if "verify" in str(event['d']['embeds'][0]['title']).lower():
                                            message_id = event['d']['id']
                                            channel_id = event['d']['channel_id']
                                            guild_id = event['d']['message_reference']['guild_id']
                                            application_id = event['d']['application_id']
                                            # nonce = event['d']['nonce']

                                            options = event['d']['components'][0]['components'][0]['options']
                                            for option in options:
                                                if str(option['value']).lower() in str(
                                                        event['d']['embeds'][0]['description']).lower():
                                                    answer = str(option['value']).lower()

                                                    reaction_payload = {
                                                        "type": 3,
                                                        "nonce": None,
                                                        "guild_id": guild_id,
                                                        "channel_id": channel_id,
                                                        "message_flags": 64,
                                                        "message_id": message_id,
                                                        "application_id": application_id,
                                                        "session_id": "429b98284e5d864be8aea65e35ee2cb2",
                                                        "data": {
                                                            "component_type": 3,
                                                            "custom_id": "verificationRequest.en",
                                                            "type": 3,
                                                            "values": [f"{answer}"]
                                                        }
                                                    }

                                                    url = "https://discord.com/api/v9/interactions"

                                                    r = self.s.post(url, headers=self.headers, json=reaction_payload)
                                                    self.success("Successful verified")
                                                    return

                            else:
                                pass
                            continue
                        except:
                            pass
                        continue
        except Exception as e:
            self.error(f"Error while verification - Sledgehammer - {e}")

    def wick_verification(self, message, message_id, channel_id, guild_id):
        if self.cap_provider != "2captcha":
            self.exitTask("Currently only 2captcha is supported for wick verification")
        else:
            try:
                if message['embeds']:
                    if "verification required" in str(message['embeds'][0]['title']).lower():
                        application_id = message["author"]["id"]
                        click_verify_url = "https://discord.com/api/v9/interactions"

                        payload = {
                            "type": 3, "nonce": None, "guild_id": guild_id,
                            "channel_id": channel_id, "message_flags": 0, "message_id": message_id,
                            "application_id": application_id, "session_id": "4a587abe3a045eac2d51fcaf3a858710",
                            "data": {
                                "component_type": 2, "custom_id": "v_911148730357522442_Z8lqex9Gzx"
                            }
                        }

                        self.s.post(click_verify_url, headers=self.headers, json=payload)

                        r = self.s.post("https://discord.com/api/v9/users/@me/channels", headers=self.headers,
                                        json={"recipients": ["548410451818708993"]})
                        dm_id = r.json()["id"]

                        time.sleep(3)
                        get_dm_url = f"https://discord.com/api/v9/channels/{dm_id}/messages?limit=50"
                        r = self.s.get(get_dm_url, headers=self.headers)

                        captcha_image = r.json()[0]["embeds"][0]["image"]["url"]

                        response = requests.get(captcha_image)

                        now = datetime.now()
                        dt_string = now.strftime("%H-%M-%S")
                        filename = f"wick_{dt_string}.png"
                        file = open(filename, "wb")
                        file.write(response.content)
                        file.close()

                        im = Image.open(filename)
                        im = im.convert("RGBA")

                        r1 = 50
                        g1 = 207
                        b1 = 126
                        r2 = 0
                        g2 = 191
                        b2 = 255

                        pixdata = im.load()

                        for y in range(im.size[1]):
                            for x in range(im.size[0]):
                                if pixdata[x, y] != (r1, g1, b1, 255) and pixdata[x, y] != (r2, g2, b2, 255):
                                    pixdata[x, y] = (0, 0, 0, 0)

                        im.save(filename)

                        from captcha2upload import CaptchaUpload

                        captcha = CaptchaUpload(self.cap_api_key)
                        captchakey = captcha.solve(filename)

                        import os
                        os.remove(filename)

                        payload1 = {"content": captchakey, "nonce": None, "tts": False}

                        send_message_url = f"https://discord.com/api/v9/channels/{dm_id}/messages"
                        self.s.post(send_message_url, headers=self.headers, json=payload1)

                        r = self.s.get(get_dm_url, headers=self.headers)
                        if "You have been verified!" in str(r.json()[0]):
                            self.success("Successful verified")
                        else:
                            self.exitTask("Error while verification")
            except KeyError:
                self.exitTask("Your account probably got a time out - Account Suspicious")
            except:
                self.exitTask("Error while verification!")

    def button_verification(self, message_data, message_id, channel_id, guild_id):
        try:
            components = message_data['components']
            for component in components:
                for option in component["components"]:
                    if "verify" or "agree" in str(option["label"]).lower():
                        custom_id = option["custom_id"]
                        application_id = message_data["author"]["id"]
                        click_payload = {
                            "type": 3,
                            "nonce": None,
                            "guild_id": guild_id,
                            "channel_id": channel_id,
                            "message_flags": 0,
                            "message_id": message_id,
                            "application_id": application_id,
                            "session_id": "5ed030d084797406de7fd7a602cf8f96",
                            "data": {
                                "component_type": 2,
                                "custom_id": custom_id
                            }
                        }

                        url = "https://discord.com/api/v9/interactions"

                        r = self.s.post(url, headers=self.headers, json=click_payload)
                        if r.status_code == 204:
                            self.success("Successful verified - Button")
                    else:
                        custom_id = option["custom_id"]
                        application_id = message_data["author"]["id"]
                        click_payload = {
                            "type": 3,
                            "nonce": None,
                            "guild_id": guild_id,
                            "channel_id": channel_id,
                            "message_flags": 0,
                            "message_id": message_id,
                            "application_id": application_id,
                            "session_id": "5ed030d084797406de7fd7a602cf8f96",
                            "data": {
                                "component_type": 2,
                                "custom_id": custom_id
                            }
                        }

                        url = "https://discord.com/api/v9/interactions"

                        r = self.s.post(url, headers=self.headers, json=click_payload)
                        if r.status_code == 204:
                            self.success("Successful verified - Button")
        except:
            pass

    def pandez_verification(self, message, message_id, channel_id, guild_id):
        verified = 0

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

        #try:
        if message['embeds']:
            if "to get full access" and "complete the following verification process" in str(message['embeds'][0]).lower():
                custom_id = "verify"
                application_id = message["author"]["id"]

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
                                 "d": {"token": self.token,
                                       "properties": {"$os": "linux", "$browser": "chrome",
                                                      "$device": "pc"}}}

                heartbeat_interval = event["d"]["heartbeat_interval"] / 1000 - 5


                click_payload = {
                    "type": 3,
                    "nonce": None,
                    "guild_id": guild_id,
                    "channel_id": channel_id,
                    "message_flags": 0,
                    "message_id": message_id,
                    "application_id": application_id,
                    "session_id": "fa131a36ae45e576496ef771b15d27f6",
                    "data": {
                        "component_type": 2,
                        "custom_id": custom_id
                    }
                }

                url = "https://discord.com/api/v9/interactions"

                heartbeat(ws, heartbeat_interval)
                send_json_request(ws, payload_event)
                r = self.s.post(url, headers=self.headers, json=click_payload)
                while True:
                    event = receive_json_response(ws)
                    try:
                        if str(event['d']['attachments']) == "[]":
                            if event['d']['author']['username'] == "Pandez Guard Beta":
                                r = self.s.patch("https://discord.com/api/v9/users/@me/settings", headers=self.headers, json={"restricted_guilds": [guild_id]})
                                message_id = event['d']['id']
                                print(message_id)
                                print(event['d'])
                                click_payload = {
                                    "type": 3,
                                    "nonce": None,
                                    "guild_id": guild_id,
                                    "channel_id": channel_id,
                                    "message_flags": 0,
                                    "message_id": message_id,
                                    "application_id": application_id,
                                    "session_id": "fa131a36ae45e576496ef771b15d27f6",
                                    "data": {
                                        "component_type": 2,
                                        "custom_id": "turnOffDMContinue"
                                    }
                                }
                                r = self.s.post(url, headers=self.headers, json=click_payload)
                                while True:
                                    event = receive_json_response(ws)
                                    if str(event['d']['attachments']) == "[]":
                                        if event['d']['author']['username'] == "Pandez Guard Beta":
                                            if event['d']['embeds']:
                                                if "read the rules" in str(event['d']['embeds']).lower():
                                                    message_id = event['d']['id']
                                                    click_payload = {
                                                        "type": 3,
                                                        "nonce": None,
                                                        "guild_id": guild_id,
                                                        "channel_id": channel_id,
                                                        "message_flags": 0,
                                                        "message_id": message_id,
                                                        "application_id": application_id,
                                                        "session_id": "fa131a36ae45e576496ef771b15d27f6",
                                                        "data": {
                                                            "component_type": 2,
                                                            "custom_id": "readRulesContinue"
                                                        }
                                                    }
                                                    r = self.s.post(url, headers=self.headers, json=click_payload)
                                                    while True:
                                                        event = receive_json_response(ws)
                                                        if str(event['d']['attachments']) == "[]":
                                                            if event['d']['author']['username'] == "Pandez Guard Beta":
                                                                if event['d']['embeds']:
                                                                    if "are you human" in str(event['d']['embeds']).lower():
                                                                        print(event['d'])


                    except:
                        pass
                    continue

                time.sleep(10000)

                while True:
                    event = receive_json_response(ws)
                    try:
                        if str(event['d']['attachments']) == "[]":
                            if event['d']['author']['username'] == "Sledgehammer":
                                if event['d']['embeds']:
                                    if "verify" in str(event['d']['embeds'][0]['title']).lower():
                                        message_id = event['d']['id']
                                        channel_id = event['d']['channel_id']
                                        guild_id = event['d']['message_reference']['guild_id']
                                        application_id = event['d']['application_id']
                                        # nonce = event['d']['nonce']

                                        options = event['d']['components'][0]['components'][0]['options']
                                        for option in options:
                                            if str(option['value']).lower() in str(
                                                    event['d']['embeds'][0]['description']).lower():
                                                answer = str(option['value']).lower()

                                                reaction_payload = {
                                                    "type": 3,
                                                    "nonce": None,
                                                    "guild_id": guild_id,
                                                    "channel_id": channel_id,
                                                    "message_flags": 64,
                                                    "message_id": message_id,
                                                    "application_id": application_id,
                                                    "session_id": "429b98284e5d864be8aea65e35ee2cb2",
                                                    "data": {
                                                        "component_type": 3,
                                                        "custom_id": "verificationRequest.en",
                                                        "type": 3,
                                                        "values": [f"{answer}"]
                                                    }
                                                }

                                                url = "https://discord.com/api/v9/interactions"

                                                r = self.s.post(url, headers=self.headers, json=reaction_payload)
                                                self.success("Successful verified")
                                                return

                        else:
                            pass
                        continue
                    except:
                        pass
                    continue
        #except Exception as e:
        #    self.error(f"Error while verification - Sledgehammer - {e}")

    def normal_verification(self, message_data, message_id, channel_id):
        try:
            if message_data["reactions"][0]["emoji"]["id"] != None:
                emoji_name = message_data["reactions"][0]["emoji"]["name"]
                emoji_id = message_data["reactions"][0]["emoji"]["id"]
                link = f"https://discord.com/api/v9/channels/{channel_id}/messages/{message_id}/reactions/{emoji_name}:{emoji_id}/@me?location=Message"
            else:
                emoji_name = message_data["reactions"][0]["emoji"]["name"]
                link = f"https://discord.com/api/v9/channels/{channel_id}/messages/{message_id}/reactions/{emoji_name}/@me?location=Message"
            r = self.s.put(link, headers=self.headers)
            if r.status_code == 204:
                self.success("Successful verified - Normal")
            elif "40002" in r.text:
                self.delete_clipped()
                self.exitTask(f"This token got clipped - {self.token}")
            elif "retry_after":
                timeout = r.json()["retry_after"]
                time.sleep(timeout)
                r = self.s.put(link, headers=self.headers)
                if r.status_code == 204:
                    verified = True
                    self.success("Successful verified - Normal")
                elif "40002" in r.text:
                    self.delete_clipped()
                    self.exitTask(f"This token got clipped - {self.token}")
                else:
                    self.exitTask("Error while verification")
            else:
                self.exitTask("Error while verification")
        except:
            pass

    def channel_verify(self, guild_id, channel_ids):
        verified = 0

        def react(reaction):
            try:
                r = self.s.put(f"https://discord.com/api/v9/channels/{channel_id}/messages/{message_id}/reactions/{reaction}/@me", headers=self.headers)
                if r.status_code == 204:
                    self.success("Successful verified - Normal")
                elif "40002" in r.text:
                    self.error(f"This token got clipped - {self.token}")
                else:
                    self.error("Error while verification")
            except:
                pass

        def dyno(message):
            try:
                options = message['components'][0]['components']
                for option in options:
                    custom_id = option["custom_id"]
                    message_id = message["id"]
                    channel_id = message["channel_id"]
                    application_id = message["author"]["id"]
                    click_payload = {
                        "type": 3,
                        "nonce": None,
                        "guild_id": guild_id,
                        "channel_id": channel_id,
                        "message_flags": 0,
                        "message_id": message_id,
                        "application_id": application_id,
                        "session_id": "5ed030d084797406de7fd7a602cf8f96",
                        "data": {
                            "component_type": 2,
                            "custom_id": custom_id
                        }
                    }

                    url = "https://discord.com/api/v9/interactions"

                    r = self.s.post(url, headers=self.headers, json=click_payload)
                    if r.status_code == 204:
                        self.success("Successful verified - Button")
            except:
                pass

        def button_verify(r, guild_id, show=True):
            try:
                for message in r.json():
                    if message["components"]:
                        message_id = message["id"]
                        channel_id = message["channel_id"]
                        application_id = message["author"]["id"]
                        components = message['components']
                        for component in components:
                            for option in component["components"]:
                                if "verify" in str(option["label"]).lower():
                                    custom_id = option["custom_id"]
                                    click_payload = {
                                        "type": 3,
                                        "nonce": None,
                                        "guild_id": guild_id,
                                        "channel_id": channel_id,
                                        "message_flags": 0,
                                        "message_id": message_id,
                                        "application_id": application_id,
                                        "session_id": "5ed030d084797406de7fd7a602cf8f96",
                                        "data": {
                                            "component_type": 2,
                                            "custom_id": custom_id
                                        }
                                    }

                                    url = "https://discord.com/api/v9/interactions"

                                    r = self.s.post(url, headers=self.headers, json=click_payload)
                                    if r.status_code == 204:
                                        if show == True:
                                            self.success("Successful verified - Button")
                                else:
                                    custom_id = option["custom_id"]
                                    click_payload = {
                                        "type": 3,
                                        "nonce": None,
                                        "guild_id": guild_id,
                                        "channel_id": channel_id,
                                        "message_flags": 0,
                                        "message_id": message_id,
                                        "application_id": application_id,
                                        "session_id": "5ed030d084797406de7fd7a602cf8f96",
                                        "data": {
                                            "component_type": 2,
                                            "custom_id": custom_id
                                        }
                                    }

                                    url = "https://discord.com/api/v9/interactions"

                                    r = self.s.post(url, headers=self.headers, json=click_payload)
                                    if r.status_code == 204:
                                        if show == True:
                                            self.success("Successful verified - Button")
                    elif message["reactions"]:
                        if message["reactions"][0]["emoji"]["id"] != None:
                            emoji_name = message["reactions"][0]["emoji"]["name"]
                            emoji_id = message["reactions"][0]["emoji"]["id"]
                            link = f"https://discord.com/api/v9/channels/{channel_id}/messages/{message_id}/reactions/{emoji_name}:{emoji_id}/@me?location=Message"
                        else:
                            emoji_name = message["reactions"][0]["emoji"]["name"]
                            link = f"https://discord.com/api/v9/channels/{channel_id}/messages/{message_id}/reactions/{emoji_name}/@me?location=Message"
                        r = self.s.put(link, headers=self.headers)
                        if r.status_code == 204:
                            if show == True:
                                self.success("Successful verified - Normal")
                        elif "40002" in r.text:
                            self.error(f"This token got clipped - {self.token}")
                        elif "retry_after":
                            timeout = r.json()["retry_after"]
                            time.sleep(timeout)
                            r = self.s.put(link, headers=self.headers)
                            if r.status_code == 204:
                                if show == True:
                                    self.success("Successful verified - Normal")
                            else:
                                if show == True:
                                    self.error("Error while verification")
                        else:
                            if show == True:
                                self.error("Error while verification")
                    else:
                        pass
            except:
                for message in r.json():
                    if message["reactions"][0]["emoji"]["id"] != None:
                        emoji_name = message["reactions"][0]["emoji"]["name"]
                        emoji_id = message["reactions"][0]["emoji"]["id"]
                        link = f"https://discord.com/api/v9/channels/{channel_id}/messages/{message_id}/reactions/{emoji_name}:{emoji_id}/@me?location=Message"
                    else:
                        emoji_name = message["reactions"][0]["emoji"]["name"]
                        link = f"https://discord.com/api/v9/channels/{channel_id}/messages/{message_id}/reactions/{emoji_name}/@me?location=Message"
                    r = self.s.put(link, headers=self.headers)
                    if r.status_code == 204:
                        if show == True:
                            self.success("Successful verified - Normal")
                    elif "40002" in r.text:
                        self.error(f"This token got clipped - {self.token}")
                    elif "retry_after":
                        timeout = r.json()["retry_after"]
                        time.sleep(timeout)
                        r = self.s.put(link, headers=self.headers)
                        if r.status_code == 204:
                            if show == True:
                                self.success("Successful verified - Normal")
                        else:
                            if show == True:
                                self.error("Error while verification")
                    else:
                        if show == True:
                            self.error("Error while verification")




        for channel_id in channel_ids:
            print(channel_ids)

            try:
                self.verified = False
                r = self.s.get(f"https://discord.com/api/v9/channels/{channel_id}/messages?limit=50",
                               headers=self.headers)
                r = self.s.get(f"https://discord.com/api/v9/channels/{channel_id}/messages?limit=50", headers=self.headers)
                for message in reversed(r.json()):
                    bot_name = message["author"]["username"]
                    if bot_name == "Pandez Guard Beta":
                        self.status("Verification detected - Pandez Guard")
                        message_id = message["id"]
                        self.pandez_verification(message, message_id, channel_id, guild_id)
                        self.verified = True
                        return
                    elif bot_name == "Wick":
                        self.status("Verification detected - Sledgehammer")
                        message_id = message["id"]
                        self.sledgehammer_verification(message, message_id, channel_id, guild_id)
                        self.verified = True
                        return
                    elif bot_name == "Sledgehammer":
                        self.status("Verification detected - Wick")
                        message_id = message["id"]
                        self.wick_verification(message, message_id, channel_id, guild_id)
                        self.verified = True
                        return
                    elif bot_name == "Captcha.bot":
                        self.status("Verification detected - Captcha.bot")
                        message_id = message["id"]
                        self.captcha_bot_verification(message, message_id, channel_id, guild_id)
                        self.verified = True
                        return
                    else:
                        words = ["verify", "verification", "verified", "react to this message", "react below", "access", "reaction button"]#, "show me your id"]
                        for word in words:
                            if word in str(message).lower():
                                if self.verified != 1:
                                    if word == "verify":
                                        self.status("Verification detected")
                                        message_id = message["id"]
                                        try:
                                            if message["components"]:
                                                self.button_verification(message, message_id, channel_id, guild_id)
                                            else:
                                                self.normal_verification(message, message_id, channel_id)
                                            self.verified = True
                                        except:
                                            pass

                                    elif word == "verification":
                                        self.status("Verification detected")
                                        message_id = message["id"]
                                        try:
                                            if message["components"]:
                                                self.button_verification(message, message_id, channel_id, guild_id)
                                            else:
                                                self.normal_verification(message, message_id, channel_id)
                                            self.verified = True
                                        except:
                                            pass


                                    elif word == "verified":
                                        self.status("Verification detected")
                                        message_id = message["id"]
                                        try:
                                            if message["components"]:
                                                self.button_verification(message, message_id, channel_id, guild_id)
                                            else:
                                                self.normal_verification(message, message_id, channel_id)
                                            self.verified = True
                                        except:
                                            pass

                                    elif word == "react to this message":
                                        self.status("Verification detected")
                                        message_id = message["id"]
                                        try:
                                            if message["components"]:
                                                self.button_verification(message, message_id, channel_id, guild_id)
                                            else:
                                                self.normal_verification(message, message_id, channel_id)
                                            self.verified = True
                                        except:
                                            pass

                                    elif word == "react below":
                                        self.status("Verification detected")
                                        message_id = message["id"]
                                        try:
                                            if message["components"]:
                                                self.button_verification(message, message_id, channel_id, guild_id)
                                            else:
                                                self.normal_verification(message, message_id, channel_id)
                                            self.verified = True
                                        except:
                                            pass

                                    elif word == "access":
                                        self.status("Verification detected")
                                        message_id = message["id"]
                                        try:
                                            if message["components"]:
                                                self.button_verification(message, message_id, channel_id, guild_id)
                                            else:
                                                self.normal_verification(message, message_id, channel_id)
                                            self.verified = True
                                        except:
                                            pass

                                    elif word == "reaction button":
                                        self.status("Verification detected")
                                        message_id = message["id"]
                                        try:
                                            if message["components"]:
                                                self.button_verification(message, message_id, channel_id, guild_id)
                                            else:
                                                self.normal_verification(message, message_id, channel_id)
                                            self.verified = True
                                        except:
                                            pass

                                    elif message["author"]["username"] == "Dyno":
                                        self.status("Verification detected")
                                        message_id = message["id"]
                                        try:
                                            if message["components"]:
                                                self.button_verification(message, message_id, channel_id, guild_id)
                                            else:
                                                self.normal_verification(message, message_id, channel_id)
                                            self.verified = True
                                        except:
                                            pass

                                    else:
                                        message_id = r.json()[0]["id"]
                                        try:
                                            if message["components"]:
                                                self.button_verification(message, message_id, channel_id, guild_id)
                                            else:
                                                self.normal_verification(message, message_id, channel_id)
                                            self.verified = True
                                        except:
                                            pass
                if self.verified == False:
                    self.status("No Verification detected")



            except:
                pass


    def get_verify_channels(self, r):
        try:
            guild_id = r.json()["guild"]["id"]
            url = f"https://discord.com/api/v9/guilds/{guild_id}/channels"
            r = self.s.get(url, headers=self.headers)
            channel_ids = []
            for i in r.json():
                #if "verify" in str(i["name"]).lower():
                #    channel_ids.append(i["id"])
                #elif "verification" in str(i["name"]).lower():
                #    channel_ids.append(i["id"])
                #else:
                #    pass
                channel_ids.append(i["id"])

            if channel_ids:
                return channel_ids
            else:
                self.status("No verify channel found")
                return None
        except Exception as e:
            self.exitTask("Error while getting channel - {}, stopping".format(str(e)))


    def join(self):
        self.status('Joining Invite')
        self.start = time.time()
        try:
            r = self.s.post(f'https://discord.com/api/v9/invites/{self.invite}', headers=self.headers)
            if r.status_code == 200:
                self.success("Successful Joined Server")
                self.server_verify(r)
                guild_id = r.json()["guild"]["id"]
                if self.get_verify_channels(r) != None:
                    self.channel_verify(guild_id, self.get_verify_channels(r))
                self.SuccessfulTask()

            elif "40002" in r.text:
                self.delete_clipped()
                self.exitTask(f"This token got clipped - {self.token}", e="Clipped")

            elif r.status_code == 401:
                self.delete_clipped()
                self.exitTask(f"This token got clipped - {self.token}", e="Clipped")

            elif "captcha_key" in r.text:
                captcha_answer = self.captcha()
                payload = {"captcha_key": captcha_answer}
                r = self.s.post(f'https://discord.com/api/v9/invites/{self.invite}', headers=self.headers, json=payload)
                if r.status_code == 200:
                    self.success("Successful Joined Server")
                    self.server_verify(r)
                    guild_id = r.json()["guild"]["id"]
                    if self.get_verify_channels(r) != None:
                        self.channel_verify(guild_id, self.get_verify_channels(r))
                    self.SuccessfulTask()
                elif "Unknown Invite" in r.text:
                    self.error("Unknown Invite")
                else:
                    self.error("Error while joining")
            elif "Unknown Invite" in r.text:
                self.error("Unknown Invite")
            else:
                self.error("Error while joining")
                print(r.text)

        except ProxyError:
            self.error("Proxy Error, retrying in 5 seconds")
            time.sleep(5)
            self.join()
        except Exception as e:
            self.exitTask("Error while joining - {}, stopping".format(str(e)), e)
        time.sleep(self.delay)


    def channel_verify_normal(self, message_data, message_id, channel_id, guild_id):
        bot_name = message_data["author"]["username"]
        if bot_name == "Pandez Guard Beta":
            self.pandez_verification(message_data, message_id, channel_id, guild_id)
        elif bot_name == "Wick":
            self.wick_verification(message_data, message_id, channel_id, guild_id)
        elif bot_name == "Sledgehammer":
            self.sledgehammer_verification(message_data, message_id, channel_id, guild_id)
        elif bot_name == "Captcha.bot":
            self.captcha_bot_verification(message_data, message_id, channel_id, guild_id)
        else:
            try:
                if message_data["components"]:
                    self.button_verification(message_data, message_id, channel_id, guild_id)
                else:
                    self.normal_verification(message_data, message_id, channel_id)
            except Exception as e:
                self.error(f"Error while verification - {e}")

    def join_normal(self, links):
        self.status('Joining Invite')
        self.start = time.time()
        try:
            r = self.s.post(f'https://discord.com/api/v9/invites/{self.invite}', headers=self.headers)
            if r.status_code == 200:
                self.success("Successful Joined Server")
                self.server_verify(r)
                try:
                    if ";" in links:
                        splitted = links.split(";")
                        for link in splitted:
                            guild_id = link.split("/")[4]
                            channel_id = link.split("/")[5]
                            message_id = link.split("/")[6]
                            r = self.s.get(f'https://discord.com/api/v9/channels/{channel_id}/messages?limit=50',
                                           headers=self.headers)
                            if "Missing Access" in r.text:
                                self.exitTask("You don't have access to this channel")
                            elif "Unauthorized" in r.text:
                                self.exitTask(f"Token clipped - {self.token}")
                            for message_data in reversed(r.json()):
                                if message_data["id"] == message_id:
                                    self.channel_verify_normal(message_data, message_id, channel_id, guild_id)
                    else:
                        guild_id = links.split("/")[4]
                        channel_id = links.split("/")[5]
                        message_id = links.split("/")[6]
                        r = self.s.get(f'https://discord.com/api/v9/channels/{channel_id}/messages?limit=50',
                                       headers=self.headers)
                        if "Missing Access" in r.text:
                            self.exitTask("You don't have access to this channel")
                        elif "Unauthorized" in r.text:
                            self.exitTask(f"Token clipped - {self.token}")
                        for message_data in reversed(r.json()):
                            if message_data["id"] == message_id:
                                self.channel_verify_normal(message_data, message_id, channel_id, guild_id)
                except ProxyError:
                    self.error("Proxy Error, retrying")
                    self.join()
                except Exception as e:
                    self.exitTask("Error while verifying - {}, stopping".format(str(e)))
                self.SuccessfulTask()

            elif "40002" in r.text:
                self.delete_clipped()
                self.exitTask(f"This token got clipped - {self.token}", e="Clipped")

            elif r.status_code == 401:
                self.delete_clipped()
                self.exitTask(f"This token got clipped - {self.token}", e="Clipped")

            elif "captcha_key" in r.text:
                captcha_answer = self.captcha()
                payload = {"captcha_key": captcha_answer}
                r = self.s.post(f'https://discord.com/api/v9/invites/{self.invite}', headers=self.headers, json=payload)
                if r.status_code == 200:
                    self.success("Successful Joined Server")
                    self.server_verify(r)
                    try:
                        if ";" in links:
                            splitted = links.split(";")
                            for link in splitted:
                                guild_id = link.split("/")[4]
                                channel_id = link.split("/")[5]
                                message_id = link.split("/")[6]
                                r = self.s.get(f'https://discord.com/api/v9/channels/{channel_id}/messages?limit=50',
                                               headers=self.headers)
                                if "Missing Access" in r.text:
                                    self.exitTask("You don't have access to this channel")
                                elif "Unauthorized" in r.text:
                                    self.exitTask(f"Token clipped - {self.token}")
                                for message_data in reversed(r.json()):
                                    if message_data["id"] == message_id:
                                        self.channel_verify_normal(message_data, message_id, channel_id, guild_id)
                        else:
                            guild_id = links.split("/")[4]
                            channel_id = links.split("/")[5]
                            message_id = links.split("/")[6]
                            r = self.s.get(f'https://discord.com/api/v9/channels/{channel_id}/messages?limit=50',
                                           headers=self.headers)
                            if "Missing Access" in r.text:
                                self.exitTask("You don't have access to this channel")
                            elif "Unauthorized" in r.text:
                                self.exitTask(f"Token clipped - {self.token}")
                            for message_data in reversed(r.json()):
                                if message_data["id"] == message_id:
                                    self.channel_verify_normal(message_data, message_id, channel_id, guild_id)
                    except ProxyError:
                        self.error("Proxy Error, retrying")
                        self.join()
                    except Exception as e:
                        self.exitTask("Error while verifying - {}, stopping".format(str(e)))
                    self.SuccessfulTask()
                elif "Unknown Invite" in r.text:
                    self.error("Unknown Invite")
                else:
                    self.error("Error while joining")
            elif "Unknown Invite" in r.text:
                self.error("Unknown Invite")
            else:
                self.error("Error while joining")

        except ProxyError:
            self.error("Proxy Error, retrying in 5 seconds")
            time.sleep(5)
            self.join()
        except Exception as e:
            self.exitTask("Error while joining - {}, stopping".format(str(e)), e)
        time.sleep(self.delay)



def main():
    change_title("Bot - Invite Joiner")
    global counter
    counter = 0
    config = Config()
    if config["joiner_delay"] != "":
        threads = config["joiner_threads"]
    else:
        threads = config["threads"]


    invite_code = input(" Invite Code: ")
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
                tasks.append(row+";"+invite_code)
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

    logger = Logger()
    logger.invite_joiner_logger(log_list(invite_code))

    print()
    print(f'{Fore.MAGENTA}Invite Joiner / Successful: {SUCCESSFUL} - Failed: {FAILED}')
    input(f'{Fore.LIGHTGREEN_EX}Entering done, press Enter to go back ')
    time.sleep(1)




def worker(tasks):
    global counter
    counter += 1
    Joiner(tasks, counter)







