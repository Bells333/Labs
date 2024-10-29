import sys
from scapy.all import sr1, IP, UDP, DNS, DNSQR
import dns.resolver
import socket


def get_primary_dns_server(domain):
    # Create a DNS query packet to find the primary DNS server for the domain
    query = IP(dst="8.8.8.8") / UDP(dport=53) / DNS(rd=1, qd=DNSQR(qname=domain, qtype="SOA"))
    response = sr1(query, verbose=0)
    if response and response.haslayer(DNS) and response[DNS].ancount > 0:
        for i in range(response[DNS].ancount):
            rr = response[DNS].an[i]
            if rr.type == 6:  # SOA type
                primary_dns = rr.mname.decode() # Decode the mname (primary DNS server) from the SOA record
                return primary_dns
    return None

# this is to change the ip address to the name from the dns we found in the original
def resolve_hostname_to_ip(hostname):
    try:
        return socket.gethostbyname(hostname)
    except socket.gaierror:
        return None


def get_ip_addresses(subdomain, dns_server):
    try:
        resolver = dns.resolver.Resolver()
        resolver.nameservers = [dns_server] #gonna use the dns server we found for jct.ac.il and then go through each domain A
        answers = resolver.resolve(subdomain, 'A') #for ipv4 we're gonna find all the ip addresess
        return [answer.address for answer in answers]
    except (dns.resolver.NoAnswer, dns.resolver.NXDOMAIN):
        return []


def main(domain, wordlist_file):
    primary_dns_server = get_primary_dns_server(domain)
    if not primary_dns_server:
        print(f"Could not find primary DNS server for {domain}")
        return

    print(f"Using primary DNS server: {primary_dns_server}")

    # Resolve the primary DNS server to its IP address opposite of what we did before
    primary_dns_ip = resolve_hostname_to_ip(primary_dns_server)
    if not primary_dns_ip:
        print(f"Could not resolve primary DNS server {primary_dns_server} to an IP address")
        return

    with open(wordlist_file, 'r') as f: # i only used a small list - not the whole list but the ones that are found and easy to iterate trhough
        subdomains = [line.strip() for line in f.readlines() if line.strip() and not line.startswith('#')]

    for subdomain in subdomains:
        full_domain = f"{subdomain}.{domain}"
        ip_addresses = get_ip_addresses(full_domain, primary_dns_ip)
        if ip_addresses:
            print(f"{full_domain} : {', '.join(ip_addresses)}")


if __name__ == "__main__":
    if len(sys.argv) != 3:
        print(f"Usage: {sys.argv[0]} <domain> <wordlist_file>") #this is how we're gonna call the code into practice
        #jct.ac.il custom_wordlist.txt
        sys.exit(1)

    domain = sys.argv[1]
    wordlist_file = sys.argv[2]
    main(domain, wordlist_file)

#Bella Kamins
#I use a macOS and code on pycharm there are some things that werent necessary according to the homework but needed in order to debug and check code
# (newenv) Bellas-MacBook-Pro:Lab4scapy bellak$ python3 main.py jct.ac.il custom_wordlist.txt
# WARNING: No IPv4 address found on ap1 !
# WARNING: No IPv4 address found on en1 !
# WARNING: more No IPv4 address found on en2 !
# Using primary DNS server: dns.jct.ac.il.
# mail.jct.ac.il : 147.161.1.38, 147.161.1.36, 147.161.1.29
# web.jct.ac.il : 147.161.1.37
# avi.jct.ac.il : 147.161.1.46
# (newenv) Bellas-MacBook-Pro:Lab4scapy bellak$