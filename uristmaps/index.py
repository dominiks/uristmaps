import os, json

from jinja2 import Environment, FileSystemLoader

from uristmaps import __version__
from uristmaps.config import conf
from uristmaps.filefinder import world_history


build_dir = conf["Paths"]["build"]


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
    tpl_context["world_name"] = get_world_name()

    # Get list of sites to write into sidebar
    with open(os.path.join(build_dir, "sites.json")) as sitesjs:
        sites_geojs = json.loads(sitesjs.read())
    tpl_context["sites"] = sites_geojs["features"]

    # Save the file to the build dir to finish
    with open(os.path.join(build_dir, "index.html"), "w") as index_file:
        index_file.write(index_tpl.render(tpl_context))


def get_world_name():
    """ Find the name of the world.
    First line in world_history.txt is the dwarfen name, second line is translated
    """
    with open(world_history()) as hist_file:
        return  "{} - {}".format(hist_file.readline().strip(), hist_file.readline().strip())

