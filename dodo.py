import itertools, shutil, os, glob

from os.path import join as pjoin

from doit.tools import LongRunning

from uristmaps import render_sat_layer, load_legends, load_biomes, filefinder, tilesets, \
                      load_structures, index, uristcopy
from uristmaps.config import conf


# TODO: Replace cmd calls with direct python calls for better platform independence

# Some convenient references to configuration entries
build_dir = conf["Paths"]["build"]
output_dir = conf["Paths"]["output"]
region_dir = conf["Paths"]["region"]
tiles_dir = conf["Paths"]["tiles"]
tilesets_dir = conf["Paths"]["tilesets"]

DOIT_CONFIG = {"default_tasks": ["dist_sites", "render_sat", "dist_index", "biome_legend", "copy_res"]}

def task_read_biome_info():
    """ Read biome info and write the biomes.json.
    """

    return {
        "actions"   : [load_biomes.load],
        "targets"   : [pjoin(build_dir, "biomes.json")],
        "verbosity" : 2,
        "file_dep"  : [filefinder.biome_map()]
        }

def task_load_sites():
    """ Read the legends.xml and export the sites.json from that.
    """

    return {
        "actions"   : [load_legends.load_sites, load_legends.create_geojson],
        "verbosity" : 2,
        "targets"   : [pjoin(build_dir, "sites.json"),pjoin(build_dir, "sitesgeo.json")],
        "file_dep"  : [filefinder.legends_xml(),
                       pjoin(build_dir, "biomes.json")]
        }


def task_create_index():
    """ Crate the index.html from the template and copy to build dir.
    """

    return {
        "actions"   : [index.create],
        "verbosity" : 2,
        "targets"   : [pjoin(build_dir, "index.html")],
        "file_dep"  : [] # Dunno yet
    }


def task_dist_index():
    """ Copy the index.html from the build to output dir.
    """

    return {
        "actions" : [(uristcopy.copy, (pjoin(build_dir, "index.html"),
                             pjoin(output_dir, "index.html")))],
        "verbosity" : 2,
        "targets" : [pjoin(output_dir, "index.html")],
        "file_dep" : [pjoin(build_dir, "index.html")]
        }


def task_load_structures():
    """ Read the legends.xml and export the sites.json from that.
    """

    return {
        "actions"   : [load_structures.load],
        "verbosity" : 2,
        "targets"   : [pjoin(build_dir, "structs.json")],
        "file_dep"  : [filefinder.struct_map()]
        }


def task_render_sat():
    """ Render the map layers for the 'satellite'-like view of the world.
    """

    def list_tile_files(topdir, level):
       """ Generate a complete list of the files that make up
       the layer with the given zoom level in the topdir.
       """
       return [pjoin(topdir, str(level), str(x),"{}.png".format(y)) for \
               (x,y) in itertools.product(range(level + 1), repeat=2)]

    for i in range(1,conf.getint("Map","max_zoom") + 1):
        yield {
            "name"      : i,
            "verbosity" : 2,
            "actions"   : [(render_sat_layer.render_layer, (i,))],

            # TODO: Make this depend on the tilesheet for the imagesize that would be used
            #       for this zoom level.
            "file_dep"  : [pjoin(build_dir, "biomes.json"),
                           "{}/structs.json".format(build_dir)],
            "targets"   : list_tile_files(pjoin(output_dir, "tiles"),i),
        }


def task_dist_sites():
    """ Copy the legends json into the output directory.
    """

    return {
        "actions"  : [(uristcopy.copy, (pjoin(build_dir, "sites.json"),
                              pjoin(output_dir, "js", "sites.json"))
                     ),
                      (uristcopy.copy, (pjoin(build_dir, "sitesgeo.json"),
                              pjoin(output_dir, "js", "sitesgeo.json"))
                     )],
        "file_dep" : [pjoin(build_dir, "sites.json"),pjoin(build_dir, "sitesgeo.json")],
        "targets"  : [pjoin(output_dir, "js", "sites.json"),pjoin(output_dir, "js", "sitesgeo.json")]
    }


def task_host():
    """ Start a web server hosting the contents of the output directory.
    """
    cmd = "cd {} && python -m http.server".format(output_dir)
    return {
        "actions" : [LongRunning(cmd)]
    }


def task_copy_res():
    """ Copy static HTML resources into the output directory.
    """
    return {
        "actions"   : [(uristcopy.copy_dir_contents, ("res", output_dir))],
        "verbosity" : 2,
    }


def task_biome_legend():
    """ Copy 32px images for biome rendering into the output dir.
    """
    return {
        "actions"   : [(uristcopy.copy_dir, (pjoin(tiles_dir, "32"),
                                   pjoin(output_dir, "biome_legend")))],
        "verbosity" : 2,
    }


def task_create_tilesets():
    """ Paste the single tile images for each image size into tilesheet
    images that will be used in rendering.
    """
    for dirname in glob.glob("{}/*".format(tiles_dir)):
        name = os.path.basename(dirname)
        yield {
            "name"      : name,
            "actions"   : [(tilesets.make_tileset, (dirname,))],
            "verbosity" : 2,

            # Depends on all single images in tiles/<name>/
            "file_dep"  : glob.glob(pjoin(tiles_dir, name, "*.png")),

            # Creates <name>.png and <name>.json in tilesets/
            "targets"   : [pjoin(tilesets_dir, "{}.png".format(name)),
                           pjoin(tilesets_dir, "{}.json".format(name))]
            }
