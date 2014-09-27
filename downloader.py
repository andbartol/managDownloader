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
        semaphore.acquire()
        print "Chapter %s started" % self.chapterName
        self.getImageList()
        self.downloadImages()
        print "Chapter " + self.chapterName + " Done"
        semaphore.release()

    def getImageList(self):
        self.imageList = requests.get("http://www.mangaeden.com/api/chapter/" + self.chapterId)
        self.imageList = json.loads(self.imageList.text);
        self.imageList = self.imageList["images"]

    def downloadImages(self):
        for img in reversed(self.imageList):
            while True:
                try:
                    image = requests.get("http://cdn.mangaeden.com/mangasimg/" + img[1])
                except Exception as exception:
                    continue
                break
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
            raise Exception("Chapter not found")
    return finalList, nameList

def chapterParser(chapters):
    returnlist = []
    chapters = chapters.split(',')
    for i in range(len(chapters)):
        chapters[i] = chapters[i].split('-')
    for c in chapters:
        if len(c) == 1:
            returnlist.append(int(c[0]))
        else:
            for i in range(int(c[0]), int(c[1])+1):
                returnlist.append(i)
    return returnlist

#Program start
if len(sys.argv) < 5:
    print "Usage: %s mangaName chapterStart-chapterEnd path download_simultanei" % sys.argv[0]
    exit();

#chapters = sys.argv[2].split("-")
print "Downloading Manga List"
mangaList = requests.get("http://www.mangaeden.com/api/list/1/")
print "Manga List Downloaded"
mangaList = json.loads(mangaList.text)
try:
    mangaIndex = findManga(sys.argv[1], mangaList)
except Exception as e:
    print e.message
    quit()
print "Downloading chapter list"
chapterList = requests.get("https://www.mangaeden.com/api/manga/" + mangaIndex)
print "Chapter list downloaded"
chapterList = json.loads(chapterList.text)
#chapters = range(int(chapters[0]), int(chapters[1])+1)
chapters = chapterParser(sys.argv[2])
try:
    download, names = findChapterCodesNames(chapterList, chapters)
except Exception as e:
    print e.message
    quit()
chapterDownloadList = []
sim_down = int(sys.argv[4])
semaphore = threading.Semaphore(sim_down)
for i in range(len(download)):
    chapterDownloadList.append(ChapterDownloader(download[i], str(chapters[i]) + " - " + names[i], sys.argv[3]))
    chapterDownloadList[i].start()
