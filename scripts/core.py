import os
import shutil
import threading

from scripts.util import downloadImage, debugPrint


class ContentImage:
    def __init__(self, url: str, width: int = None, height: int = None):
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

    def __str__(self):
        return ", ".join([self.title, self.chapter,
                          self.content]) + " - " + f"prev: {self.previousChapter}" + f"next: {self.nextChapter}"

    def buildHTML(self, path: str, headers=None):
        chapter_dir = os.path.join(path, "Chapter_" + str(self.chapter))
        chapter_html = os.path.join(chapter_dir, "read.html")
        content_dir = os.path.join(chapter_dir, "content")
        styles_dir = os.path.join(chapter_dir, "styles")
        print(f"building chapter: {self.title + ' - ' + str(self.chapter)} at {os.path.abspath(chapter_html)}")
        try:
            os.mkdir(chapter_dir)
        except:
            print("Chapter directory already exists, overwriting existing chapter...")
            shutil.rmtree(chapter_dir)
            os.mkdir(chapter_dir)

        os.mkdir(content_dir)
        os.mkdir(styles_dir)

        chapter_css = os.path.join(styles_dir, "chapter.css")
        shutil.copyfile("./styles/styles.css", chapter_css)

        start = [
            '<!DOCTYPE html>',
            '<html lang="en">',
            '<head>',
            '    <meta charset="UTF-8">',
            f'    <title>{self.title + " - " + str(self.chapter)}</title>',
            '<link rel="stylesheet" href="styles/chapter.css">',
            '<script type="text/javascript">',
            "function loadNextChapter() {window.location.href = '../Chapter_" + str(
                self.nextChapter) + "/read.html'}" if self.nextChapter is not None else "",
            "function loadPrevChapter() {window.location.href = '../Chapter_" + str(
                self.previousChapter) + "/read.html'}" if self.previousChapter is not None else "",
            '</script>',
            '</head>',
            '<body class="main">',
            '<div class="menu">',
            '<button class="nav" onclick="loadPrevChapter()">< Prev</button>' if self.previousChapter is not None else "",
            '<button class="nav" onclick="loadNextChapter()">Next ></button>' if self.nextChapter is not None else "",
            '</div>',
            '<div class="readerarea">'
        ]

        threads = []

        print(f"downloading content...")
        for i in range(len(self.content)):
            name = f"ChapterContent{i}"
            img_path = os.path.join(content_dir, f"{name}.jpg")
            t = threading.Thread(target=threadDownload, args=(self.content[i].url, img_path, i, headers,))
            threads.append(t)
            width = self.content[i].width
            height = self.content[i].height
            start.append(f'<p><img decoding="async" loading="lazy" src="{os.path.basename(content_dir)}/{name}.jpg"' + (f' width="{width}"' if width is not None else '') + (f' height="{height}"' if height is not None else '') + ' class="readcontent"></p>')

        for thread in threads:
            thread.start()

        for thread in threads:
            thread.join()

        end = [
            '</div>',
            '<div class="menu">',
            '<button class="nav" onclick="loadPrevChapter()">< Prev</button>' if self.previousChapter is not None else "",
            '<button class="nav" onclick="loadNextChapter()">Next ></button>' if self.nextChapter is not None else "",
            '</div>',
            '</body>',
            '</html>'
        ]

        f = open(chapter_html, 'w')
        lines = start + end
        f.writelines([line + "\n" for line in lines])
        f.close()
        print("Chapter was built succesfully!\n")

def threadDownload(url, path, i, headers = None):
    debugPrint(f"thread ({i}) started for download of " + url)
    downloadImage(url, path, headers)
    debugPrint(f"thread ({i}) finished for download of " + url)

