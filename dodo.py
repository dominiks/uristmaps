import itertools, shutil, os, glob

from doit.tools import LongRunning

from uristmaps import render_sat_layer, load_legends, load_biomes, filefinder, tilesets, \
                      load_structures, index
from uristmaps.config import conf


# TODO: Replace cmd calls with direct python calls for better platform independence

# Some convenient references to configuration entries
build_dir = conf["Paths"]["build"]
output_dir = conf["Paths"]["output"]
region_dir = conf["Paths"]["region"]
tiles_dir = conf["Paths"]["tiles"]
tilesets_dir = conf["Paths"]["tilesets"]

DOIT_CONFIG = {"default_tasks": ["dist_legends", "render_sat", "dist_index", "copy_res"]}

def task_read_biome_info():
    """ Read biome info and write the biomes.json.
    """

    return {
        "actions"   : [load_biomes.load],
        "targets"   : ["{}/biomes.json".format(build_dir)],
        "verbosity" : 2,
        "file_dep"  : [filefinder.biome_map()]
        }

def task_load_legends():
    """ Read the legends.xml and export the sites.json from that.
    """

    return {
        "actions"   : [load_legends.load],
        "verbosity" : 2,
        "targets"   : ["{}/sites.json".format(build_dir)],
        "file_dep"  : [filefinder.legends_xml(),
                       "{}/biomes.json".format(build_dir)]
        }


def task_create_index():
    """ Crate the index.html from the template and copy to build dir.
    """

    return {
        "actions"   : [index.create],
        "verbosity" : 2,
        "targets"   : ["{}/index.html".format(build_dir)],
        "file_dep"  : [] # Dunno yet
    }


def task_dist_index():
    """ Copy the index.html from the build to output dir.
    """

    return {
        "actions" : [(copy, ("{}/index.html".format(build_dir),
                             "{}/index.html".format(output_dir)))],
        "verbosity" : 2,
        "targets" : [os.path.join(output_dir, "index.html")],
        "file_dep" : [os.path.join(build_dir, "index.html")]
        }


def task_load_structures():
    """ Read the legends.xml and export the sites.json from that.
    """

    return {
        "actions"   : [load_structures.load],
        "verbosity" : 2,
        "targets"   : ["{}/structs.json".format(build_dir)],
        "file_dep"  : [filefinder.struct_map()]
        }


def task_render_sat():
    """ Render the map layers for the 'satellite'-like view of the world.
    """

    def list_tile_files(topdir, level):
       """ Generate a complete list of the files that make up
       the layer with the given zoom level in the topdir.
       """
       return ["{}/{}/{}/{}.png".format(topdir, level, x, y) for \
               (x,y) in itertools.product(range(level + 1), repeat=2)]

    for i in range(1,conf.getint("Map","max_zoom") + 1):
        yield {
            "name"      : i,
            "verbosity" : 2,
            "actions"   : [(render_sat_layer.render_layer, (i,))],

            # TODO: Make this depend on the tilesheet for the imagesize that would be used
            #       for this zoom level.
            "file_dep"  : ["{}/biomes.json".format(build_dir),
                           "{}/structs.json".format(build_dir)],
            "targets"   : list_tile_files("{}/tiles".format(output_dir),i),
        }


def task_dist_legends():
    """ Copy the legends json into the output directory.
    """

    return {
        "actions"  : [(copy, ("{}/sites.json".format(build_dir),
                              "{}/js/sites.json".format(output_dir))
                     )],
        "file_dep" : ["{}/sites.json".format(build_dir)],
        "targets"  : ["{}/js/sites.json".format(output_dir)]
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
        "actions"   : [(copy_dir_contents, ("res", output_dir))],
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
            "file_dep"  : glob.glob(os.path.join(tiles_dir, name, "*.png")),

            # Creates <name>.png and <name>.json in tilesets/
            "targets"   : [os.path.join(tilesets_dir, "{}.png".format(name)),
                           os.path.join(tilesets_dir, "{}.json".format(name))]
            }


def copy_dir_contents(src, dst):
    """ Copy the contents of the src directory into the dst directory.
    """
    for item in glob.glob("{}/*".format(src)):
        if os.path.isdir(item):
            copy_dir(item, os.path.join(dst, os.path.relpath(item, src)))
        else:
            copy(item, os.path.join(dst, os.path.relpath(item, src)))


def copy_dir(src, dst):
    """ Copy the complete directory into the dst directory.

    shutil.copytree should work but it fails when the dst already exists and
    is unable to just overwrite that.
    """
    for root,subdirs,files in os.walk(src):
        for sub in subdirs:
            copy_dir(os.path.join(src, sub), os.path.join(dst, sub))
        for f in files:
            copy(os.path.join(root, f), 
                 os.path.join(dst, f))


def copy(src,dst):
    """ Copy a file.
    Using shutil.copyfile directly as an action for the task resulted in
    an exception so here is the copy call in its own function and it
    can also create the target directory if it does not exist.
    """
    dstdir = os.path.dirname(dst)
    if not os.path.exists(dstdir):
        os.makedirs(dstdir)
    shutil.copyfile(src, dst)

