#!/usr/bin/env python

import sys, getopt, os
from math import sqrt

from PyQt4 import QtGui, QtCore
from PyQt4.QtGui import *
from PyQt4.QtCore import Qt, pyqtSlot, QMetaObject

import numpy as np
from matplotlib import image as mpimg
from scipy import ndimage
from scipy.misc import imsave

import skimage.color
import skimage.filters
import skimage.morphology
import skimage.feature
import skimage.draw
from skimage.util.shape import view_as_blocks


def toQImage(im):
    result = QImage(im.ctypes.data, im.shape[1], im.shape[0], QImage.Format_RGB888)
    return result


class ListEdit(QDialog):
    def setupUi(self, TestLayout):
        TestLayout.setObjectName("ListEdit")
        TestLayout.resize(440,240)
        self.centralwidget = QtGui.QWidget(TestLayout)
        self.centralwidget.setObjectName("centralwidget")
        self.horizontalLayout = QtGui.QHBoxLayout(self.centralwidget)
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.verticalLayout = QtGui.QVBoxLayout()
        self.verticalLayout.setObjectName("verticalLayout")
        self.editBox = QtGui.QLineEdit(self.centralwidget)
        self.editBox.setObjectName("editBox")
        self.verticalLayout.addWidget(self.editBox)
        self.listBox = QtGui.QListWidget(self.centralwidget)
        self.listBox.setObjectName("listBox")
        self.verticalLayout.addWidget(self.listBox)
        self.horizontalLayout.addLayout(self.verticalLayout)
        self.verticalLayout_2 = QtGui.QVBoxLayout()
        self.verticalLayout_2.setObjectName("verticalLayout_2")
        self.addButton = QtGui.QPushButton(self.centralwidget)
        self.addButton.setObjectName("addButton")
        self.addButton.setText("Add")
        self.verticalLayout_2.addWidget(self.addButton)
        self.removeButton = QtGui.QPushButton(self.centralwidget)
        self.removeButton.setObjectName("removeButton")
        self.removeButton.setText("Remove")
        self.verticalLayout_2.addWidget(self.removeButton)
        self.clearButton = QtGui.QPushButton(self.centralwidget)
        self.clearButton.setObjectName("clearButton")
        self.clearButton.setText("Clear")
        

        self.loadButton = QtGui.QPushButton(self.centralwidget)
        self.loadButton.setObjectName("clearButton")
        self.loadButton.setText("Load File")
        self.verticalLayout_2.addWidget(self.loadButton)

        self.verticalLayout_2.addWidget(self.clearButton)
        spacerItem = QtGui.QSpacerItem(20,40,QtGui.QSizePolicy.Minimum,QtGui.QSizePolicy.Expanding)
        self.verticalLayout_2.addItem(spacerItem)
        self.horizontalLayout_2 = QtGui.QHBoxLayout()
        self.okButton = QtGui.QPushButton(self.centralwidget)
        self.okButton.setText("OK")
        self.cancelButton = QtGui.QPushButton(self.centralwidget)
        self.cancelButton.setText("Cancel")
        self.horizontalLayout_2.addWidget(self.okButton)
        self.horizontalLayout_2.addWidget(self.cancelButton)
        self.verticalLayout_2.addLayout(self.horizontalLayout_2)
        self.horizontalLayout.addLayout(self.verticalLayout_2)
        QMetaObject.connectSlotsByName(TestLayout)

        # connect buttons
        self.connect(self.addButton, QtCore.SIGNAL("clicked()"), self.addToList)
        self.connect(self.removeButton, QtCore.SIGNAL("clicked()"), self.removeFromList)
        self.connect(self.clearButton, QtCore.SIGNAL("clicked()"), self.clearList)
        self.connect(self.loadButton, QtCore.SIGNAL("clicked()"), self.loadListFile)
        self.connect(self.okButton, QtCore.SIGNAL("clicked()"), self.ListUpdate)
        self.connect(self.cancelButton, QtCore.SIGNAL("clicked()"), self.cancelListUpdate)

    def addToList(self):
        self.listBox.addItem(self.editBox.text())
        self.editBox.clear()

    def removeFromList(self):
        for item in self.listBox.selectedItems():
            self.listBox.takeItem(self.listBox.row(item))

    def clearList(self):
        self.listBox.clear()

    def ListUpdate(self):
        self.accept()

    def cancelListUpdate(self):
        self.close()
        
    def getList(self):
        return [str(i.text()) for i in self.listBox.findItems("", QtCore.Qt.MatchContains)]

    def setList(self, listEntries):
        for i in listEntries:
            self.listBox.addItem(i) 

    def loadListFile(self):
        classfile = QFileDialog.getOpenFileName(self, 'Open file', os.path.curdir)
        if classfile:
            self.clearList()
            with open(classfile) as f:
                lines = f.read().splitlines()
            self.setList(lines)



