import pyperclip
import subprocess
import base64
import random
import sys
import time
import multiprocessing.dummy as mp
import uuid
import websocket, json
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
import platform

print_lock = Lock()

cwd = os.getcwd()

colorama.init(autoreset=True)

console = Console()

task_log_list = []

def clear():
    if platform.system().lower() == "darwin":
        os.system("clear")
    else:
        os.system("cls")


SUCCESSFUL = 0
FAILED = 0

def updateStatusBar(success=False):
    global SUCCESSFUL
    global FAILED

    if success == True:
        SUCCESSFUL += 1
    elif success == False:
        FAILED += 1
    change_title(f"Bot - Token Manager / Successful: {str(SUCCESSFUL)} - Failed: {str(FAILED)}")


class Manager:
    def __init__(self):
        config = Config()
        self.taskId = f"Task-{1}"

        while True:
            clear()
            print("""
1. Extract Tokens
2. Extract Proxies
3. Delete Proxies
4. Update Proxies
5. Exit Manager
            """)
            choice = int(input("Select >>> "))
            if choice == 5:
                sys.exit()
            else:
                self.extract(choice)

        
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

    def SuccessfulTask(self, success):
        self.success(success)
        updateStatusBar(success=True)
        return


    def save(self, list, choice):
        if choice == 1:
            filename = input("Filename: ")
            with open(get_path(filename+".txt"), "w") as fp:
                for line in list:
                    fp.write(line.replace("\n", "")+"\n")
                fp.close()
        elif choice == 2:
            string1 = ""
            for row in list:
                string1 += row.replace("\n", "")+"\n"
            pyperclip.copy(string1)
	

    def extract(self, choice):
        if choice == 1:
            print("""
    1. Save to file 
    2. Copy to clipboard
            """)
            extract_choice = int(input("Select >>> "))
            clear()
            extracted = []
            tokens = open(get_path("tokens.txt")).readlines()
            i = 0
            for row in tokens:
                time.sleep(0.03)
                i += 1
                if ";" in row:
                    token_row = row.split(";")[0]
                    if ":" in token_row:
                        token = token_row.split(":")[2]
                        extracted.append(token)
                    else:
                        extracted.append(token_row)
                else:
                    token_row = row
                    if ":" in token_row:
                        token = token_row.split(":")[2]
                        extracted.append(token)
                    else:
                        extracted.append(token_row)
                self.status(f"Extracted [{i}/{len(tokens)}]")
            self.save(extracted, extract_choice)
            self.SuccessfulTask("Finished extracting")
            time.sleep(3)
        elif choice == 2:
            print("""
    1. Save to file 
    2. Copy to clipboard
            """)
            extract_choice = int(input("Select >>> "))
            clear()
            extracted = []
            tokens = open(get_path("tokens.txt")).readlines()
            i = 0
            for row in tokens:
                time.sleep(0.03)
                i += 1
                if ";" in row:
                    proxy = row.split(";")[1]
                    extracted.append(proxy)
                    self.status(f"Extracted [{i}/{len(tokens)}]")
            self.save(extracted, extract_choice)
            self.SuccessfulTask("Finished extracting")
            time.sleep(3)
        elif choice == 3:
            deleted = []
            tokens = open(get_path("tokens.txt")).readlines()
            i = 0
            for row in tokens:
                time.sleep(0.03)
                i += 1
                if ";" in row:
                    proxy = row.split(";")[1]
                    new_row = row.replace(f";{proxy}", "")
                    deleted.append(new_row)
                else:
                    deleted.append(row)
                self.status(f"Deleted [{i}/{len(tokens)}]")
            with open(get_path("tokens.txt"), "w") as fp:
                for line in deleted:
                    fp.write(line.replace("\n", "")+"\n")
                fp.close()
            self.SuccessfulTask("Finished deleting")
            time.sleep(3)
        elif choice == 4:
            updated = []
            proxies = open(get_path("proxies.txt")).readlines()
            tokens = open(get_path("tokens.txt")).readlines()
            i = 0
            for proxy, row in zip(proxies, tokens):
                time.sleep(0.03)
                i += 1
                if ";" in row:
                    prox = row.split(";")[1]
                    new_row = row.replace(prox, proxy)
                    updated.append(new_row)
                else:
                    new_row = row+";"+proxy
                    updated.append(new_row)
                self.status(f"Updated [{i}/{len(tokens)}]")
                
            with open(get_path("tokens.txt"), "w") as fp:
                for line in updated:
                    fp.write(line.replace("\n", "")+"\n")
                fp.close()
            self.SuccessfulTask("Finished updating")
            time.sleep(3)


def main():
    change_title("Bot - Token Manager")

    worker()

    print()
    print(f'{Fore.MAGENTA}Token Manager / Successful: {SUCCESSFUL} - Failed: {FAILED}')
    input(f'{Fore.LIGHTGREEN_EX}Entering done, press Enter to go back ')
    time.sleep(1)



def worker():
    global counter
    Manager()





#if __name__ == "__main__":
#    main()

    #print()
    #print(f'{Fore.MAGENTA}Invite Joiner / Successful: {SUCCESSFUL} - Failed: {FAILED}')
    #input(f'{Fore.LIGHTGREEN_EX}Entering done, press Enter to go back ')
    #time.sleep(1)







		

