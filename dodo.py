from doit.tools import LongRunning

from modules.config import conf


# TODO: Replace cmd calls with direct python calls for better platform independence

# Some convenient references to configuration entries
build_dir = conf["Paths"]["build"]
output_dir = conf["Paths"]["output"]

def task_read_biome_info():
    """read info"""

    return {
        "actions": [["python", "modules/load_biomes.py"]],
        "targets": ["{}/biomes.json".format(build_dir)],
        "verbosity": 2,
        "file_dep": [] # TODO: Find the biomes file
        }

def task_load_legends():

    return {
        "actions": [["python", "modules/load_legends.py"]],
        "verbosity": 2,
        "targets": ["{}/sites.json".format(build_dir)],
        }

def task_render_biomes():

    for i in range(conf.getint("Map","max_zoom")):
        cmd = "python modules/render_biome_layer.py {}".format(str(i))
        yield {
        "name": "zoom level {}".format(i),
        "actions": [LongRunning(cmd)],
        "file_dep": ["{}/biomes.json".format(build_dir)]
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