class patchSorter(QMainWindow):
    
    def __init__(self, inputfile, dims, outname):
        super(patchSorter, self).__init__()
        self.inputfile = inputfile
        self.setupPatches(dims)
        self.initUI(self.view,self.im,outname)

    def setupPatches(self, dims):
        self.dims = dims
        self.im = mpimg.imread(self.inputfile)
        self.block_shape = (self.dims[0], self.dims[1], self.im.shape[2]) #height, width
        margin=np.mod(self.im.shape,self.block_shape)
        self.im_crop = self.im[:(self.im.shape-margin)[0],:(self.im.shape-margin)[1],:(self.im.shape-margin)[2]]
        self.view = view_as_blocks(self.im_crop, self.block_shape)


    def initUI(self, view, mainimage, outname):
        self.view = view
        self.mainimage = mainimage
        self.outname = outname

        self.gui = mmdGUI(self)
        self.gui.setupImages(self.view, self.mainimage, self.outname)
        self.gui.setupInterface()
        self.setCentralWidget(self.gui)


        openAction = QAction('Open', self)
        openAction.setShortcut('Ctrl+O')
        openAction.setStatusTip('Open an image file')
        openAction.triggered.connect(self.fileOpen)

        exitAction = QAction(QIcon('exit.png'), '&Exit', self)        
        exitAction.setShortcut('Ctrl+Q')
        exitAction.setStatusTip('Exit application')
        exitAction.triggered.connect(qApp.quit)

        setclassAction = QAction('Set Classes', self) 
        setclassAction.setShortcut('Ctrl+C') 
        setclassAction.setStatusTip('Set the name of the Class Buttons') 
        setclassAction.triggered.connect(self.setClasses) 

        setpatchsizeAction = QAction('Set Patch Size', self) 
        setpatchsizeAction.setShortcut('Ctrl+P') 
        setpatchsizeAction.setStatusTip('Set the edge size of the square patches') 
        setpatchsizeAction.triggered.connect(self.setPatchSize) 

        randomizeAction = QAction('Randomize Order', self)
        randomizeAction.triggered.connect(self.gui.randomize)
        unrandomizeAction = QAction('Unrandomize Order', self)
        unrandomizeAction.triggered.connect(self.gui.unrandomize)

        menubar = self.menuBar()
        fileMenu = menubar.addMenu('&File')
        fileMenu.addAction(openAction)
        fileMenu.addAction(exitAction)
        editMenu = menubar.addMenu('&Edit')
        editMenu.addAction(setclassAction)
        editMenu.addAction(setpatchsizeAction)
        optionMenu = menubar.addMenu('&Options')
        optionMenu.addAction(randomizeAction)
        optionMenu.addAction(unrandomizeAction)
        

        self.setWindowTitle("Patch sorter")
        self.resize(1000,800)

        self.show()


    def fileOpen(self):
        reply = QMessageBox.question(self, "Open a new main image file?",
                                           "This will restart labeling. Continue?",
                                           QMessageBox.Yes | QMessageBox.No )
        if reply == QMessageBox.Yes:
            newImageFile = QFileDialog.getOpenFileName(self, 'Open file', os.path.curdir)
            if newImageFile:
                self.inputfile = str(newImageFile)
                self.setupPatches(self.dims)
                self.gui.setupImages(self.view, self.im, self.outname)
                self.gui.labelPatchNum.setText("("+str(self.gui.i+1)+"/"+str(self.gui.viewlist.shape[0])+")")
                self.gui.patchsizeStatus.setText("Patch size: "+str(self.view.shape[3])+"x"+str(self.view.shape[4]))
                self.gui.outname = os.path.splitext(os.path.abspath(self.inputfile))[0]
                self.gui.updateClasses()
                self.gui.i = 0
                self.gui.thispatch = np.copy(self.gui.viewlist[self.gui.idxl[self.gui.i],:,:,:])
                pixmap = QPixmap.fromImage(toQImage(self.gui.thispatch))
                self.gui.labelPatch.setPixmap(pixmap.scaled(100, 100, Qt.KeepAspectRatio,Qt.SmoothTransformation))
                self.gui.labelPatchNum.setText("("+str(self.gui.i+1)+"/"+str(self.gui.viewlist.shape[0])+")")
                self.gui.showPatchLoc(self.gui.idxl[self.gui.i])

    def setClasses(self):
        reply = QMessageBox.question(self, "Set the class names?",
                                           "This will set new classes and restart labeling, with output into new folders. Continue?",
                                           QMessageBox.Yes | QMessageBox.No )
        if reply == QMessageBox.Yes:
            l = ListEdit()
            l.setupUi(l)
            l.setList(self.gui.classNames)
            if(l.exec_()):
                self.gui.classNames = l.getList()
                self.gui.updateClasses()
            else:
                return 0
                
    def setPatchSize(self):
        reply = QMessageBox.question(self, "Set the patch size?",
                                           "This will set new edge lengths for the patched and restart labeling, with output into new folders. Continue?",
                                           QMessageBox.Yes | QMessageBox.No )
        if reply == QMessageBox.Yes:
            text, ok = QInputDialog.getText(self, 'Patch Edge Length', 
                                            'Enter the Patch Edge Length in Pixels (it will be rounded to nearest multiple of 8):')
            if ok:
                if str(text).isdigit():
                    newPatchSize = int(str(text))
                    newPatchSize = int(np.ceil(newPatchSize/8.0) * 8) # must be multiple of 8
                    dims = [newPatchSize, newPatchSize]
                    self.setupPatches(dims)
                    self.gui.setupImages(self.view, self.im, self.outname)
                    self.gui.i = 0
                    self.gui.showPatchLoc(self.gui.idxl[self.gui.i])
                    self.gui.labelPatchNum.setText("("+str(self.gui.i+1)+"/"+str(self.gui.viewlist.shape[0])+")")
                    self.gui.patchsizeStatus.setText("Patch size: "+str(self.view.shape[3])+"x"+str(self.view.shape[4]))

                else:
                    reply = QMessageBox.warning(self,"Invalid patch edge length","Value must be an integer.")


