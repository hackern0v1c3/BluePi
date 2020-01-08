# Test script for detecting LLMNR spoofing

# Import packages
from scapy.all import *
import threading
import random
import string

# Global variables
DESTINATION_IP = '224.0.0.252' # multicast address for LLMNR
SLEEP_TIME = 10 # number of seconds to sleep between requests

# Function to generate random hostnames
# Used microsofts DNS naming conventions https://support.microsoft.com/en-us/help/909264/naming-conventions-in-active-directory-for-computers-domains-sites-and
def generateName():
    stringLength = random.randint(2, 63)
    lettersAndDigits = string.ascii_letters + string.digits + '.'
    return ''.join(random.choice(lettersAndDigits) for i in range(stringLength))

# Function to send requests
def sender():
    while 1:
        source_port = random.randint(49152, 65535)
        id = random.randint(1, 65535)
        query_name = generateName()
        pkt = IP(dst=DESTINATION_IP, ttl=1)/UDP(sport=source_port,dport=5355)/LLMNRQuery(id=id, qr=0, qdcount=1, ancount=0, nscount=0, arcount=0, qd=DNSQR(qname=query_name))

        send (pkt, verbose=0)
        time.sleep(SLEEP_TIME)

# Handler for incoming responses
def get_packet(pkt):
    if not pkt.getlayer(LLMNRResponse):
        return
    if (pkt.qr == 1) & (pkt.opcode == 0) & (pkt.c == 0) & (pkt.tc == 0) & (pkt.rcode == 0):
        # Get the machine name from the LLMNR response
        response_name = str(pkt.qd.qname, 'utf-8')
        print(f'A spoofed LMNR response for {response_name} was detected by from host {pkt.getlayer(IP).src} - {pkt.getlayer(Ether).src}')

#Function for starting sniffing
def listen():
    sniff(filter="udp and port 5355",store=0,prn=get_packet)

# Main function
def main():
    try:
        try:
            print ("Starting UDP Response Server...")
            threading.Thread(target=listen).start()
            print ("Starting LLMNR Request Thread...")
            threading.Thread(target=sender).start()
        except KeyboardInterrupt:
            print ("\nStopping Server and Exiting...\n")
        except:
            print ("Server could not be started, confirm you're running this as root.\n")
    except KeyboardInterrupt:
        exit()
    except:
        print ("Server could not be started, confirm you're running this as root.\n")

# Launch main
main()