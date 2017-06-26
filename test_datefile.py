#!/usr/bin/env python

import time
import requests
import rex

from nxtools import *

SERVER = "push.streampunk.cz"

while True:
    print ("sending tc")
    payload = format_time(time.time())
    file_name = "date.txt"

    result = requests.post(
        "https://" + SERVER,
        data=payload,
        headers={
                "X-Pushkin-Filename" : file_name,
                "X-Pushkin-Key" : "anon"
            }
        )

    print (result.status_code)
    if result.status_code < 400:
        print (result.text)

    time.sleep(5)
