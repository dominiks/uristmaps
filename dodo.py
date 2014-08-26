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
        "file_dep": [] # TODO: Find the biomes file
        }

def task_load_legends():
    """ Read the legends.xml and export the sites.json from that.
    """

    return {
        "actions": [["python", "uristmaps/load_legends.py"]],
        "verbosity": 2,
        "targets": ["{}/sites.json".format(build_dir)],
        "file_dep": ["{}/region5-legends.xml".format(region_dir)] # TODO: nay
        }

def task_render_biome():

    for i in range(1,conf.getint("Map","max_zoom")):
        yield {
        "name": i,
        "verbosity": 2,
        "actions": [(render_biome_layer.render_layer, (i,))],
        "file_dep": ["{}/biomes.json".format(build_dir)],
        "targets": ["{}/tiles/{}".format(output_dir, i)],
        }

def task_dist_legends():
    return {
        "actions": [["cp",
                     "{}/sites.json".format(build_dir),
                     "{}/assets/sites.json".format(output_dir)
                   ]],
        "file_dep": ["{}/sites.json".format(build_dir)],
        # TODO: function to generate filenames for all tiles?
        #"targets": ["{}/assets/sites.json".format(output_dir)]
    }

def task_host():
    """ Start a web server hosting the contents of the output directory.
    """
    cmd = "cd {} && python -m http.server".format(output_dir)
    return {
        "actions": [LongRunning(cmd)]
    }
