"""
YOU NEED NOT HAVE TO EDIT THIS FILE.

This is a client file that will send request to the server with a number
You can however use this file and make some changes that would assist you in
testing your framework
"""
import requests
import sys
import time

if __name__ == "__main__":
    num = 0
    while True:
        num += 1
        payload = {
            'num': num,
        }
        r = requests.get("http://%s" % sys.argv[1], params=payload)
        if r.status_code == requests.code.ok:
            print r.text
        else:
            print "No response"
        time.sleep(2)
