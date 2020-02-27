import sys
from enum import Enum
from colorama import init, Fore, Back, Style

class State(Enum):
    clear = 1
    snd_to = 2
    snd_timestamp = 3
    snd_body = 4
    rcv_env = 5
    rcv_timestamp = 6
    rcv_sender = 7
    rcv_body = 8
    rcv_groupbody = 9
    rcv_groupinfo = 10
    rcv_groupid = 11
    rcv_key = 12
    rcv_attachment = 13
    rcv_msgcomplete = 14

contacts = {}

colorMe = Fore.GREEN + Style.BRIGHT
colorTrusted = Fore.YELLOW + Style.BRIGHT
colorUntrusted = Fore.YELLOW + Style.BRIGHT
init(autoreset=True)

def extractTime(line):
    timestr = line.split()[2]
    return timestr[1:len(timestr) - 9]

def extractNumber(str):
    if str[0] == '+':
        return str
    elif str[0] == '(':
        return str[1:len(str)-1]
    else:
        return ""

def readContacts(filename):
    with open(filename) as f:
        for line in f:
            pair = line.split()
            if len(pair) == 1:
                # unknown number
                name = "?"
                number = pair[0]
            elif len(pair) == 2:
                name = pair[0]
                number = extractNumber(pair[1])
            contacts[number] = name

def printsndmsg(name, ts, msg):
    string = "To " + name + " on " + ts + ": " + msg
    print(colorMe + string)
    
# TODO: yellow if trusted, orange if not
def printrcvmsg(name, ts, msg):
    string = "From " + name + " on " + ts + ": " + msg
    print(colorUntrusted + string)

def filtermsgs(filename, isgroup, query, name):

    spaces = "" # * (len(name) )
    state = State.clear

    with open(filename) as f:    
        for line in f:

            # send block
            if state == State.clear and line.startswith( 'Sent to: ' + query ):
                state = State.snd_to
                continue
            if state == State.snd_to and line.startswith( 'Timestamp:' ):
                ts = extractTime(line)
                state = State.snd_timestamp
                continue
            if state == State.snd_timestamp and line.startswith( 'Body:' ):
                msg = line[5:]
                printsndmsg(name, ts, msg)
                state = State.clear
                continue

            # receive block
            if state == State.clear and line.startswith( 'Envelope from: ' ):
                msg = ""
                state = State.rcv_env
                continue
            if state == State.rcv_env and line.startswith( 'Timestamp:' ) :
                ts = extractTime(line)
                state = State.rcv_timestamp
                continue

            # handle exceptions and receipts
            if state == State.rcv_timestamp:
                if line.startswith( 'Got receipt.') or line.startswith( 'Exception:'):
                    state = State.clear
                    continue

            if state == State.rcv_timestamp and line.startswith( 'Sender: '):
                number = extractNumber(line.split()[-3])
                # if requesting a single number and the sender does not match
                # then we can abort
                if not isgroup and number != query:
                    state = State.clear
                else:
                    state = State.rcv_sender
                continue        

            # handle other receipts
            if state == State.rcv_sender:
                if line.startswith( 'Received a receipt message'):
                    state = State.clear
                    continue

            if state == State.rcv_sender and line.startswith( 'Body:' ):
                if isgroup:
                    state = State.rcv_groupbody
                else:
                    state = State.rcv_body
                msg = line[5:]
                continue

            #read body until we reach the line 'Profile key update ...'
            #skip this message if 'Group info' appears
            if state == State.rcv_body:
                if line.startswith( 'Group info:' ):
                    state = State.clear
                    continue

                if line.startswith( 'Profile key update, key length:' ):
                    state = State.rcv_key
                    continue

                if line.strip():
                    msg += line
                    continue

            #read body until we reach the line 'Group info:'
            if state == State.rcv_groupbody:

                if line.startswith( 'Group info:' ):
                    state = State.rcv_groupinfo
                    continue

                if line.strip():
                    msg += line
                    continue

            if state == State.rcv_groupinfo and line.split()[0] == 'Id:':
                if query == line[6:len(line)-1]:
                    state = State.rcv_groupid
                else:
                    state = State.clear
                continue

            if state == State.rcv_groupid:
                if line.startswith( 'Profile key update' ):
                    state = State.rcv_key
                    continue
                elif not line.strip():
                    state = State.rcv_msgcomplete
                    #no continue

            #attachment?
            if state == State.rcv_key:
                if line.startswith( 'Attachments:' ) :
                    state = State.rcv_attachment
                    msg += line
                else:
                    state = State.rcv_msgcomplete
                continue

            if state == State.rcv_attachment:
                if line.strip():
                    msg += line
                else:
                    state = State.rcv_msgcomplete
                continue

            if state == State.rcv_msgcomplete:
                printrcvmsg(contacts.get(number), ts, msg)
                state = State.clear

#main
if len(sys.argv) != 6 and (sys.argv[2] != "-n" or sys.argv[2] != "-g"):
    print('usage: ' + sys.argv[0] + " path-to-msgs query name path-to-ids")
    print('        where query is either "-n number" or "-g group"')
else:
    readContacts(sys.argv[5])
    if sys.argv[2] == "-n":
        isgroup = False
    else:
        isgroup = True
    filtermsgs(sys.argv[1], isgroup , sys.argv[3], sys.argv[4])
