import os
import platform
import sys
import time
from rich.console import Console
from rich.table import Table
from termcolor import colored

from utils import activity_webhook
from utils import Config


version = "0.1.9"


config = Config()
webhook = config["webhook_url"]
delay = config["delay"]
license = config["license"]


console = Console()


def clear():
    if platform.system().lower() == "darwin":
        os.system("clear")
    else:
        os.system("cls")


def set_title():
    from utils import change_title
    change_title(f"Bot - {version}")



def cli():
    HEADER = """[purple]

 _______  _______  _______ 
|  _    ||       ||       |
| |_|   ||   _   ||_     _|
|       ||  | |  |  |   |  
|  _   | |  |_|  |  |   |  
| |_|   ||       |  |   |  
|_______||_______|  |___|  
    """
    console.print(HEADER, justify="center")
    console.print(f"[blue]Version - {version}", justify="center")
    console.print()

    table = Table(show_header=True)
    # table.add_column('[purple]MODULES', justify='left')
    table.add_column('                    [purple]TOOLS', justify='left')

    table.add_row('[1] [purple]Invite                    [white][4] [purple]AIO Monitor\n')#[white][5] [purple]Custom Mode\n')
    table.add_row('[2] [purple]Giveaway                  [white][5] [purple]Chat Bot\n')
    table.add_row('[3] [purple]Games                     [white][6] [purple]Utils\n')
    table.add_row()
    table.add_row('[0] [purple]Quit program\n')



    # table.add_row('                     ', '')

    console.print(table, justify="center")
    print()
    print()

def invite_cli():
    HEADER = """[purple]

 ___   __    _  __   __  ___   _______  _______ 
|   | |  |  | ||  | |  ||   | |       ||       |
|   | |   |_| ||  |_|  ||   | |_     _||    ___|
|   | |       ||       ||   |   |   |  |   |___ 
|   | |  _    ||       ||   |   |   |  |    ___|
|   | | | |   | |     | |   |   |   |  |   |___ 
|___| |_|  |__|  |___|  |___|   |___|  |_______|

        """
    console.print(HEADER, justify="center")
    #console.print("[blue]Version - 0.0.3", justify="center")
    console.print()
    console.print("\n")

    table = Table(show_header=True)
    # table.add_column('[purple]MODULES', justify='left')
    table.add_column('                   [purple]INVITE MODULES', justify='left')

    table.add_row('[1] [purple]Invite Joiner           [white][2] [purple]Manual verification\n')
    table.add_row()
    table.add_row('[0] [purple]Back to main menu\n')
    #table.add_row('[2] [purple]Invite Leaver\n')



    # table.add_row('                     ', '')

    console.print(table, justify="center")
    print()
    print()
    print()
    print()

def giveaway_cli():
    HEADER = """[purple]       
     
  _______  ___   __   __  _______  _______  _     _  _______  __   __ 
 |       ||   | |  | |  ||       ||   _   || | _ | ||   _   ||  | |  |
 |    ___||   | |  |_|  ||    ___||  |_|  || || || ||  |_|  ||  |_|  |
 |   | __ |   | |       ||   |___ |       ||       ||       ||       |
 |   ||  ||   | |       ||    ___||       ||       ||       ||_     _|
|   |_| ||   |  |     | |   |___ |   _   ||   _   ||   _   |  |   |  
|_______||___|   |___|  |_______||__| |__||__| |__||__| |__|  |___|  

            """
    console.print(HEADER, justify="center")
    # console.print("[blue]Version - 0.0.3", justify="center")
    console.print()

    table = Table(show_header=True)
    # table.add_column('[purple]MODULES', justify='left')
    table.add_column('                 [purple]GIVEAWAY MODULES', justify='left')

    table.add_row('[1] [purple]Giveaway Monitor           [white][3] [purple]Giveaway Checker\n')
    table.add_row('[2] [purple]Giveaway Joiner\n')
    table.add_row()
    table.add_row('[0] [purple]Back to main menu\n')
    # table.add_row('                     ', '')

    console.print(table, justify="center")
    print()
    print()
    print()
    print()

def utils_cli():
    HEADER = """[purple]
 __   __  _______  ___   ___      _______ 
|  | |  ||       ||   | |   |    |       |
|  | |  ||_     _||   | |   |    |  _____|
|  |_|  |  |   |  |   | |   |    | |_____ 
|       |  |   |  |   | |   |___ |_____  |
|       |  |   |  |   | |       | _____| |
|_______|  |___|  |___| |_______||_______|

            """
    console.print(HEADER, justify="center")
    # console.print("[blue]Version - 0.0.3", justify="center")

    table = Table(show_header=True)
    # table.add_column('[purple]MODULES', justify='left')
    table.add_column('                     [purple]UTILS', justify='left')
    table.add_row('[1] [purple]Manual browser          [white][6] [purple]Message Scraper\n')
    table.add_row('[2] [purple]Token Checker           [white][7] [purple]Bio Changer\n')
    table.add_row('[3] [purple]Token Cleaner           [white][8] [purple]Name Changer\n')
    table.add_row('[4] [purple]Token Manager           [white][9] [purple]Avatar Changer\n')
    table.add_row('[5] [purple]Scraper')
    table.add_row()
    table.add_row('[0] [purple]Back to main menu\n')

    # table.add_row('                     ', '')

    console.print(table, justify="center")
    print()

