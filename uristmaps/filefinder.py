""" Provide easy access to the latest versions of requested
export-maps.
"""
import os, glob, re

from uristmaps.config import conf

region_dir = conf["Paths"]["region"]
region_name = conf["Paths"]["region_name"]


def biome_map(fail=True):
    """ Convenience method to load the biome map.
    """
    return load_map("bm", fail)


def hydro_map(fail=True):
    """ Convenience method to load the water map.
    """
    return load_map("hyd", fail)


def all_site_maps():
    return glob.glob(os.path.join(region_dir, region_name + "*site_map*.png"))


def all_site_maps_target():
    """ Determine the filenames for all detailed site maps
    as they would appear in the output directory.
    """
    output_dir = conf.get("Paths", "output")
    id_re = re.compile("(\d+).png")
    result = []
    for site_map in all_site_maps():
        filename = os.path.basename(site_map)
        site_id = id_re.findall(filename)[0]
        result.append(os.path.join(output_dir, "{}.png".format(site_id)))
        
    return result

def struct_map(fail=True):
    """ Convenience method to load the structures map.
    """
    return load_map("str", fail)


def world_history(fail=True):
    files = glob.glob(region_dir + "/" + region_name + "*-world_history.txt")

    if files:
        return files[0]

    raise IOError("Could not find world history file in {}!".format(region_dir))
    return None


def sites_and_pops(fail=True):
    """ Find the sites and populations file
    """
    files = glob.glob(os.path.join(region_dir, region_name + "*-world_sites_and_pops.txt"))
    if files:
        return files[0]
    raise IOError("Could not find sites and pops file in {}!".format(region_dir))
    return None


def legends_xml(fail=True):
    """ Find the legends.xml file.
    """
    files = glob.glob(region_dir + "/" + region_name + "*-legends.xml")

    if files:
        return files[0]

    raise IOError("Could not find legends xml export in {}!".format(region_dir))
    return None
    

def load_map(key, fail=True):
    """ Search for a map export in the region dir by its keyand return the
    file's path.

    Returns the path to the exported map or None when no export could be found.
    When fail is true, an exception will be thrown if the file could not be found.
    """
    files = glob.glob(region_dir + "/" + region_name + "*-{}.png".format(key))

    if not files:
        files = glob.glob(region_dir + "/" + region_name + "*-{}-*.png".format(key))

    if files:
        return files[0]

    if fail:
        raise IOError("Could not find map export '{}' in {}!".format(key, region_dir))

    return ""

