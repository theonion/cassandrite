from datetime import datetime
import json
from random import choice
import time

import requests


while 1:
    now = time.mktime(datetime.now().timetuple())
    payload = {
        'path': 'some-path-name',
        'data': choice(range(2, 15)),
        'time': now,
    }
    res = requests.post('http://localhost:8080/', data=json.dumps(payload))
    print(now, res)
    time.sleep(choice(range(1, 10)))
