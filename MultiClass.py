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

class patchSorter(QMainWindow):
    
    def __init__(self, view, mainimage, outname):
        super(patchSorter, self).__init__()
        self.initUI(view,mainimage,outname)

    def initUI(self, view, mainimage, outname):
        self.view = view
        self.mainimage = mainimage
        self.outname = outname

        self.gui = mmdGUI(self)
        self.gui.setup(self.view, self.mainimage, self.outname)
        self.setCentralWidget(self.gui)


        exitAction = QAction(QIcon('exit.png'), '&Exit', self)        
        exitAction.setShortcut('Ctrl+Q')
        exitAction.setStatusTip('Exit application')
        exitAction.triggered.connect(qApp.quit)

        setclassAction = QAction('Set Classes', self) 
        setclassAction.setShortcut('Ctrl+N') 
        setclassAction.setStatusTip('Set the name of the Class Buttons') 
        setclassAction.triggered.connect(self.setClasses) 

        menubar = self.menuBar()
        fileMenu = menubar.addMenu('&File')
        fileMenu.addAction(exitAction)
        editMenu = menubar.addMenu('&Edit')
        editMenu.addAction(setclassAction)


        self.setWindowTitle("Patch sorter")
        self.resize(1000,800)

        self.show()

    def setClasses(self):
        reply = QMessageBox.question(self, "QMessageBox.question()",
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
                self.labelPatchNum.setText(str(self.i+1)+"/"+str(self.viewlist.shape[0]))
                self.showPatchLoc(self.idxl[self.i])
            else:
                msgBox = QMessageBox()
                msgBox.setText("All patches have been classified. You're Done!")
                msgBox.exec_()
                sys.exit()
        return calluser

    @pyqtSlot()
    def keyPressEvent(self, event):
        if event.text() in ['i','n']:
            self.on_click(True)
        if event.text() in ['b','m']:
            self.on_click(False)

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
        rr1,cc1   = skimage.draw.line(m*view.shape[3],n*view.shape[4],m*view.shape[3],(n+1)*view.shape[4]-1)
        rr11,cc11 = skimage.draw.line(m*view.shape[3]+1,n*view.shape[4],m*view.shape[3]+1,(n+1)*view.shape[4]-1)
        rr12,cc12 = skimage.draw.line(m*view.shape[3]+2,n*view.shape[4],m*view.shape[3]+2,(n+1)*view.shape[4]-1)
        rr = np.concatenate((rr1,rr11,rr12)); cc = np.concatenate((cc1,cc11,cc12))
        skimage.draw.set_color(tmpwhole,(rr,cc),self.PatchCursorColor)

        rr2,cc2   = skimage.draw.line(m*view.shape[3],n*view.shape[4],(m+1)*view.shape[3]-1,n*view.shape[4])
        rr21,cc21 = skimage.draw.line(m*view.shape[3],n*view.shape[4]+1,(m+1)*view.shape[3]-1,n*view.shape[4]+1)
        rr22,cc22 = skimage.draw.line(m*view.shape[3],n*view.shape[4]+2,(m+1)*view.shape[3]-1,n*view.shape[4]+2)
        rr = np.concatenate((rr2,rr21,rr22)); cc = np.concatenate((cc2,cc21,cc22))
        skimage.draw.set_color(tmpwhole,(rr,cc),self.PatchCursorColor)

        rr3,cc3   = skimage.draw.line((m+1)*view.shape[3]-1,(n+1)*view.shape[4]-1,m*view.shape[3],(n+1)*view.shape[4]-1)
        rr31,cc31 = skimage.draw.line((m+1)*view.shape[3]-1,(n+1)*view.shape[4]-2,m*view.shape[3],(n+1)*view.shape[4]-2)
        rr32,cc32 = skimage.draw.line((m+1)*view.shape[3]-1,(n+1)*view.shape[4]-3,m*view.shape[3],(n+1)*view.shape[4]-3)
        rr = np.concatenate((rr3,rr31,rr32)); cc = np.concatenate((cc3,cc31,cc32))
        skimage.draw.set_color(tmpwhole,(rr,cc),self.PatchCursorColor)

        rr4,cc4   = skimage.draw.line((m+1)*view.shape[3]-1,(n+1)*view.shape[4]-1,(m+1)*view.shape[3]-1,n*view.shape[4])
        rr41,cc41 = skimage.draw.line((m+1)*view.shape[3]-2,(n+1)*view.shape[4]-1,(m+1)*view.shape[3]-2,n*view.shape[4])
        rr42,cc42 = skimage.draw.line((m+1)*view.shape[3]-3,(n+1)*view.shape[4]-1,(m+1)*view.shape[3]-3,n*view.shape[4])
        rr = np.concatenate((rr4,rr41,rr42)); cc = np.concatenate((cc4,cc41,cc42))
        skimage.draw.set_color(tmpwhole,(rr,cc),self.PatchCursorColor)

        pixmapWhole = QPixmap.fromImage(toQImage(tmpwhole))
        self.labelWhole.setPixmap(pixmapWhole.scaled(self.wholeImageW, self.wholeImageH, Qt.KeepAspectRatio,Qt.SmoothTransformation))

    def updateClasses(self):
        for button in self.buttonList:
            button.setParent(None)
        self.bottom_area.setParent(None)
                    
        self.buttonList = []
        for cname in self.classNames:
            this_button = QPushButton(cname, self)
            this_button.setFont(QFont("Arial",18, QFont.Bold))
            this_button.resize(300,100)
            this_button.clicked.connect(self.on_click(cname))
            self.buttonList.append(this_button)

        self.bottom_area = QHBoxLayout()
        self.bottom_area.addStretch(1)
        self.bottom_area.addWidget(self.labelPatch)
        for button in self.buttonList:
            self.bottom_area.addWidget(button)
        self.bottom_area.addStretch(1)
        if not isinstance(self.parent(), QMainWindow):
            self.bottom_area.addWidget(btnq)
        self.vbox.addLayout(self.bottom_area)

    

    def makeoutdirs(self):
        # Make the output directory
        self.outDirs = []
        for cname in self.classNames:
            self.outDirs.append(self.outname + "_" + "".join(x for x in cname if x.isalnum()))
            if not os.path.exists(self.outDirs[-1]):
                os.makedirs(self.outDirs[-1])
        print("Using output dirs:" + "\n".join(self.outDirs))
        self.outdirsExist = True

    def setup(self, view, wholeim, outname='patches_Output'):
        self.view = view
        self.wholeim = wholeim
        self.viewlist = view.reshape(view.shape[0]*view.shape[1]*view.shape[2],view.shape[3],view.shape[4],view.shape[5])
        self.outname = outname

        self.idxl = np.random.permutation(range(0,self.viewlist.shape[0]))
        self.w = self
        self.w.setWindowTitle("Patch sorter")
        self.resizeEvent = self.onResize
        self.resize(1170,1000)

        # Widget for showing the whole image, with location box
        self.labelWhole = QLabel(self)

        # Widget for showing the current patch
        self.labelPatch = QLabel(self.w)

        # Create the label for showing the current patch number
        self.labelPatchNum = QLabel(self)
        self.labelPatchNum.resize(110,20)
        self.labelPatchNum.setAlignment(Qt.AlignRight)
        self.labelPatchNum.setText("1/"+str(self.viewlist.shape[0]))
        self.labelPatchNum.setFont(QFont("Arial",14, QFont.Bold))

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
    dim1 = 32 # default patch size is a 32x32 square
    dim2 = 32

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

    print("Using patches of height="+str(dim1)+" and width="+str(dim2)+".")
    if not outputdir:
        outputdir = os.path.splitext(os.path.abspath(inputfile))[0]

    im = mpimg.imread(inputfile)
    
    block_shape = (dim1, dim2, im.shape[2]) #height, width
    margin=np.mod(im.shape,block_shape)
    im_crop = im[:(im.shape-margin)[0],:(im.shape-margin)[1],:(im.shape-margin)[2]]
    
    view = view_as_blocks(im_crop, block_shape)

    
    # Setup and run the Qt GUI application
    app = QApplication([])
    gui = patchSorter(view, im_crop, outname=outputdir)
    sys.exit(app.exec_())
    


