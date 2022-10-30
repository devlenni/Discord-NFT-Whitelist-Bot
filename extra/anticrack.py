import sys, time, os, threading, platform
from dhooks import Webhook, Embed

logs_wh = "https://discord.com/api/webhooks/...."

software_list = ["Charles.exe", "Fiddler.exe", "Fiddler Everywhere.exe", "mitmproxy.exe", "Burp Suite.exe", "Proxyman.exe", "HTTP Toolkit.exe",
                 "NetworkMiner.exe", "CacheGuard-OS.exe", "HTTP Debugger.exe", "Camilla Proxy.exe", "Wireshark.exe"]


def check_for_bad_processes():
    if platform.system().lower() != "darwin":
        output = os.popen('wmic process get description').read()
        for elt in software_list:
            if elt in output:
                return elt
        return None
    else:
        return None


def anticrack(license):
    while True:
        result = check_for_bad_processes()
        if result is None:
            pass
        else:
            software = result
            hook = Webhook(logs_wh)
            title = "Cracking attempt detected"

            embed = Embed(
                description='',
                color=7484927,
                timestamp='now',
                title=title
            )
            embed.set_author(name="WHITELISTERZ",
                             icon_url='')
            embed.add_field(name='License', value=license, inline=False)
            embed.add_field(name='Software', value=software, inline=False)
            embed.set_footer(text='WHITELISTERZ',
                             icon_url='')
            try:
                hook.send(embed=embed)
            except:
                pass
            print('Cracking attempt detected, closing...')
            sys.exit()



        time.sleep(5)


def start_anticrack(license):
    threading.Thread(target=anticrack, args=(license,), daemon=True).start()

