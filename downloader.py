import errno
import json
import os
import requests
import sys
import threading

class ChapterDownloader(threading.Thread):
    def __init__(self, chapterId, chapterName, path):
        super(ChapterDownloader, self).__init__()
        self.chapterId = chapterId
        self.chapterName = chapterName
        self.path = path

    def run(self):
        print "Chapter %s started" % self.chapterName
        self.getImageList()
        self.downloadImages()
        print "Chapter " + self.chapterName + " Done"

    def getImageList(self):
        self.imageList = requests.get("http://www.mangaeden.com/api/chapter/" + self.chapterId)
        self.imageList = json.loads(self.imageList.text);
        self.imageList = self.imageList["images"]

    def downloadImages(self):
        for img in reversed(self.imageList):
            try:
                image = requests.get("http://cdn.mangaeden.com/mangasimg/" + img[1])
            except HTTPConnectionPool as exception:
                pass
            finalpath = os.path.join(self.path, self.chapterName)
            #create the directory
            try:
                os.makedirs(finalpath)
            except OSError as exception:
                if exception.errno != errno.EEXIST:
                    raise
            #start writing
            extension = img[1].split(".")[-1]
            with open(os.path.join(finalpath, str(img[0])+"." + extension), "wb") as file:
                for block in image.iter_content(1024):
                    if not block:
                        break
                    file.write(block)

def findManga(mangaName, mangaList):
    for manga in mangaList["manga"]:
        if manga["a"] == mangaName:
            return manga["i"]
    raise Exception("Manga not found")

def findChapterCodesNames(chapterList, findList):
    finalList = []
    nameList = []
    for chapterNumber in findList:
        for num in chapterList["chapters"]:
            if num[0] == chapterNumber:
                finalList.append(num[3])
                nameList.append(num[2])
                break
        else:
            raise Exception("Chapter not find")
    return finalList, nameList

#Program start
if len(sys.argv) < 4:
    print "Usage: %s mangaName chapterStart-chapterEnd path" % sys.argv[0]
    exit();

chapters = sys.argv[2].split("-")
mangaList = requests.get("http://www.mangaeden.com/api/list/1/")
mangaList = json.loads(mangaList.text)
mangaIndex = findManga(sys.argv[1], mangaList)
chapterList = requests.get("https://www.mangaeden.com/api/manga/" + mangaIndex)
chapterList = json.loads(chapterList.text)
chapters = range(int(chapters[0]), int(chapters[1])+1)
download, names = findChapterCodesNames(chapterList, chapters)
chapterDownloadList = []
for i in range(len(download)):
    chapterDownloadList.append(ChapterDownloader(download[i], str(chapters[i]) + " - " + names[i], sys.argv[3]))
    chapterDownloadList[i].start()
for c in chapterDownloadList:
    c.join()
