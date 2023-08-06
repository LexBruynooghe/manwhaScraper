import requests
import os
import re
import shutil
from tkinter.filedialog import askdirectory
from bs4 import BeautifulSoup


class ContentImage:
    def __init__(self, url: str, width: int, height: int):
        self.url = url
        self.width = width
        self.height = height

    def __str__(self):
        return self.url + " " + str(self.width) + "x" + str(self.height)


class Chapter:
    def __init__(self, title: str, chapter: float):
        self.title = title
        self.chapter = chapter
        self.content: list[ContentImage] = []
        self.nextChapter = None
        self.previousChapter = None

    def addContentImage(self, contentImage: ContentImage):
        self.content.append(contentImage)

    def setPrevious(self, prevChapter):
        self.previousChapter = prevChapter

    def setNext(self, nextChapter):
        self.nextChapter = nextChapter

    def buildHTML(self, path: str):
        chapter_dir = os.path.join(path, "Chapter_" + str(self.chapter))
        chapter_html = os.path.join(chapter_dir, "read.html")
        print(f"building chapter: {self.title + ' - ' + str(self.chapter)} at {os.path.abspath(chapter_html)}")
        try:
            os.mkdir(chapter_dir)
        except:
            print("Chapter directory already exists, overwriting existing chapter...")
            shutil.rmtree(chapter_dir)
            os.mkdir(chapter_dir)

        print(f"building chapter ")
        f = open(chapter_html, 'w')

        start = [
            '<!DOCTYPE html>',
            '<html lang="en">',
            '<head>',
            '    <meta charset="UTF-8">',
            f'    <title>{self.title + " - " + str(self.chapter)}</title>',
            '<style>.readerarea{text-align: center;padding: 10px;}.main{background:#1e1f22;}.menu{background: #3f3f3f;padding: 5px 50px 5px 50px;text-align: right;}  .nav {border-radius: 10px; border: 0;background-color: #c7a669;padding: 5px 10px 5px 10px; margin-left: 10px; font-family: "Helvetica Neue", arial, sans-serif; font-size: 18px; color: #886464;}.nav:hover {background-color: #b78730;cursor: pointer;}</style>',
            '<script type="text/javascript">',
            "function loadNextChapter() {window.location.href = '../Chapter_" + str(
                self.nextChapter) + "/read.html'}" if self.nextChapter is not None else "",
            "function loadPrevChapter() {window.location.href = '../Chapter_" + str(
                self.previousChapter) + "/read.html'}" if self.previousChapter is not None else "",
            '</script>',
            '</head>',
            '<body class="main">',
            '<div class="menu">',
            '<button class="nav" onclick="loadPrevChapter()">Prev</button>' if self.previousChapter is not None else "",
            '<button class="nav" onclick="loadNextChapter()">Next</button>' if self.nextChapter is not None else "",
            '</div>',
            '<div class="readerarea">'
        ]

        for i in range(len(self.content)):
            print(f"downloading image {i + 1}/{len(self.content)}")
            name = f"ChapterContent{i}"
            img_path = os.path.join(chapter_dir, f"{name}.jpg")
            downloadImage(self.content[i].url, img_path)
            start.append(
                f'<p><img decoding="async" loading="lazy" src="{name}.jpg" width="{self.content[i].width}" height="{self.content[i].height}" class="readcontent"><p>')

        end = [
            '</div>',
            '<div class="menu">',
            '<button class="nav" onclick="loadPrevChapter()">Prev</button>' if self.previousChapter is not None else "",
            '<button class="nav" onclick="loadNextChapter()">Next</button>' if self.nextChapter is not None else "",
            '</div>',
            '</body>',
            '</html>'
        ]

        lines = start + end
        f.writelines([line + "\n" for line in lines])
        f.close()
        print("Chapter was built succesfully!")


def getContentImages(soup: BeautifulSoup) -> [ContentImage]:
    readerarea = soup.find(id="readerarea")
    images = readerarea.findAll("img")
    return [ContentImage(img.attrs["src"], img.attrs["width"], img.attrs["height"]) for img in images]


def getPageTitle(soup: BeautifulSoup):
    return soup.find("title").getText()


def getTitle(pageTitle: str):
    return re.sub(" Chapter.*$", "", pageTitle)


def getChapter(pageTitle: str):
    for id in re.finditer(r'Chapter ([0-9.,-]+)', pageTitle):
        return float(id.group(1))


def downloadImage(url, path: str):
    data = requests.get(url).content
    f = open(path, 'wb')
    f.write(data)
    f.close()


def getNextURL(html):
    for id in re.finditer(r'"nextUrl":"([^"]*)"', html):
        return normalizeURL(id.group(1))
    return None


def getPrevURL(html):
    for id in re.finditer(r'"prevUrl":"([^"]*)"', html):
        return normalizeURL(id.group(1))
    return None

def normalizeURL(url):
    return re.sub(r"[\\]", "", url)


def makeChapter(page):
    soup = BeautifulSoup(page.content, "html.parser")
    pageTitle = getPageTitle(soup)
    title = getTitle(pageTitle)
    chapterNr = getChapter(pageTitle)

    chapter = Chapter(title, chapterNr)

    images = getContentImages(soup)
    for img in images:
        chapter.addContentImage(img)

    html = page.content.decode('utf-8')

    next_url = getNextURL(html)
    try:
        nextChapter = re.finditer(r"chapter-([0-9.]*)[-/]*", next_url).__next__().group(1)
    except:
        nextChapter = None

    prev_url = getPrevURL(html)
    try:
        previousChapter = re.finditer(r"chapter-([0-9.]*)[-/]*", prev_url).__next__().group(1)
    except:
        previousChapter = None

    if nextChapter is not None:
        chapter.nextChapter = float(nextChapter)
    if previousChapter is not None:
        chapter.previousChapter = float(previousChapter)

    return chapter

def UI():
    print("Welcome to 'Unnamed Manwha Scraper v0.1' by Acheros.")
    print("Feedback is appreciated and can be sent via discord '_acheros'.\n")

    while True:
        url = input("Enter the url of a chapter (currently only Asura scans) ==> ")
        limit = input("Enter how many chapters you want to download, just press enter if there is no limit ==> ")
        if limit == "":
            limit = 99999999
        else:
            limit = int(limit)
        print("Select the folder where you want to download the chapters.")
        path = askdirectory(title='Select Folder')
        print("Path selected: " + path)

        print("loading chapters...")
        chapters = []

        page = requests.get(url)
        nextChapter = getNextURL(page.content.decode('utf-8'))
        chapter = makeChapter(page)
        chapters.append(chapter)
        i = 1
        while (nextChapter is not None and nextChapter != "") and i < limit:
            page = requests.get(nextChapter)
            nextChapter = getNextURL(page.content.decode('utf-8'))
            chapters.append(makeChapter(page))
            i += 1

        print(f"Found {len(chapters)} chapters")

        for ch in chapters:
            ch.buildHTML(path)

        print(f"All {len(chapters)} chapters were built downloaded and built succesfully. Enjoy!\n")

UI()
