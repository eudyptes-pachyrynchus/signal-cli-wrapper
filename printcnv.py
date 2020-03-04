import sys, os
from colorama import init, Fore, Back, Style
import json
from datetime import datetime

home = os.getenv("HOME")
configpath = home + "/.config/signal-cli-wrapper/config"
conversationspath= home + "/.local/share/signal-cli-wrapper/conversations/"
contacts = {}
colorMe = Fore.GREEN 
colorTrusted = Fore.YELLOW + Style.BRIGHT
colorUntrusted = Fore.YELLOW + Style.BRIGHT

def dateandtime(timestamp):
    dt = datetime.fromtimestamp(ts/1000)
    return '{:%y/%m/%d %H:%M}'.format(dt)

def readConfig(filename):
    global mynum
    with open(filename) as f:    
        for line in f:
            if line.startswith( 'MYNUM='):
                mynum = line[7:len(line)-2]

            if line.startswith( 'NUM') or line.startswith( 'GRP'):
                pair = line.split("=")
                name = pair[0][4:len(pair[0])-1]
                number = pair[1][1:len(pair[1])-2]
                contacts[number] = name

def printsndmsg(name, ts, msg):
    string = "To " + name + " on " + dateandtime(ts) + ": " + msg
    print(colorMe + string)
    
# TODO: yellow if trusted, orange if not
def printrcvmsg(name, ts, msg):
    string = "From " + name + " on " + dateandtime(ts) + ": " + msg
    print(colorUntrusted + string)


# MAIN #

if len(sys.argv) != 2 :
    print('usage: ' + sys.argv[0] + " query")
    print("where query is either a phone number or a group id")
    exit()

init(autoreset=True)
readConfig(configpath)
query = sys.argv[1]
name = contacts.get(query, query)

with open(conversationspath + query) as infile:    
    for line in infile:
        python_obj = json.loads(line)
        e = python_obj["envelope"]
        ts = e["timestamp"]
        source = e["source"]
        d = e["dataMessage"]
        if d == None:
            continue
        msg = d["message"]
        if source == mynum:
            printsndmsg(name, ts, msg)
        else:
            if query[0] == "+":
                printrcvmsg(name, ts, msg)
            else:
                printrcvmsg(contacts.get(source, source), ts, msg)
