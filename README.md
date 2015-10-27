# patchSorter
Python GUI utility for sorting image patches

Created August, 2015 by Marcello DiStasio

Randomly presents user with subregions of an image ("patches") and lets user select between two categories for each patch, saving the patches as individual \*.png files in two output directories.

##Screenshot##
<img src="doc/img/screenshot_1.png">

Pretty straigforward.  The whole image is displayed, and a box cursor shows you the current patch to be sorted. The patch is represented in a scaled mini-display at the bottom. Clicking either of the large buttons sends a saved \*.png image to one of the output directories, and advances to the next randomly selected patch.  You can also use the the following hotkeys to sort: **i** or **n** for the left button and **b** or **m** for the right button. The counter at the bottom right shows which patch is currently active.

##Usage##

Tested with Python 2.7. Basic invocation with default options is:
```
python SortPatches.py -i <inputfile.jpg>
```

This loads the input file and starts the program.  When you click either button to classify the first patch displayed, the two default output directories are created in the same directory of the input file (defult named `<inputfile>_interesting` and `<inputfile>_boring`). If you rename the two classes (Using the option under the "Edit" menu), the buttons text will change to your class names ("Epithelium" and "Stroma"), and output directories will be created that reflect your class names.  The class names can be changed at any time, and all subsquently classified patches will be sorted into filders that reflect the new class names.

The full options are:
```
python SortPatches.py -i <inputfile> -o <outputdir> -s <patchheight>,<patchwidth>
```

This lets you specify the output directory basenames. `<basename>_[CLASS_1_NAME]` and `<basename>_[CLASS_2_NAME]` will be created in the same directory as the input image), and set a custom patch size (the default is 32x32).  The patch dimensions must be multiples of 8, and will be rounded up to the nearest multiple of 8 otherwise.

