import requests
import threading
import json

class ChapterDownloader(threading.Thread):
    def __init__(self, chapterId, chapterName, path):
        self.chapterId = chapterId
        self.chapterName = chapterName
        self.path = path

    def run():
        getImageList()
        downloadImages()
        print "Chapter " + chapterName + " Done\n"

    def getImageList(self):
        self.imageList = requests.get("http://www.mangaeden.com/api/chapter/" + chapterId)
        self.imageList = json.loads(self.imageList.text);
        self.imageList = self.imageList["images"]

    def downloadImages(self):
        for img in imageList:
            image = requests.get("http://cdn.mangaeden.com/mangasimg/" + img[1])
            with open(path+"/"+chapterName+"/"+img[0]+".png") as file:
                file.write(image.text)
