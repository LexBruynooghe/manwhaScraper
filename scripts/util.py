import re

import requests

DEBUGGING = False
def debugPrint(msg):
    if DEBUGGING:
        print(msg)
def downloadImage(url, path: str):
    data = requests.get(url).content
    f = open(path, 'wb')
    f.write(data)
    f.close()

def normalizeURL(url):
    return re.sub(r"[\\]", "", url)

