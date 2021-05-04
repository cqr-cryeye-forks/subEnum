# subEnum
**subEnum** is a small Python3 script used to bruteforce subdomain names of a specified domain. Given a domain name and a wordlist, subEnum can bruteforce the names of subdomains located within your target domain, opening up a much larger attack surface during your engagement.

[![asciicast](https://asciinema.org/a/258669.svg)](https://asciinema.org/a/258669)

Note: This script currently does not support multithreading, but should support it very soon.

## Requirements
Due to the usage of "f" strings, this script must be run using python3. If this becomes too much of an issue I can add python2 support. The `dns.resolver` module is also required, but this should be in your default python3 installation.

## Options

```console
Usage:

  -h, --help            show this help message and exit
  -d, --domain          specifies the target parent domain you want to enumerate the subdomains of
  -w, --wordlist        specifies the wordlist to use for subdomain brute force (subnames.txt by default)
  -r, --resolver        specifies the IP address of the resolver to use (8.8.8.8 by default)
  -o, --output          specifies a file to log results (output.json by default)

```
