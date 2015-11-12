# patchSorter
Python GUI utility for sorting image patches

Created August, 2015 by Marcello DiStasio

Randomly presents user with subregions of an image ("patches") and lets user select between two categories for each patch, saving the patches as individual \*.png files in two output directories.

##Screenshot##
<img src="doc/img/screenshot_1.png">

Pretty straigforward.  The whole image is displayed, and a box cursor shows you the current patch to be sorted. The patch is represented in a scaled mini-display at the bottom. Clicking either of the large buttons sends a saved \*.png image to one of the output directories, and advances to the next randomly selected patch.  You can also use the numbers displayed on the buttons as hotkeys. The counter at the bottom left shows which patch is currently active. The status message at the right shows the most recent selection.

##Usage##

Tested with Python 2.7. Basic invocation with default options is:
```
python SortPatches.py -i <inputfile.jpg>
```

This loads the input file and starts the program.  When you click any button to classify the first patch displayed, the output directories are created in the same directory of the input file (named `<inputfile>_Class1`, `<inputfile>_Class2`, ..., etc.). If you rename the classes (Using the option under the "Edit" menu), the buttons text will change to your new class names, and output directories will be created that reflect your class names.  The class names can be changed at any time, and all subsquently classified patches will be sorted into filders that reflect the new class names.

The full options are:
```
python SortPatches.py -i <inputfile> -o <outputdir> -s <patchheight>,<patchwidth> -c <class name listing file>
```

This lets you specify the output directory basenames. `<basename>_[CLASS_1_NAME]` and `<basename>_[CLASS_2_NAME]` will be created in the output dir. You can also set a custom patch size (the default is 32x32) with the `-s` option.  The patch dimensions must be multiples of 8, and will be rounded up to the nearest multiple of 8 otherwise.

The classnames can be specified in a text file, with one class name per line (as in `exampleClasses.txt`).  Each name will get its own button, and its own output directory. You can load a file from the command line or within the `Set Class Names` dialog.

Input image files can be passed via the command line, or from the `File|Open` menu option.
