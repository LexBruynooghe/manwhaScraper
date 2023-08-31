import re

import requests

DEBUGGING = False
def debugPrint(msg):
    if DEBUGGING:
        print(msg)
def downloadImage(url, path: str, headers = None):
    data = requests.get(url, headers=headers).content
    f = open(path, 'wb')
    f.write(data)
    f.close()

def normalizeURL(url):
    return re.sub(r"[\\]", "", url)



