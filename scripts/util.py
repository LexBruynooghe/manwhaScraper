import re
import platform
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

def getUserSystem():
    system = platform.system()

    if system == 'Linux':
        # Check for Android by examining the kernel version
        with open('/proc/version', 'r') as version_file:
            if 'Android' in version_file.read():
                return 'Android'
        # If not Android, assume Linux desktop
        return 'Linux Desktop'

    elif system == 'Darwin':
        return 'MacOS'

    elif system == 'Windows':
        return 'Windows'

    else:
        return 'Unknown'

def isDesktop(system: str):
    return system in ['MacOS', 'Windows']
