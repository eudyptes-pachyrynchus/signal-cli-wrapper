import sys, os
import json

home = os.getenv("HOME")
conversationspath= home + "/.local/share/signal-cli-wrapper/conversations/"

for line in sys.stdin:
    python_obj = json.loads(line)
    e = python_obj["envelope"]
    if (e["isReceipt"]) == False:
        d = e["dataMessage"]
        if d == None:
            continue
        try:
            filename = d["groupInfo"]["groupId"]
        except (ValueError, KeyError, TypeError):
            filename = e["source"]
        finally:
            with open(conversationspath + filename, "a") as outfile:
                outfile.write(line)
