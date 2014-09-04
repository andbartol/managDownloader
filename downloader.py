import errno
import json
import os
import requests
import threading

class ChapterDownloader(threading.Thread):
    def __init__(self, chapterId, chapterName, path):
        super(ChapterDownloader, self).__init__()
        self.chapterId = chapterId
        self.chapterName = chapterName
        self.path = path

    def run(self):
        self.getImageList()
        self.downloadImages()
        print "Chapter " + self.chapterName + " Done\n"

    def getImageList(self):
        self.imageList = requests.get("http://www.mangaeden.com/api/chapter/" + self.chapterId)
        self.imageList = json.loads(self.imageList.text);
        self.imageList = self.imageList["images"]

    def downloadImages(self):
        for img in self.imageList:
            image = requests.get("http://cdn.mangaeden.com/mangasimg/" + img[1])
            finalpath = os.path.join(self.path, self.chapterName)
            #create the directory
            try:
                os.makedirs(finalpath)
            except OSError as exception:
                if exception.errno != errno.EEXIST:
                    raise
            #start writing
            with open(os.path.join(finalpath, str(img[0])+".jpg"), "wb") as file:
                file.write(image.text.encode("UTF-8"))

foo = ChapterDownloader("5064306fc092253769022d52", "36", "/home/andrea/mangaedenDownloads")
foo.start()
foo.join()
