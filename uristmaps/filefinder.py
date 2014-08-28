""" Provide easy access to the latest versions of requested
export-maps.
"""
import os, glob

from uristmaps.config import conf

region_dir = conf["Paths"]["region"]

def biome_map():
    """ Convenience method to load the biome map.
    """
    return load_map("bm")

def legends_xml():
    """ Find the legends.xml file.
    """
    files = glob.glob(region_dir + "/*-legends.xml")

    if files:
        return files[0]

    raise IOError("Could not find biome export in {}!".format(region_dir))
    return None
    

def load_map(key):
    """ Search for a map export in the region dir by its keyand return the
    file's path.

    Supports old and new style named export.

    Returns the path to the exported map or None when no export could be found.
    """
    files = glob.glob(region_dir + "/*-{}.bmp".format(key))

    if not files:
        files = glob.glob(region_dir + "/*-{}-*.bmp".format(key))

    if files:
        return files[0]

    raise IOError("Could not find map export '{}' in {}!".format(key, region_dir))
    return None

