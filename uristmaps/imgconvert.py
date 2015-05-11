import os, glob, re
from PIL import Image
from clint.textui import progress

from uristmaps.config import conf

region_dir = conf["Paths"]["region"]
region_name = conf["Paths"]["region_name"]

def convert_bitmaps():
    """ Convert all bitmaps to png files, delete the bitmaps.
    """
    bitmaps = glob.glob(os.path.join(region_dir, region_name + "*.bmp"))

    if not bitmaps:
        # Nothing to do, quit before the useless progress bar prints
        return
 
    for bmp_file in progress.bar(bitmaps):
        # convert file
        newname = bmp_file[:-3] + "png"
        Image.open(bmp_file).save(newname, "PNG")
        os.remove(bmp_file)
