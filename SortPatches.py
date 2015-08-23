#!/usr/bin/env python

import sys, getopt, os
from math import sqrt

from PyQt4.QtGui import *
from PyQt4.QtCore import Qt, pyqtSlot

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


class patchSorter(QMainWindow):
    
    def __init__(self, view, mainimage, outname):
        super(patchSorter, self).__init__()
        self.initUI(view,mainimage,outname)

    def initUI(self, view, mainimage, outname):
        self.gui = mmdGUI(self)
        self.gui.setup(view, im_crop, outname)
        self.setCentralWidget(self.gui)

        self.setWindowTitle("Patch sorter")
        self.resize(1170,1000)

        self.show()

class mmdGUI(QFrame):
    ### 
    # Create GUI (requires Qt4)
    ###
    def __init__(self, parent):
        super(mmdGUI,self).__init__(parent)
        self.PatchCursorColor = np.array([0,255,0])
        
    
    # Create the button click actions 
    @pyqtSlot()
    def on_click(self, interesting):
        if interesting:
            f_out = os.path.join(self.outdir_inter, "patch_"+str(self.i)+".png")
            imsave(f_out, self.thispatch)
        else:
            f_out = os.path.join(self.outdir_borin, "patch_"+str(self.i)+".png")
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

    @pyqtSlot()
    def keyPressEvent(self, event):
        if event.text() in ['i','n']:
            self.on_click(True)
        if event.text() in ['b','m']:
            self.on_click(False)

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
        self.labelWhole.setPixmap(pixmapWhole.scaled(1200, 800, Qt.KeepAspectRatio,Qt.SmoothTransformation))
        


    def setup(self, view, wholeim, outname='patches_Output'):
        self.view = view
        self.wholeim = wholeim
        self.viewlist = view.reshape(view.shape[0]*view.shape[1]*view.shape[2],view.shape[3],view.shape[4],view.shape[5])
        self.outname = outname

        # Make the output directory
        self.outdir_inter = self.outname + "_interesting"
        self.outdir_borin = self.outname + "_boring"
        if not os.path.exists(self.outdir_inter):
            os.makedirs(self.outdir_inter)
        if not os.path.exists(self.outdir_borin):
            os.makedirs(self.outdir_borin)
        print("Using output dirs: \n" + self.outdir_inter + "\n" + self.outdir_borin)

        self.idxl = np.random.permutation(range(0,self.viewlist.shape[0]))
        self.w = self
        self.w.setWindowTitle("Patch sorter")
        self.resize(1170,1000)

        # Widget for showing the whole image, with location box
        self.labelWhole = QLabel(self)
        self.labelWhole.move(10,10)

        # Create the label for showing the current patch number
        self.labelPatchNum = QLabel(self)
        self.labelPatchNum.move(780,950)
        self.labelPatchNum.resize(110,20)
        self.labelPatchNum.setAlignment(Qt.AlignRight)
        self.labelPatchNum.setText("1/"+str(self.viewlist.shape[0]))
        self.labelPatchNum.setFont(QFont("Arial",14, QFont.Bold))

        # Add buttons
        btnq = QPushButton('Quit', self)
        btnq.setToolTip('Click to quit!')
        btnq.clicked.connect(exit)
        btnq.resize(btnq.sizeHint())
        btnq.move(900, 950)   

        btn = QPushButton('Interesting', self)
        btn.setFont(QFont("Arial",18, QFont.Bold))
        btn.resize(300,100)
        btn.move(100,850)
        btn.clicked.connect(lambda: self.on_click(1))
        
        btn = QPushButton('Boring', self)
        btn.setFont(QFont("Arial",18, QFont.Bold))
        btn.resize(300,100)
        btn.move(600,850)
        btn.clicked.connect(lambda: self.on_click(0))

        # This is the patch
        self.labelPatch = QLabel(self.w)
        self.labelPatch.move(450,850)
        
        # Display the current whole image
        self.i = 0
        self.thispatch = self.viewlist[self.idxl[self.i],:,:,:]
        pixmap = QPixmap.fromImage(toQImage(self.thispatch))
        self.labelPatch.setPixmap(pixmap.scaled(100, 100, Qt.KeepAspectRatio,Qt.SmoothTransformation))
        self.showPatchLoc(self.idxl[self.i])
        

# ----------------------------------------------------------------------------------------------------
# Main method
if __name__ == "__main__":
#    inputdir = 
    inputfile = "data/example.jpg" #default
    outputdir = None
    dim1 = 32 # default patch size is a 32x32 square
    dim2 = 32

    try:
        opts, args = getopt.getopt(sys.argv[1:],"hi:o:s:",["inputfile=","outputdir=","size="])
    except getopt.GetoptError:
        print 'python SortPatches.py -i <inputfile> -o <outputdir> -s <patchheight>,<patchwidth>'
        sys.exit(2)
    for opt, arg in opts:
        if opt in ("-i", "--inputfile"):
            inputfile = arg
        if opt in ("-o", "--outputdir"):
            outputdir = arg
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
    