def games_cli():
    HEADER = """[purple]
    
 _______  _______  __   __  _______  _______ 
|       ||   _   ||  |_|  ||       ||       |
|    ___||  |_|  ||       ||    ___||  _____|
|   | __ |       ||       ||   |___ | |_____ 
|   ||  ||       ||       ||    ___||_____  |
|   |_| ||   _   || ||_|| ||   |___  _____| |
|_______||__| |__||_|   |_||_______||_______|

              """
    console.print(HEADER, justify="center")
    # console.print("[blue]Version - 0.0.3", justify="center")
    console.print()
    console.print("\n")

    table = Table(show_header=True)
    # table.add_column('[purple]MODULES', justify='left')
    table.add_column('                     [purple]GAMES', justify='left')

    table.add_row('[1] [purple]Rumble Royale Monitor    [white][2] [purple]Coming soon...\n')
    table.add_row()
    table.add_row('[0] [purple]Back to main menu\n')

    #table.add_row('[2] [purple]Rumble Royale Joiner\n')

    # table.add_row('                     ', '')

    console.print(table, justify="center")
    print()
    print()
    print()
    print()

i = 0
def menu():
    global i
    if i == 0:
        from Licensing.license_check import validate_license
        from extra.anticrack import start_anticrack
        from extra.auto_update import autoupdate
        start_anticrack(license)
        user = validate_license(license)
        autoupdate(version)
        i += 1
    user = validate_license(license, log=False)
    clear()
    set_title()
    cli()
    user_choice = int(input("Select option >>> "))

    while user_choice != 0:

        if user_choice == 1:
            clear()
            invite_cli()
            invite_choice = int(input("Select option >>> "))

            while invite_choice != 0:

                if invite_choice == 1:
                    activity_webhook("Invite Joiner", license, user)
                    clear()
                    from modules.invite_joiner import main
                    main()
                    menu()

                elif invite_choice == 2:
                    activity_webhook("Manual Verification", license, user)
                    clear()
                    from modules.manual_verification import main
                    main()
                    menu()

                else:
                    print(colored(f'Invalid selection', 'red'))
                    time.sleep(2)
                    menu()
            print(colored(f'Going back to main menu', 'red'))
            time.sleep(2)
            menu()


        elif user_choice == 2:
            clear()
            giveaway_cli()
            giveaway_choice = int(input("Select option >>> "))

            while giveaway_choice != 0:

                if giveaway_choice == 1:
                    activity_webhook("Giveaway Monitor", license, user)
                    clear()
                    from modules.giveaway_monitor import main
                    main()
                    menu()

                elif giveaway_choice == 2:
                    activity_webhook("Giveaway Joiner", license, user)
                    clear()
                    from modules.giveaway_joiner import main
                    main()
                    menu()

                elif giveaway_choice == 3:
                    activity_webhook("Giveaway Checker", license, user)
                    clear()
                    from modules.giveaway_checker import main
                    main()
                    menu()

                else:
                    print(colored(f'Invalid selection', 'red'))
                    time.sleep(2)
                    menu()
            print(colored(f'Going back to main menu', 'red'))
            time.sleep(2)
            menu()

        elif user_choice == 3:
            clear()
            games_cli()
            games_choice = int(input("Select option >>> "))
            
            while games_choice != 0:

                if games_choice == 1:
                    activity_webhook("Rumble Royale Monitor", license, user)
                    clear()
                    from modules.rumbleroyale_monitor import main
                    main()
                    menu()

                else:
                    print(colored(f'Invalid selection', 'red'))
                    time.sleep(2)
                    menu()

            print(colored(f'Going back to main menu', 'red'))
            time.sleep(2)
            menu()
            
    


        elif user_choice == 4:
            activity_webhook("AIO Monitor", license, user)
            clear()
            from modules.aio_monitor import main
            main()
            menu()


        elif user_choice == 5:
            activity_webhook("Chat Bot", license, user)
            clear()
            from modules.chat_bot import main
            main()
            menu()


        elif user_choice == 6:
            clear()
            utils_cli()
            utils_choice = int(input("Select option >>> "))

            while utils_choice != 0:

                if utils_choice == 1:
                    activity_webhook("Manual Browser", license, user)
                    clear()
                    from modules.manual_browser import main
                    main()
                    menu()

                elif utils_choice == 2:
                    activity_webhook("Token Checker", license, user)
                    clear()
                    from modules.token_checker import main
                    main()
                    menu()

                elif utils_choice == 3:
                    activity_webhook("Token Cleaner", license, user)
                    clear()
                    from modules.token_cleaner import main
                    main()
                    menu()

                elif utils_choice == 4:
                    activity_webhook("Token manager", license, user)
                    clear()
                    from modules.token_manager import main
                    main()
                    menu()

                elif utils_choice == 5:
                    activity_webhook("Scraper", license, user)
                    clear()
                    from modules.scraper import main
                    main()
                    menu()

                elif utils_choice == 6:
                    activity_webhook("Message Scraper", license, user)
                    clear()
                    from modules.message_scraper import main
                    main()
                    menu()

                elif utils_choice == 7:
                    activity_webhook("Bio Changer", license, user)
                    clear()
                    from modules.bio_changer import main
                    main()
                    menu()

                elif utils_choice == 8:
                    activity_webhook("Name Changer", license, user)
                    clear()
                    from modules.name_changer import main
                    main()
                    menu()
                
                elif utils_choice == 9:
                    activity_webhook("Avatar Changer", license, user)
                    clear()
                    from modules.pfp_changer import main
                    main()
                    menu()
                
                else:
                    print(colored(f'Invalid selection', 'red'))
                    time.sleep(2)
                    menu()

            print(colored(f'Going back to main menu', 'red'))
            time.sleep(2)
            menu()


        else:
            print(colored(f'Invalid selection', 'red'))
            time.sleep(2)
            menu()
    print(colored(f'Quitting...', 'red'))
    time.sleep(2)
    sys.exit()


if __name__ == '__main__':
    #try:
    menu()
    #except:
    #    print(colored(f'Quitting...', 'red'))
    #    time.sleep(2)
    #    sys.exit()
