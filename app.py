from flask import Flask, render_template, send_from_directory
from concurrent.futures import ThreadPoolExecutor

from flask.helpers import send_file
from bs4 import BeautifulSoup
from PIL import Image
import requests
import os.path
import shutil
import lxml
import os
import re
app = Flask(__name__)

@app.route('/')
def index():
  return render_template('index.html')

@app.route('/downloadManga/')
def my_link():
    imgList = []
    UrlList = []
    pdfList = []

    url = "https://mangafast.net/shingeki-no-kyojin-before-the-fall-chapter-1/"
    html = requests.get(url).text
    soup = BeautifulSoup(html, "lxml")

    currentDirectory = os.getcwd() #get current working directory
    directoryName = "ShingekiNoKyojinBeforeTheFall" #name of new directory
    if os.path.exists(directoryName + ".pdf"):
        return send_file(directoryName + '.pdf', as_attachment=True)
    else:
        path = os.path.join(currentDirectory, directoryName) #join current path and new directory
        os.mkdir(path) #make the directory

        imgs = soup.findAll("img", {"title": re.compile(r"Shingeki No Kyojin Before The Fall Chapter 1 Page")})

        for img in imgs:
            imgUrl = img['src']
            UrlList.append(imgUrl) #list of Urls
            filename = imgUrl.split('/')[-1] #file name (.jpg)
            imgPath = path + '/' + filename #path to image
            imgList.append(imgPath) #final location of images


        def download(url, images): #gets images and saves them to previously generated directory
            response = requests.get(url, stream = True)
            if response.status_code == 200:
                response.raw.decode_content = True
                img = Image.open(response.raw)
                img.save(images) 
                print('Success')
            else:
                print('Failure.')

        with ThreadPoolExecutor(max_workers=32) as executor: #multithreading to speed up downloads
            executor.map(download, UrlList, imgList)

        for images in imgList: #generates list of Image objects
            thisImage = Image.open(images)
            pdfList.append(thisImage)

        newList = pdfList[1:] #ensures the last page is not saved first due to implementation of PIL
        pdfList[0].save(directoryName + '.pdf',save_all=True, append_images=newList) #saves images as single pdf

        try:
            shutil.rmtree(path) #removes the generated directory and all images
        except OSError as e:
            print("Error: %s : %s" % (path, e.strerror))

        print("End")
        return send_file(directoryName + '.pdf', as_attachment=True)
if __name__ == '__main__':
  app.run(debug=True)
