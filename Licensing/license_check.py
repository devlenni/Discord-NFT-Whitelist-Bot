import sys
import time
import socket
import requests
from termcolor import colored


def license_webhook(user, license, ip_address, hostname):

    webhook = "https://discord.com/api/webhooks/..."

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/93.0.4577.82 Safari/537.36",
        "Accept": "application/json"
    }

    webhookData = {
        "content": None,
        "embeds": [
            {
                "title": f"User Bound",
                "color": 3447003,
                "fields": [
                    {
                        "name": "License",
                        "value": f"||{license}||"
                    },
                    {
                        "name": "User",
                        "value": user
                    },
                    {
                        "name": "IP",
                        "value": f"||{ip_address}||"
                    },
                    {
                        "name": "Host Name",
                        "value": f"||{hostname}||"
                    },
                ]
            }
        ]
    }
    requests.post(webhook, json=webhookData, headers=headers)


import pyrebase

config = {
  "apiKey": "apikey",
  "authDomain": "bot-172f2.firebaseapp.com",
  "databaseURL": "https://bot-172f2-default-rtdb.firebaseio.com/",
  "storageBucket": "bot-172f2.appspot.com"
}

firebase = pyrebase.initialize_app(config)

db = firebase.database()


""" 
		for cli licensing
"""
def validate_license(user_key, log=True):
    x = dict(db.child("Licenses").get().val())
    valid_key = False
    bound = False
    for i in x:
        if x[i]["license"] == user_key:
            user = x[i]["user"]
            license = x[i]["license"]
            if x[i]["bound"] == False:
                """
				    bind to ip, hwid
			    """
                hostname = socket.gethostname()
                ip_address = socket.gethostbyname(hostname)

                bind_data = {
                    "hostname": hostname,
                    "ip_address": ip_address
                }

                db.child("Licenses").child(i).update({"bound": bind_data})
                license_webhook(user, license, ip_address, hostname)


                valid_key = True
                if log == True:
                    print(f"License Validated, Welcome {user}!")
                time.sleep(3)
                return user

            else:
                """
                        check if ip and hwid is same from pc
                """

                hostname = socket.gethostname()
                ip_address = socket.gethostbyname(hostname)

                if hostname == x[i]["bound"]["hostname"] and ip_address == x[i]["bound"]["ip_address"]:
                    valid_key = True
                    if log == True:
                        print(colored(f'Welcome back {user}!', 'green'))
                    time.sleep(3)
                    return user
                else:
                    print("License already bound!")
                    bound = True
                    time.sleep(3)
                    sys.exit()
    if valid_key == False:
        print("No license found!")
        time.sleep(3)
        sys.exit()
    elif bound == True:
        print("License already bound!")
        time.sleep(3)
        sys.exit()


