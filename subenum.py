#!/usr/bin/env python3

import dns.resolver
import threading
import argparse
import sys
import string

# Constants. Most of them completely unneccessary, I just hate
# seeing string literals in code blocks.
MAX_SUBDOMAIN_LENGTH = 63
FILEMODE_READ = "r"
FILEMODE_APPEND = "a"
NXDOMAIN = "NXDOMAIN"
RECORD_TYPE_A = "A"
RECORD_TYPE_AAAA = "AAAA"
RECORD_TYPE_MX = "MX"
RECORD_TYPE_NS = "NS"
GOOGLE_NAME_SERVER = "8.8.8.8"
NO_SINK = "the mitochondria is the powerhouse of the cell"

C_RED = "\033[1;31m"
C_RESET = "\033[0m"
C_YELLOW = "\033[1;33m"
C_GREEN = "\033[1;32m"
C_WHITE = "\033[1;37m"

def parseWordlist(filename):

	words = []

	try:

		with open(filename, FILEMODE_READ) as f:
			for i in f.readlines():
			
				if len(i) <= MAX_SUBDOMAIN_LENGTH:
				
					# no reason to try words with bad characters in them; this is cutting them out of the list.
					badChars = False
					for j in string.punctuation:
						if j != "-" and j in i:
							badChars = True

					if badChars == False:
						words.append(i.strip())

			return words

	except:
			print_err( "Specified wordlist could not be found.")


def resolve(sub, root, name_server):

	resolver = dns.resolver.Resolver()
	
	resolver.nameservers = [ name_server, ]

	domain = sub + "." + root

	try:

		# probably should check other records (A, AAAA, MX, NS), but this will do for now.
		answers = resolver.query(domain, RECORD_TYPE_A)

	# not all of these errors indicate an NXDOMAIN, but I'm too lazy to do proper error-handling; treating these all as
	# "the subdomain doesn't exist" is fine for our purposes.
	except ( dns.resolver.NXDOMAIN, dns.name.EmptyLabel, dns.resolver.NoAnswer):
		answers = [ NXDOMAIN, ]
	
	# technically I probably should return ALL the resolved IPs, however the actual IP's don't matter that much;
	# I'm more concerned with knowing that the subdomain exists, not what IP it resolves to.
	return answers[0]


def print_err(message):

	print(f"{C_RED}[-]{C_RESET} ERROR: {message}")
	sys.exit(1)

def print_notif(message):
	
	print(f"{C_YELLOW}[!]{C_RESET} {message}")


def print_yay(message):
	
	print(f"{C_GREEN}[+]{C_RESET} {message}")


#shameless plugs; its what I do best
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




def runBrute(domain, wordlist, resolver, outfile):

		sinkhole = checkSinkHole(domain, resolver)
		print_notif("Beginning brute force...")

		for sub in wordlist:
			queryRet = resolve(sub, domain, resolver)

			# if its not a sink and its not an NX, its a legitimate response, meaning the subdomain
			# exists.
			if queryRet != sinkhole and queryRet != NXDOMAIN:
				print_yay(f"{sub}.{domain} => {queryRet}")
				if outfile:
					with open(outfile, FILEMODE_APPEND) as f:
						f.write(sub + "." + domain + ":" + str(queryRet) + "\n")


# this probably isn't the correct terminology, but I noticed that my provider was returning an A record
# for non-existent domains. This function checks if that is happening, and if it is, don't 
# treat any query that resolves to that A record as valid.
def checkSinkHole(domain, resolver):

	# IN THEORY sysadmins could register this hard-coded subdomain to prevent this script from enumerating
	# subdomains associated with an IP address, but that's obviously not a concern at this point in time.
	nonexist = "weijffjwejf3weijfwejfoi423rji"
	sinkholeReturn = resolve(nonexist, domain, resolver)

	if sinkholeReturn != NXDOMAIN: 
		print_notif(f"Detected {sinkholeReturn} as a false positive. Ignoring any subdomains that resolve to this address...")
		return sinkholeReturn
	else:
		return NO_SINK
	

def main():

	parser = argparse.ArgumentParser( description="Brute force subdomains of a specified domain.")
	parser.add_argument('-d', nargs='?', metavar='domain', help='Specifies the target parent domain you want to enumerate the subdomains of.')
	parser.add_argument('-w', nargs='?', metavar='wordlist', help='Specifies the wordlist to use for subdomain brute force.')
	parser.add_argument('-r', nargs='?', metavar='resolver', help='Specifies the IP address of the resolver to use (8.8.8.8 by default).')
	parser.add_argument('-o', nargs='?', metavar='outfile', help='Specifies a file to log results to in addition to standard output.')

	args = parser.parse_args()

	domain = ""	
	if not args.d:
		print_err("A parent domain must be specified with the -d option.")

	elif args.d:
		domain = args.d

	wordlist = ""
	if not args.w:
		print_err("A wordlist must be specified with the -w option.")

	else:
		wordlist = parseWordlist(args.w)
	
	resolver = ""	
	if not args.r:

		# defaults to using Google's Name Server. Probably should build in some redundancy here, but
		# I've never actually seen 8.8.8.8 go down, so I'm not too worried about this.
		resolver = GOOGLE_NAME_SERVER

	elif args.r:
		resolver = args.r

	
	# this wont work once I add threading. 
	try:
		printBanner()
		runBrute(domain, wordlist, resolver, args.o)
	except KeyboardInterrupt:
		print_notif("Exiting...")
		sys.exit(2)


main()