class mmdGUI(QFrame):
    ### 
    # Create GUI (requires Qt4)
    ###
    def __init__(self, parent):
        super(mmdGUI,self).__init__(parent)
        self.PatchCursorColor = np.array([0,255,0])
        self.wholeImageW = 600
        self.wholeImageH = 600
        self.outdirsExist = False
        self.classNames = ("Interesting", "Boring", "Useless")

    # Create the button click actions 
    @pyqtSlot()
    def on_click(self, classname):
        def calluser():
            if not self.outdirsExist:
                self.makeoutdirs()
            f_out = os.path.join(self.outDirs[self.classNames.index(classname)], "patch_"+str(self.i)+".png")
            imsave(f_out, self.thispatch)
            self.i = self.i+1
            if self.i <= self.idxl.shape[0]-1:
                self.thispatch = np.copy(self.viewlist[self.idxl[self.i],:,:,:])
                pixmap = QPixmap.fromImage(toQImage(self.thispatch))
                self.labelPatch.setPixmap(pixmap.scaled(100, 100, Qt.KeepAspectRatio,Qt.SmoothTransformation))
                self.labelPatchNum.setText("("+str(self.i+1)+"/"+str(self.viewlist.shape[0])+")")
                self.lastpickPatch.setText("Last: " + classname)
                self.showPatchLoc(self.idxl[self.i])
            else:
                msgBox = QMessageBox()
                msgBox.setText("All patches have been classified. You're Done!")
                msgBox.exec_()
                sys.exit()
        return calluser

    @pyqtSlot()
    def keyPressEvent(self, event):
        if str(event.text()).isdigit():
            ind = int(str(event.text())) - 1
            if ind < len(self.classNames):
                self.on_click(self.classNames[ind])()

    def onResize(self, event):
        winWidth = event.size().width()
        winHeight = event.size().height()
        self.wholeImageW = int(0.8*winWidth)
        self.wholeImageH = int(0.8*winHeight)
        self.showPatchLoc(self.idxl[self.i])

    def showPatchLoc(self,patchNum):
        tmpwhole = np.copy(self.wholeim)
        m,n = np.unravel_index(patchNum,(self.view.shape[0],self.view.shape[1]))
        
        # Coordinates for rectangle
        rr1,cc1   = skimage.draw.line(m*self.view.shape[3],n*self.view.shape[4],m*self.view.shape[3],(n+1)*self.view.shape[4]-1)
        rr11,cc11 = skimage.draw.line(m*self.view.shape[3]+1,n*self.view.shape[4],m*self.view.shape[3]+1,(n+1)*self.view.shape[4]-1)
        rr12,cc12 = skimage.draw.line(m*self.view.shape[3]+2,n*self.view.shape[4],m*self.view.shape[3]+2,(n+1)*self.view.shape[4]-1)
        rr = np.concatenate((rr1,rr11,rr12)); cc = np.concatenate((cc1,cc11,cc12))
        skimage.draw.set_color(tmpwhole,(rr,cc),self.PatchCursorColor)

        rr2,cc2   = skimage.draw.line(m*self.view.shape[3],n*self.view.shape[4],(m+1)*self.view.shape[3]-1,n*self.view.shape[4])
        rr21,cc21 = skimage.draw.line(m*self.view.shape[3],n*self.view.shape[4]+1,(m+1)*self.view.shape[3]-1,n*self.view.shape[4]+1)
        rr22,cc22 = skimage.draw.line(m*self.view.shape[3],n*self.view.shape[4]+2,(m+1)*self.view.shape[3]-1,n*self.view.shape[4]+2)
        rr = np.concatenate((rr2,rr21,rr22)); cc = np.concatenate((cc2,cc21,cc22))
        skimage.draw.set_color(tmpwhole,(rr,cc),self.PatchCursorColor)

        rr3,cc3   = skimage.draw.line((m+1)*self.view.shape[3]-1,(n+1)*self.view.shape[4]-1,m*self.view.shape[3],(n+1)*self.view.shape[4]-1)
        rr31,cc31 = skimage.draw.line((m+1)*self.view.shape[3]-1,(n+1)*self.view.shape[4]-2,m*self.view.shape[3],(n+1)*self.view.shape[4]-2)
        rr32,cc32 = skimage.draw.line((m+1)*self.view.shape[3]-1,(n+1)*self.view.shape[4]-3,m*self.view.shape[3],(n+1)*self.view.shape[4]-3)
        rr = np.concatenate((rr3,rr31,rr32)); cc = np.concatenate((cc3,cc31,cc32))
        skimage.draw.set_color(tmpwhole,(rr,cc),self.PatchCursorColor)

        rr4,cc4   = skimage.draw.line((m+1)*self.view.shape[3]-1,(n+1)*self.view.shape[4]-1,(m+1)*self.view.shape[3]-1,n*self.view.shape[4])
        rr41,cc41 = skimage.draw.line((m+1)*self.view.shape[3]-2,(n+1)*self.view.shape[4]-1,(m+1)*self.view.shape[3]-2,n*self.view.shape[4])
        rr42,cc42 = skimage.draw.line((m+1)*self.view.shape[3]-3,(n+1)*self.view.shape[4]-1,(m+1)*self.view.shape[3]-3,n*self.view.shape[4])
        rr = np.concatenate((rr4,rr41,rr42)); cc = np.concatenate((cc4,cc41,cc42))
        skimage.draw.set_color(tmpwhole,(rr,cc),self.PatchCursorColor)

        pixmapWhole = QPixmap.fromImage(toQImage(tmpwhole))
        self.labelWhole.setPixmap(pixmapWhole.scaled(self.wholeImageW, self.wholeImageH, Qt.KeepAspectRatio,Qt.SmoothTransformation))

    def updateClasses(self):
        for button in self.buttonList:
            button.setParent(None)
        self.bottom_area.setParent(None)
                    
        self.buttonList = []
        buttoni = 1
        for cname in self.classNames:
            this_button = QPushButton(cname+" ("+str(buttoni)+")", self)
            this_button.setFont(QFont("Arial",18, QFont.Bold))
            this_button.resize(300,100)
            this_button.clicked.connect(self.on_click(cname))
            self.buttonList.append(this_button)
            buttoni = buttoni+1

        self.bottom_area = QHBoxLayout()
        self.bottom_area.addStretch(1)
        self.bottom_area.addWidget(self.labelPatch)
        for button in self.buttonList:
            self.bottom_area.addWidget(button)
        self.bottom_area.addStretch(1)
        if not isinstance(self.parent(), QMainWindow):
            self.bottom_area.addWidget(btnq)
        self.vbox.addLayout(self.bottom_area)
        self.i = 0
   
        self.outdirsExist = False

    def makeoutdirs(self):
        # Make the output directory
        self.outDirs = []
        for cname in self.classNames:
            self.outDirs.append(self.outname + "_" + "".join(x for x in cname if x.isalnum()))
            if not os.path.exists(self.outDirs[-1]):
                os.makedirs(self.outDirs[-1])
        print("Using output dirs:\n" + "\n".join(self.outDirs))
        self.outdirsExist = True

    def setupImages(self, view, wholeim, outname='patches_Output'):
        self.view = view
        self.wholeim = wholeim
        self.viewlist = view.reshape(view.shape[0]*view.shape[1]*view.shape[2],view.shape[3],view.shape[4],view.shape[5])
        self.outname = outname
        self.idxl = np.random.permutation(range(0,self.viewlist.shape[0]))

    def unrandomize(self):
        self.idxl = np.concatenate([self.idxl[0:self.i],np.sort(self.idxl[self.i:])])
    
    def randomize(self):
        self.idxl = np.concatenate([self.idxl[0:self.i],np.random.permutation(self.idxl[self.i:])])

    def setupInterface(self):
        self.w = self
        self.w.setWindowTitle("Patch sorter")
        self.resizeEvent = self.onResize
        self.resize(1170,1000)

        # Widget for showing the whole image, with location box
        self.labelWhole = QLabel(self)

        # Widget for showing the current patch
        self.labelPatch = QLabel(self.w)
        self.labelPatch.setFrameStyle(QFrame.Panel)

        # Create the label for showing the current patch number
        self.labelPatchNum = QLabel(self)
        self.labelPatchNum.resize(110,20)
        self.labelPatchNum.setAlignment(Qt.AlignRight)
        self.labelPatchNum.setText("(1/"+str(self.viewlist.shape[0])+")")
        self.labelPatchNum.setFont(QFont("Arial",14, QFont.Bold))

        self.lastpickPatch = QLabel(self)
        self.lastpickPatch.resize(110,20)
        self.lastpickPatch.setAlignment(Qt.AlignRight)
        self.lastpickPatch.setText("Last: ")
        self.lastpickPatch.setFont(QFont("Arial",14, QFont.Bold))

        self.patchsizeStatus = QLabel(self)
        self.patchsizeStatus.resize(110,20)
        self.patchsizeStatus.setAlignment(Qt.AlignRight)
        self.patchsizeStatus.setText("Patch size: "+str(self.view.shape[3])+"x"+str(self.view.shape[4]))
        self.patchsizeStatus.setFont(QFont("Arial",14, QFont.Bold))



        # Display area for the current whole image
        self.i = 0
        self.thispatch = self.viewlist[self.idxl[self.i],:,:,:]
        pixmap = QPixmap.fromImage(toQImage(self.thispatch))
        self.labelPatch.setPixmap(pixmap.scaled(100, 100, Qt.KeepAspectRatio,Qt.SmoothTransformation))
        self.showPatchLoc(self.idxl[self.i])

        # Add buttons
        if not isinstance(self.parent(), QMainWindow):
            btnq = QPushButton('Quit', self)
            btnq.setToolTip('Click to quit!')
            btnq.clicked.connect(exit)
            btnq.resize(btnq.sizeHint())

        self.buttonList = []
        for cname in self.classNames:
            this_button = QPushButton(cname, self)
            this_button.setFont(QFont("Arial",18, QFont.Bold))
            this_button.resize(300,100)
            this_button.clicked.connect(self.on_click(cname))
            self.buttonList.append(this_button)

        # Set up the layout of the GUI
        top_area = QHBoxLayout()
        top_area.addStretch(1)
        top_area.addWidget(self.labelWhole)
        top_area.addStretch(1)
        middle_area = QHBoxLayout()
        middle_area.addStretch(1)
        if isinstance(self.parent(), QMainWindow):
            self.parent().statusBar().insertWidget(0,self.labelPatchNum)
            self.parent().statusBar().insertWidget(0,self.patchsizeStatus)
            self.parent().statusBar().insertPermanentWidget(1,self.lastpickPatch, stretch=200)
        else:
            middle_area.addWidget(self.labelPatchNum)
        self.bottom_area = QHBoxLayout()
        self.bottom_area.addStretch(1)
        self.bottom_area.addWidget(self.labelPatch)
        for button in self.buttonList:
            self.bottom_area.addWidget(button)
        self.bottom_area.addStretch(1)
        if not isinstance(self.parent(), QMainWindow):
            self.bottom_area.addWidget(btnq)
        self.vbox = QVBoxLayout()
        self.vbox.addLayout(top_area)
        self.vbox.addLayout(middle_area)
        self.vbox.addLayout(self.bottom_area)
        self.setLayout(self.vbox)


