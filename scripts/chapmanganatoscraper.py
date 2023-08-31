import re

from bs4 import BeautifulSoup

from scripts.core import ContentImage, Chapter
from scripts.util import debugPrint, normalizeURL


def getContentImages(soup: BeautifulSoup) -> [ContentImage]:
    readerarea = soup.find(class_="container-chapter-reader")

    images = [img for img in readerarea.findAll("img")]

    contentImage = [ContentImage(img.get("src"), img.get("width"), img.get("height")) for img in images]
    return contentImage

def makeChapter(page):
    soup = BeautifulSoup(page.content, "html.parser")
    pageTitle = getPageTitle(soup)
    title = getTitle(pageTitle)
    chapterNr = getChapterFromTitle(pageTitle)

    chapter = Chapter(title, chapterNr)

    print(f"Loading: '{title} - {chapterNr}'...")
    images = getContentImages(soup)
    for img in images:
        chapter.addContentImage(img)

    html = page.content.decode('utf-8')
    next_url = getNextURL(page)
    nextChapter = None
    previousChapter = None

    try:
        nextChapter = getChapterFromURL(next_url)
        debugPrint(f"next chapter found at {next_url}")
        debugPrint(f"next chapterNr is {nextChapter}")
    except:
        debugPrint("no next chapter detected")

    prev_url = getPrevURL(page)
    try:
        previousChapter = getChapterFromURL(prev_url)
        debugPrint(f"previous chapter found at {prev_url}")
        debugPrint(f"previous chapterNr is {previousChapter}")
    except:
        previousChapter = None
        debugPrint("no previous chapter detected")

    if nextChapter is not None:
        chapter.nextChapter = float(nextChapter)
    if previousChapter is not None:
        chapter.previousChapter = float(previousChapter)

    return chapter

def getChapterFromTitle(pageTitle: str):
    return float(re.search(r'Chapter ([0-9.]+)', pageTitle, re.IGNORECASE).group(1))

def getPageTitle(soup: BeautifulSoup):
    return soup.find("title").getText()

def getTitle(pageTitle: str):
    return re.sub(" Chapter.*$", "", pageTitle, re.IGNORECASE)

def getNextURL(page):
    soup = BeautifulSoup(page.content, "html.parser")
    element = soup.find("a", class_="navi-change-chapter-btn-next")

    if element is None:
        return element

    url = normalizeURL(element.get("href"))
    return url

def getPrevURL(page):
    soup = BeautifulSoup(page.content, "html.parser")
    element = soup.find("a", class_="navi-change-chapter-btn-prev")

    if element is None:
        return element

    url = normalizeURL(element.get("href"))
    return url

def getChapterFromURL(url: str):
    raw = re.search(r"chapter-([0-9.]+(-[0-9]+)?)[-/]*", url).group(1)
    normalized = raw.strip("-").replace("-", ".")
    return normalized or None


