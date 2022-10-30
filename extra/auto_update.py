import ftplib


def download_file(latest_version):
    try:
        path = '/'
        filename = f'Bot - {latest_version}.rar'
        ftp = ftplib.FTP("ftp-bot.alwaysdata.net")
        ftp.login("login", "password")
        ftp.cwd(path)
        ftp.retrbinary("RETR " + filename, open("Bot - {}.rar".format(latest_version), 'wb').write)
        ftp.quit()
        print("Updated Bot!")
    except Exception as e:
        print("Error while downloading update : {}".format(str(e)))


def get_latest_version():
    import pyrebase

    config = {
        "apiKey": "apikey",
        "authDomain": "bot-172f2.firebaseapp.com",
        "databaseURL": "https://bot-172f2-default-rtdb.firebaseio.com/",
        "storageBucket": "bot-172f2.appspot.com"
    }

    firebase = pyrebase.initialize_app(config)

    db = firebase.database()

    version = db.child("Version").get().val()
    return version


def autoupdate(actual_version):
    latest_version = get_latest_version()
    if str(actual_version) != str(latest_version):
        print("New update available, downloading")
        download_file(latest_version)
    else:
        print("Bot is up to date !")

def upload_file(version):
    session = ftplib.FTP("ftp-bot.alwaysdata.net", "login", "password")
    file = open(f'Bot - {version}.rar','rb')
    session.storbinary(f'STOR Bot - {version}.rar', file)
    file.close()
    session.quit()


if __name__ == '__main__':
    upload_file("0.1.9")

