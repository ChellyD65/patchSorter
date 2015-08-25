# patchSorter
Python GUI utility for sorting image patches

Created August, 2015 by Marcello DiStasio

Randomly presents user with subregions of an image ("patches") and lets user select between two categories for each patch, saving the patches as individual \*.png files in two output directories.

##Screenshot##
<img src="doc/img/screenshot_1.png">

Pretty straigforward.  The whole image is displayed, and a box cursor shows you the current patch to be sorted. The patch is represented in a scaled mini-display at the bottom. Clicking either of the large buttons sends a saved \*.png image to one of the output directories, and advances to the next randomly selected patch.  You can also use the the following hotkeys to sort: **i** or **n** for "Interesting" and **b** or **m** for "Boring". The counter at the bottom right shows which patch is currently active.

##Usage##

Tested with Python 2.7. Basic invocation with default options is:
```
python SortPatches.py -i <inputfile.jpg>
```
This creates two directories in the same directory of ths input file named `<inputfile>_interesting` and `<inputfile>_boring`, and sort the patches into these.  The full options are:
```
python SortPatches.py -i <inputfile> -o <outputdir> -s <patchheight>,<patchwidth>
```

This lets you specify the output directory basenames (`<outputdir>_interesting` and `<outputdir>_boring` will be created in the same directory as the input image), and set a custom patch size (the default is 32x32).  The patch dimensions must be multiples of 8, and will be rounded up to the nearest multiple of 8 otherwise.

