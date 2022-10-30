from email import header
import requests

s = requests.Session()
def sess():
    headers = {"user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/102.0.0.0 Safari/537.36"}
    r = s.get("https://mercury.blocksmithlabs.io/api/auth/providers", headers=headers)
    print(r.status_code)
    print(r.text)

    r = s.get("https://mercury.blocksmithlabs.io/api/auth/csrf", headers=headers)
    csrfToken = r.json()["csrfToken"]
    print(r.status_code)
    print(r.text)

    r = s.post("https://mercury.blocksmithlabs.io/api/auth/signin/discord?", headers=headers, data={
        "callbackUrl":"/",
        "csrfToken": csrfToken,
        "json": "true"
    })
    print(r.status_code)
    print(r.text)
sess()    