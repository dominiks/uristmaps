""" Provide easy access to the latest versions of requested
export-maps.
"""
import os, glob

from uristmaps.config import conf

region_dir = conf["Paths"]["region"]

def biome_map():
    """ Search for a biome-map export in the region dir and return the
    file's path.

    Returns the path to the exported biome map or None when no export could be found.
    """
    files = glob.glob(region_dir + "/*-bm.bmp")
    if not files:
        files = glob.glob(region_dir + "/*-bm-*.bmp")

    if files:
        return files[0]

    return None

