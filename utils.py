import argparse
import re
from pathlib import Path

NXDOMAIN = "NXDOMAIN"
RECORD_TYPE_A = "A"
RECORD_TYPE_AAAA = "AAAA"
RECORD_TYPE_MX = "MX"
RECORD_TYPE_NS = "NS"
NO_SINK = "the mitochondria is the powerhouse of the cell"

C_RED = "\033[1;31m"
C_RESET = "\033[0m"
C_YELLOW = "\033[1;33m"
C_GREEN = "\033[1;32m"
C_WHITE = "\033[1;37m"


def valid_subname(subname: str) -> bool:
    # no reason to try words with bad characters in them; this is cutting them out of the list.
    print(re.fullmatch(r'[\w]{0,63}', subname.replace('-', '').strip()))
    if len(subname) > 63 or not subname.replace('-', '').isascii():
        return False
    return True


def load_wordlist(filename) -> list:
    file_path = Path(filename)
    subname_pattern = re.compile(r'[\w]{0,63}')

    if not file_path.exists():
        print_err(f"File: {filename} does not exist.")

    if not file_path.is_file():
        print_err(f"The specified filename: {filename} is not a file.")

    words = []

    try:
        with open(file_path, 'r') as f:
            for subname in f:
                subname = subname.strip()
                if subname_pattern.fullmatch(subname.replace('-', '')):
                    words.append(subname)
        return words
    except Exception as e:
        print_err(e)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Brute force subdomains of a specified domain.")
    parser.add_argument('-d', '--domain', required=True, type=str,
                        help='specifies the target parent domain you want to enumerate the subdomains of')
    parser.add_argument('-w', '--wordlist', type=str, default='subnames.txt',
                        help='specifies the wordlist to use for subdomain brute force (subnames.txt by default)')
    parser.add_argument('-r', '--resolver', type=str, default='8.8.8.8',
                        help='specifies the IP address of the resolver to use (8.8.8.8 by default)')
    parser.add_argument('-o', '--output', type=str, default='output.json',
                        help='specifies a file to log results (output.json by default)')

    return parser.parse_args()


# shameless plugs; its what I do best
def printBanner():
    asciiArt = C_RED + """
            _     _____                       
  ___ _   _| |__ | ____|_ __  _   _ _ __ ___  
 / __| | | | '_ \|  _| | '_ \| | | | '_ ` _ \ 
 \__ \ |_| | |_) | |___| | | | |_| | | | | | |
 |___/\__,_|_.__/|_____|_| |_|\__,_|_| |_| |_|

	""" + C_RESET

    socials = f"\tCreated by: {C_WHITE}kindredsec{C_RESET}\n"
    socials += "\thttps://twitter.com/kindredsec\n"
    socials += "\thttps://kindredsec.com\n"
    socials += "\thttps://github.com/itsKindred"
    print("-" * 50)
    print(asciiArt)
    print(socials)
    print("-" * 50)


def print_err(message):
    print(f"{C_RED}[-]{C_RESET} ERROR: {message}")
    exit(1)


def print_notif(message):
    print(f"{C_YELLOW}[!]{C_RESET} {message}")


def print_yay(message):
    print(f"{C_GREEN}[+]{C_RESET} {message}")
