import itertools, shutil, os, glob

from os.path import join as pjoin

from doit.tools import LongRunning

from uristmaps import render_sat_layer, load_legends, load_biomes, filefinder, tilesets, \
                      load_structures, templates, uristcopy, group_structures, \
                      load_pops, imgconvert
from uristmaps.config import conf


# Some convenient references to configuration entries
build_dir = conf["Paths"]["build"]
output_dir = conf["Paths"]["output"]
region_dir = conf["Paths"]["region"]
tiles_dir = conf["Paths"]["tiles"]
tilesets_dir = conf["Paths"]["tilesets"]

DOIT_CONFIG = {"default_tasks": ["create_tilesets", "load_populations", "dist_sites", "render_sat", "index", "js_file", "biome_legend", "copy_res"]}

def task_read_biome_info():
    """ Read biome info and write the biomes.json.
    """

    return {
        "actions"   : [load_biomes.load],
        "targets"   : [pjoin(build_dir, "biomes.json")],
        "verbosity" : 2,
        "file_dep"  : [filefinder.biome_map(fail=False)],
        "clean"     : True,
        }

def task_load_sites():
    """ Read the legends.xml and export the sites.json from that.
    """

    return {
        "actions"   : [load_legends.load_sites],
        "verbosity" : 2,
        "targets"   : [pjoin(build_dir, "sites.json")],
        "file_dep"  : [filefinder.legends_xml(fail=False),
                       pjoin(build_dir, "biomes.json")],
        "clean"     : True,
        }


def task_index():
    """ Crate the index.html from the template and copy to the output dir.
    """

    yield {
        "name"      : "compile",
        "actions"   : [templates.render_index],
        "verbosity" : 2,
        "targets"   : [pjoin(build_dir, "index.html")],
        "file_dep"  : [pjoin("templates", "index.html")],
        "clean"     : True,
    }

    yield {
        "name"    : "dist",
        "actions" : [(uristcopy.copy, (pjoin(build_dir, "index.html"),
                             pjoin(output_dir, "index.html")))],
        "verbosity" : 2,
        "targets" : [pjoin(output_dir, "index.html")],
        "file_dep" : [pjoin(build_dir, "index.html")],
    }

def task_js_file():
    """ Crate the urist.js from the template and copy to the output dir.
    """

    yield {
        "name"      : "compile",
        "actions"   : [templates.render_uristjs],
        "verbosity" : 2,
        "targets"   : [pjoin(build_dir, "js", "urist.js")],
        #"file_dep"  : [pjoin("templates", "js", "urist.js")],
        "clean"     : True,
    }

    yield {
        "name"    : "dist",
        "actions" : [(uristcopy.copy, (pjoin(build_dir, "js", "urist.js"),
                             pjoin(output_dir, "js", "urist.js")))],
        "verbosity" : 2,
        "targets" : [pjoin(output_dir, "js", "urist.js")],
        "file_dep" : [pjoin(build_dir, "js", "urist.js")],
    }


def task_load_structures():
    """ Read the legends.xml and export the sites.json from that.
    """

    return {
        "actions"   : [load_structures.load],
        "verbosity" : 2,
        "targets"   : [pjoin(build_dir, "structs.json")],
        "file_dep"  : [filefinder.struct_map(fail=False)],
        "clean"     : True,
        }


def task_group_structures():
    """ Read the structure info and find connected groups.
    """
    return {
        "actions"   : [group_structures.make_groups],
        "verbosity" : 2,
        "targets"   : [pjoin(build_dir, "groups.json")],
        "file_dep"  : [pjoin(build_dir, "structs.json")],
        "clean"     : True,
    }

def task_group_centers():
    """ Read the structure groups and find a coordinate for the group's center.
    """
    return {
        "actions"   : [group_structures.center_groups],
        "verbosity" : 2,
        "targets"   : [pjoin(build_dir, "group_centers.json")],
        "file_dep"  : [pjoin(build_dir, "groups.json")],
        "clean"     : True,
        }


def task_center_sites():
    """ Iterate over all groups and see if a site marker is close to
    the group. Move the site marker to the center of this group.
    """
    return {
       "actions"    : [group_structures.center_group_sites],
       "verbosity"  : 2,
       "file_dep"   : [pjoin(build_dir, "group_centers.json"),
                       pjoin(build_dir, "sites.json")],
       "clean"     : True,
    }


def task_place_site_markers():
    """ Calculate the map-coordinates for the sites.
    """
    return {
        "actions"   : [load_legends.create_geojson],
        "verbosity" : 2,
        "file_dep"  : [pjoin(build_dir, "sites.json"),
                       pjoin(build_dir, "detailed_maps.json")],
        "targets"   : [pjoin(build_dir, "sitesgeo.json")],
        "task_dep"  : ["center_sites"],
        "clean"     : True,
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

    for i in range(conf.getint("Map", "min_zoom"),conf.getint("Map","max_zoom") + 1):
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
        "targets"  : [pjoin(output_dir, "js", "sites.json"),pjoin(output_dir, "js", "sitesgeo.json")],
    }


def task_load_detailed_maps():
    """ Check for detailed maps in the region directory and
    send them to the output dir. Also writes the detailed_maps.json.
    """
    return {
        "actions"   : [load_legends.load_detailed_maps],
        "file_dep"  : filefinder.all_site_maps(),
        "targets"   : [pjoin(build_dir, "detailed_maps.json")] + filefinder.all_site_maps_target(),
        "verbosity" : 2
    }



def task_load_populations():
    """ Load the population counts and add them to the sites.js.
    TODO: Write the output of this into a separate file that is merged into the sitesgeo.json
    to create your own target for this. (current target is sitesgeo.json but doit doesn't allow
    this - for good reason).
    """
    return {
        "actions"   : [load_pops.load_populations],
        #"file_dep"  : [filefinder.sites_and_pops()],
        "task_dep"  : ["load_sites"],
        "verbosity" : 2
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
        "clean"     : True,
    }

def task_convert_bmp():
    """ Convert all bmp files to png and delete the bmp.
    """
    return {
        "actions" : [imgconvert.convert_bitmaps],
        "verbosity" : 2
    }


def task_biome_legend():
    """ Copy 32px images for biome rendering into the output dir.
    """
    return {
        "actions"   : [(uristcopy.copy_dir, (pjoin(tiles_dir, "32"),
                                   pjoin(output_dir, "biome_legend")))],
        "verbosity" : 2,
        "clean"     : True,
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