# ----------------------------------------------------------------------------------------------------
# Main method
if __name__ == "__main__":
    inputfile = "data/example.jpg" #default
    outputdir = None
    classfile = None
    dim1 = 256 # default patch size is a 256x256 square
    dim2 = 256

    try:
        opts, args = getopt.getopt(sys.argv[1:],"hi:o:c:s:",["inputfile=","outputdir=","classfile=","size="])
    except getopt.GetoptError:
        print 'python SortPatches.py -i <inputfile> -o <outputdir> -c <classfile> -s <patchheight>,<patchwidth>'
        sys.exit(2)
    for opt, arg in opts:
        if opt in ("-i", "--inputfile"):
            inputfile = arg
        if opt in ("-o", "--outputdir"):
            outputdir = arg
        if opt in ("-c", "--classfile"):
            classfile = arg
        if opt in ("-s", "--size"): 
            serr = False
            aarg = arg.split(',')
            if len(aarg) == 2:
                dim1 = float(aarg[0])
                dim2 = float(aarg[1])
                if(dim1 > 0):
                    dim1 = int(np.ceil(dim1/8.0) * 8)
                else:
                    serr = True
                if(dim2 > 0):
                    dim2 = int(np.ceil(dim2/8.0) * 8)
                else:
                    serr = True
            else:
                serr = True
            if serr:
                print("Size argument (-s or --size) should be of the form m,n. Sizes must be >0 and are rounded to the nearest byte (multiple of 8).")
                sys.exit(2)

    if not outputdir:
        outputdir = os.path.splitext(os.path.abspath(inputfile))[0]

    app = QApplication([])
    p = patchSorter(inputfile, [dim1, dim2], outname=outputdir)
    if classfile:
        with open(classfile) as f:
            lines = f.read().splitlines()
        p.gui.classNames = lines
        p.gui.updateClasses()
    sys.exit(app.exec_())
    



