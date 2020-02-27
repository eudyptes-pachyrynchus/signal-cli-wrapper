import sys
from enum import Enum

class State(Enum):
    clear = 1
    snd_to = 2
    snd_timestamp = 3
    snd_body = 4
    rcv_env = 5
    rcv_timestamp = 6
    rcv_sender = 7
    rcv_body = 8
    rcv_key = 9
    rcv_attachment = 10

def extractTime(line):
    timestr = line.split()[2]
    return timestr[1:len(timestr) - 9]
    
def filtermsgs(filename, number, name):

    spaces = "" # * (len(name) )
    state = State.clear

    with open(filename) as f:    
        for line in f:
            # send block
            if state == State.clear and line.startswith( 'Sent to: ' + number ):
                state = State.snd_to
                continue
            if state == State.snd_to and line.startswith( 'Timestamp:' ):
                print("To " + name + " on " + extractTime(line))
                state = State.snd_timestamp
                continue
            if state == State.snd_timestamp and line.startswith( 'Body:' ):
                print(spaces + "<" + line[5:], end='')
                state = State.clear
                continue

            # receive block
            if state == State.clear and line.startswith( 'Envelope from: ' ):
                state = State.rcv_env
                continue
            if state == State.rcv_env and line.startswith( 'Timestamp:' ) :
                timestr = extractTime(line)
                state = State.rcv_timestamp
                continue            
            if state == State.rcv_timestamp and line.startswith( 'Sender: ' + number ):
                state = State.rcv_sender
                print(name + " on " + timestr)                        
                continue        
            if state == State.rcv_sender and line.startswith( 'Body:' ):
                state = State.rcv_body
                line = line[5:]
                if line.strip():
                    print(spaces + " > " + line, end='')
                continue
            #read body until we reach the line 'Profile key update ...'
            if state == State.rcv_body:
                if line.startswith( 'Profile key update, key length:' ):
                    state = State.rcv_key
                    continue
                if line.strip():
                    print(spaces + " > " + line, end='')
                    continue

            #attachment?
            if state == State.rcv_key:
                if not line.strip():
                    state = State.clear                
                    continue
                if line.startswith( 'Attachments:' ) :
                    state = State.rcv_attachment
                    print(spaces + " > " + line, end='')
                    continue
            if state == State.rcv_attachment:
                if not line.strip():
                    state = State.clear
                    print()
                else:
                    print(spaces + " > " + line, end='')
                continue
    
#main
if len(sys.argv) != 4:
    print('usage: ' + sys.argv[0] + " path-to-msgs number name")
else:
    filtermsgs(sys.argv[1], sys.argv[2], sys.argv[3])
