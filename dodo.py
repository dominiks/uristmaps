import itertools

from doit.tools import LongRunning

from uristmaps import render_biome_layer
from uristmaps.config import conf


# TODO: Replace cmd calls with direct python calls for better platform independence

# Some convenient references to configuration entries
build_dir = conf["Paths"]["build"]
output_dir = conf["Paths"]["output"]
region_dir = conf["Paths"]["region"]

DOIT_CONFIG = {"default_tasks": ["render_biome"]}

def task_read_biome_info():
    """ Read biome info and write the biomes.json.
    """

    return {
        "actions": [["python", "uristmaps/load_biomes.py"]],
        "targets": ["{}/biomes.json".format(build_dir)],
        "verbosity": 2,
        "file_dep": ["{}/el.bmp".format(region_dir)] # TODO: Generalize
        }

def task_load_legends():
    """ Read the legends.xml and export the sites.json from that.
    """

    return {
        "actions": [["python", "uristmaps/load_legends.py"]],
        "verbosity": 2,
        "targets": ["{}/sites.json".format(build_dir)],
        "file_dep": ["{}/region5-legends.xml".format(region_dir)] # TODO: Generalize file name
        }

def task_render_biome():

    def list_tile_files(topdir, level):
       """ Generate a complete list of the files that make up
       the layer with the given zoom level in the topdir.
       """
       return ["{}/{}/{}/{}.png".format(topdir, level, x, y) for \
               (x,y) in itertools.product(range(level + 1), repeat=2)]

    for i in range(1,conf.getint("Map","max_zoom") + 1):
        yield {
            "name": i,
            "verbosity": 2,
            "actions": [(render_biome_layer.render_layer, (i,))],
            "file_dep": ["{}/biomes.json".format(build_dir)],
            "targets": list_tile_files("{}/tiles".format(output_dir),i),
        }

def task_dist_legends():
    return {
        "actions": [["cp",
                     "{}/sites.json".format(build_dir),
                     "{}/assets/sites.json".format(output_dir)
                   ]],
        "file_dep": ["{}/sites.json".format(build_dir)],
        "targets": ["{}/assets/sites.json".format(output_dir)]
    }

def task_host():
    """ Start a web server hosting the contents of the output directory.
    """
    cmd = "cd {} && python -m http.server".format(output_dir)
    return {
        "actions": [LongRunning(cmd)]
    }
