import re

from bs4 import BeautifulSoup

from scripts.core import ContentImage, Chapter
from scripts.util import debugPrint, normalizeURL


def getContentImagesAsurascans(soup: BeautifulSoup) -> [ContentImage]:
    readerarea = soup.find(id="readerarea")
    image_containers = readerarea.findAll("p")
    images = [inner for outer in
              [container.findAll("img") for container in image_containers if container.find("img") is not None] for
              inner in outer]  # idk either bro

    contentImage = [ContentImage(img.get("src"), img.get("width"), img.get("height")) for img in images]
    return contentImage

def makeChapter(page):
    soup = BeautifulSoup(page.content, "html.parser")
    pageTitle = getPageTitle(soup)
    title = getTitle(pageTitle)
    chapterNr = getChapterFromTitle(pageTitle)

    chapter = Chapter(title, chapterNr)

    print(f"Loading: '{title} - {chapterNr}'...")
    images = getContentImagesAsurascans(soup)
    for img in images:
        chapter.addContentImage(img)

    html = page.content.decode('utf-8')

    next_url = getNextURL(html)

    nextChapter = None
    previousChapter = None

    try:
        nextChapter = getChapterFromURL(next_url)
        debugPrint(f"next chapter found at {next_url}")
        debugPrint(f"next chapterNr is {nextChapter}")
    except:
        debugPrint("no next chapter detected")

    prev_url = getPrevURL(html)
    try:
        previousChapter = getChapterFromURL(prev_url)
        debugPrint(f"previous chapter found at {prev_url}")
        debugPrint(f"previous chapterNr is {previousChapter}")
    except:
        previousChapter = None
        debugPrint("no previous chapter detected")

    if nextChapter not in [None, '']:
        chapter.nextChapter = float(nextChapter)
    if previousChapter not in [None, '']:
        chapter.previousChapter = float(previousChapter)

    return chapter

def getChapterFromTitle(pageTitle: str):
    return float(re.search(r'Chapter ([0-9.]+)', pageTitle, re.IGNORECASE).group(1))

def getPageTitle(soup: BeautifulSoup):
    return soup.find("title").getText()

def getTitle(pageTitle: str):
    return re.sub(" Chapter.*$", "", pageTitle, re.IGNORECASE)

def getNextURL(html):
    return normalizeURL(re.search(r'"nextUrl":"([^"]*)"', html).group(1)) or None

def getPrevURL(html):
    return normalizeURL(re.search(r'"prevUrl":"([^"]*)"', html).group(1)) or None

def getChapterFromURL(url: str):
    raw = re.search(r"chapter-([0-9.]+(-[0-9]+)?)[-/]*", url).group(1)
    normalized = raw.strip("-").replace("-", ".")
    return normalized