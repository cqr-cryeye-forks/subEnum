# subEnum
**subEnum** is a small Python3 script used to bruteforce subdomain names of a specified domain. Given a domain name and a wordlist, subEnum can bruteforce the names of subdomains located within your target domain, opening up a much larger attack surface during your engagement.

[![asciicast](https://asciinema.org/a/258669.svg)](https://asciinema.org/a/258669)

Note: This script currently does not support multithreading, but should support it very soon.

## Requirements
Due to the usage of "f" strings, this script must be run using python3. If this becomes too much of an issue I can add python2 support. The `dns.resolver` module is also required, but this should be in your default python3 installation.
