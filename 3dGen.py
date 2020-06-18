from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PIL import Image
from PIL.ImageQt import ImageQt
from io import BytesIO
import os
import urllib.request
import requests
import numpy as np
import sys
import cv2
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure

def disparity(imgL_, imgR_):
    kernel = np.ones((3,3),np.uint8)
    stereo = cv2.StereoBM_create(numDisparities=16, blockSize=15)
    disparity = stereo.compute(imgL_,imgR_)
    threshold = cv2.threshold(disparity, 0.6, 1.0, cv2.THRESH_BINARY)[1]
    morphology = cv2.morphologyEx(threshold, cv2.MORPH_OPEN, kernel)
    return imgL_, disparity, threshold, morphology

def url_to_image(url):
    # download the image, convert it to a NumPy array, and then read
    # it into OpenCV format
    resp = urllib.request.urlopen(url)
    image = np.asarray(bytearray(resp.read()), dtype="uint8")
    image = cv2.imdecode(image, cv2.IMREAD_COLOR,)

    # return the image
    return image

def main():
    app = QApplication([])
    tabWindow = QTabWidget()
    tabWindow.setWindowTitle("3dGen")
    MainWindow = QWidget()
    urlWindow = QWidget()
    cameraWindow = QWidget()
    imgLayout = QVBoxLayout()
    imgShowLayout = QHBoxLayout()
    depthMapLayout = QHBoxLayout()
    
    ##Label
    labelImgL = QLabel()
    labelImgR = QLabel()
    staticCanvas = FigureCanvas(Figure(figsize=(5,3)))
    #labelDisparity = QLabel()
    #lableMorphology = QLabel()
    #file = ''
    ##imgSelection
    imgSelectionLayout = QHBoxLayout()
    bibSelectionLayouts = [QVBoxLayout() for i in range(2)]
    pathLTextbox = QLineEdit()
    pathLTextbox.setReadOnly(True)
    def SearchFileL():
        file = QFileDialog()
        file.setFileMode(QFileDialog.AnyFile)
        file.setNameFilter("Images (*.png *.jpg)")
        file.setViewMode(QFileDialog.Detail)
        pathLTextbox.setText(file.getOpenFileName()[0])
        imgL = QPixmap(pathLTextbox.text())
        
        labelImgL.setPixmap(imgL)
    selectLButton = QPushButton("Select Left img")
    selectLButton.clicked.connect(SearchFileL)
    bibSelectionLayouts[0].addWidget(QLabel("Left image"))
    bibSelectionLayouts[0].addWidget(pathLTextbox)
    bibSelectionLayouts[0].addWidget(selectLButton)
    pathRTextbox = QLineEdit()
    pathRTextbox.setReadOnly(True)
    def SearchFileR():
        file = QFileDialog()
        file.setFileMode(QFileDialog.AnyFile)
        file.setNameFilter("Images (*.png *.jpg)")
        file.setViewMode(QFileDialog.Detail)
        pathRTextbox.setText(file.getOpenFileName()[0])
        imgR = QPixmap(pathRTextbox.text())
        labelImgR.setPixmap(imgR)
    selectRButton = QPushButton("Select Right img")
    selectRButton.clicked.connect(SearchFileR)
    bibSelectionLayouts[1].addWidget(QLabel("Right image"))
    bibSelectionLayouts[1].addWidget(pathRTextbox)
    bibSelectionLayouts[1].addWidget(selectRButton)

    def showDepthMap():
        imgL = cv2.imread(pathLTextbox.text(),0)
        imgR = cv2.imread(pathRTextbox.text(),0)
        imgL_, disparity_, threshold, morphology=disparity(imgL, imgR)
        gImage = QPixmap.fromImage(ImageQt(Image.fromarray(imgL_)))
        staticCanvas.figure.subplots().imshow(disparity_)
        #labelDisparity.setPixmap(disparityF)
        #lableMorphology.setPixmap(gImage)
        

    btnShowDepthMap = QPushButton("Show DepthMap")
    btnShowDepthMap.clicked.connect(showDepthMap)
    depthMapLayout.addWidget(staticCanvas)
    #depthMapLayout.addWidget(lableMorphology)

    for i in range(2):
        imgSelectionLayout.addLayout(bibSelectionLayouts[i])
    imgShowLayout.addWidget(labelImgL)
    imgShowLayout.addWidget(labelImgR)
    imgLayout.addLayout(imgSelectionLayout)
    imgLayout.addLayout(imgShowLayout)
    imgLayout.addWidget(btnShowDepthMap)
    imgLayout.addLayout(depthMapLayout)
    MainWindow.setLayout(imgLayout)

    ### URL Tab
    urlMainLayout = QVBoxLayout()
    urlImgShowLayout = QHBoxLayout()
    imgUrlLayoutL = QVBoxLayout()
    lableUrlL = QLabel("URL image Left")
    textUrlL = QLineEdit()
    btnUrlL = QPushButton("Load Left Image")
    imgLft = None
    def URLLeft():
        try:
            imgLft=url_to_image((textUrlL.text())).copy()
            #plt.imshow(imgLft)
            image = Image.open(urllib.request.urlopen(textUrlL.text()))
            imgURLL.setPixmap(QPixmap(QImage(ImageQt(image)).copy()))
        except:
            imgURLL.setText("Ingrese un URL Valido")
    btnUrlL.clicked.connect(URLLeft)
    imgURLL = QLabel()
    #Left
    imgUrlLayoutL.addWidget(lableUrlL)
    imgUrlLayoutL.addWidget(textUrlL)
    imgUrlLayoutL.addWidget(btnUrlL)
    imgUrlLayoutL.addWidget(imgURLL)
    #Right
    imgUrlLayoutR = QVBoxLayout()
    lableUrlR = QLabel("URL image Right")
    textUrlR = QLineEdit()
    imgRgt = None
    def URLRight():
        try:
            imgRgt=url_to_image((textUrlR.text())).copy()
            image = Image.open(urllib.request.urlopen(textUrlR.text()))
            imgURLR.setPixmap(QPixmap(QImage(ImageQt(image))).copy())
        except:
            imgURLR.setText("Ingrese un URL Valido")
    btnUrlR = QPushButton("Load Right Image")
    btnUrlR.clicked.connect(URLRight)
    imgURLR = QLabel()

    imgUrlLayoutR.addWidget(lableUrlR)
    imgUrlLayoutR.addWidget(textUrlR)
    imgUrlLayoutR.addWidget(btnUrlR)
    imgUrlLayoutR.addWidget(imgURLR)

    urlImgShowLayout.addLayout(imgUrlLayoutL)
    urlImgShowLayout.addLayout(imgUrlLayoutR)

    #Disparity
    urlDisparityLayout = QHBoxLayout()
    #Adding the layouts
    urlMainLayout.addLayout(urlImgShowLayout)
    urlMainLayout.addLayout(urlDisparityLayout)
    urlWindow.setLayout(urlMainLayout)
    tabWindow.addTab(MainWindow, "File")
    tabWindow.addTab(urlWindow, "URL")
    tabWindow.addTab(cameraWindow, "Cam")
    tabWindow.show()
    app.exec_()

if __name__ == "__main__":
    main()