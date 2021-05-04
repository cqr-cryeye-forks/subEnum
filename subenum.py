#!/usr/bin/env python3

import concurrent.futures
import json

import dns.resolver

# Constants. Most of them completely unneccessary, I just hate
# seeing string literals in code blocks.
from utils import *


def resolve(sub, root, name_server):
    resolver = dns.resolver.Resolver()
    resolver.nameservers = [name_server, ]
    domain = f"{sub}.{root}"

    try:
        # probably should check other records (A, AAAA, MX, NS), but this will do for now.
        ip, *_ = resolver.resolve(domain, RECORD_TYPE_A)
    # not all of these errors indicate an NXDOMAIN, but I'm too lazy to do proper error-handling; treating these all as
    # "the subdomain doesn't exist" is fine for our purposes.
    except (dns.resolver.NXDOMAIN, dns.name.EmptyLabel, dns.resolver.NoAnswer) as e:
        ip = None
    # technically I probably should return ALL the resolved IPs, however the actual IP's don't matter that much;
    # I'm more concerned with knowing that the subdomain exists, not what IP it resolves to.
    return ip


def run_brute(domain: str, subname: str, resolver: str, sinkhole: str):
    ip = resolve(subname, domain, resolver)

    # if its not a sink and its not an NX, its a legitimate response, meaning the subdomain
    # exists.
    if ip and ip != sinkhole:
        print_yay(f"{subname}.{domain} => {ip}")
        return {
            "domain": f"{subname}.{domain}",
            "ip": str(ip)
        }


# this probably isn't the correct terminology, but I noticed that my provider was returning an A record
# for non-existent domains. This function checks if that is happening, and if it is, don't 
# treat any query that resolves to that A record as valid.

def check_sink_hole(domain, resolver):
    # IN THEORY sysadmins could register this hard-coded subdomain to prevent this script from enumerating
    # subdomains associated with an IP address, but that's obviously not a concern at this point in time.
    not_exist = "weijffjwejf3weijfwejfoi423rji"
    sinkhole = resolve(sub=not_exist, root=domain, name_server=resolver)

    if sinkhole != NXDOMAIN:
        mes = f"Detected {sinkhole} as a false positive. Ignoring any subdomains that resolve to this address..."
        print_notif(mes)
        return sinkhole
    else:
        return NO_SINK


def main():
    args = parse_args()
    wordlist = load_wordlist(args.wordlist)
    output = []

    # defaults to using Google's Name Server. Probably should build in some redundancy here, but
    # I've never actually seen 8.8.8.8 go down, so I'm not too worried about this.

    try:
        printBanner()
        sinkhole = check_sink_hole(domain=args.domain, resolver=args.resolver)
        print_notif("Beginning brute force...")
        with concurrent.futures.ThreadPoolExecutor() as executor:
            # Start the load operations and mark each future with its URL
            futures = [executor.submit(run_brute, args.domain, subname, args.resolver, sinkhole) for subname in
                       wordlist]
            for future in concurrent.futures.as_completed(futures):
                try:
                    data = future.result()
                except Exception as e:
                    print_err(e)
                else:
                    output.append(data)

    except KeyboardInterrupt:
        print_notif("Exiting...")
        # weakness ^C
        executor.shutdown(wait=False, cancel_futures=True)
        exit(2)
    finally:
        output = list(filter(None, output))
        with open(args.output, 'w') as f:
            json.dump(output, f, indent=2)


if __name__ == "__main__":
    main()
