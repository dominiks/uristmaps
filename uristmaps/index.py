import os, json, glob

from jinja2 import Environment, FileSystemLoader

from uristmaps import __version__
from uristmaps.config import conf
from uristmaps.filefinder import world_history


build_dir = conf["Paths"]["build"]
tile_dir = conf["Paths"]["tiles"]
tile_output_dir = "biome_legend/"

def create():
    """ Create the index file and save it to the build dir.
    """

    # Setup jinja env and load index template
    env = Environment(loader=FileSystemLoader("templates"))
    index_tpl = env.get_template("index.html")

    # Create template render context and insert version
    tpl_context = {
        "version" : __version__
    }

    # Add world name
    try:
        tpl_context["world_name"] = get_world_name()
    except IOError:
        print("Could not find world history file to resolve world name!")

    # Get list of sites to write into sidebar
    with open(os.path.join(build_dir, "sites.json")) as sitesjs:
        sites_geojs = json.loads(sitesjs.read())
    tpl_context["sites"] = sites_geojs["features"]

    ## Gather biome info for the legend
    tpl_context["biomes_legend"] = create_biomes_legend()

    # Save the file to the build dir to finish
    with open(os.path.join(build_dir, "index.html"), "w") as index_file:
        index_file.write(index_tpl.render(tpl_context))


def create_biomes_legend():
    """ Iterate over all tile images in tiles/32/ and
    create a map for all non-structures mapping
        { file_name -> /biome_legend/file_name }
    This is processed by the _biome-legend.html template.
    """
    # keywords for image files that are blocked
    keywords = ["village", "river", "wall", "castle"]
    biomes = {}
    for img_file in glob.glob(os.path.join(tile_dir, "32", "*.png")):
        if [img_file for struct in keywords if struct in img_file]:
            continue
        # Resolve filename and remove file extension to use as biome name
        filename = os.path.splitext(os.path.basename(img_file))[0]
        biomes[filename.replace("_", " ")] = tile_output_dir + os.path.basename(img_file)
    return biomes


def get_world_name():
    """ Find the name of the world.
    First line in world_history.txt is the dwarfen name, second line is translated
    """
    with open(world_history()) as hist_file:
        return  "{} - {}".format(hist_file.readline().strip(), hist_file.readline().strip())

