import traceback
from tkinter.filedialog import askdirectory

import scripts.asurascraper as ASURA
import scripts.chapmanganatoscraper as CHAPMANGANATO
from scripts.util import *


def requestUrlFromUser():
    url = input("Enter the url of a chapter from a supported site ==> ")
    while getSite(url) == None:
        url = input("The entered link is invalid, or is from a website that isn't supported (yet). Supported websites are: 'asuracomics.com, chapmanganato.com' Please try again ==> ")
    return url


def requestChapterAmountFromUser():
    limit = input("Enter how many chapters you want to download, just press enter if there is no limit ==> ")
    if not re.compile("^[0-9]+$").match(limit):
        return 99999999
    return int(limit)

def getSite(url):
    site = None
    if url.startswith("https://asura"):
        site = "ASURASCANS"
    elif url.startswith("https://chapmanganato"):
        site = "CHAPMANGANATO"
    else:
        debugPrint("site not supported")
        return None

    return site

def getNextChapterURL(site, page):
    if site == "ASURASCANS":
        return ASURA.getNextURL(page.content.decode("utf-8"))
    elif site == "CHAPMANGANATO":
        return CHAPMANGANATO.getNextURL(page)

def getChapter(site, page):
    if site == "ASURASCANS":
        return ASURA.makeChapter(page)
    elif site == "CHAPMANGANATO":
        return CHAPMANGANATO.makeChapter(page)

def getHeaders(site):
    if site == "CHAPMANGANATO":
        return {'Referer': 'https://chapmanganato.com/'}

def UI():
    print("Welcome to 'Unnamed Manwha Scraper v1.1' by Acheros.")
    print("Feedback is appreciated and can be sent via discord '_acheros'.\n")

    while True:
        url = requestUrlFromUser()
        site = getSite(url)
        debugPrint("selected site is " + site)
        limit = requestChapterAmountFromUser()

        print("Select the folder where you want to download the chapters.")
        path = askdirectory(title='Select Folder')
        print("Path selected: " + path)
        print("loading chapters...")
        chapters = []
        page = requests.get(url)
        nextChapter = getNextChapterURL(site, page)
        chapter = getChapter(site, page)
        chapters.append(chapter)
        i = 1

        while nextChapter is not None and i < limit:
            page = requests.get(nextChapter)
            nextChapter = getNextChapterURL(site, page)
            chapters.append(getChapter(site, page))
            i += 1

        print(f"Found {len(chapters)} chapters")

        for ch in chapters:
            ch.buildHTML(path, getHeaders(site))

        print((f"All {len(chapters)} chapters were" if len(chapters) > 1 else "Chapter was") + " downloaded and built succesfully. Enjoy!\n")


try:
    UI()
except:
    traceback.print_exc()
