import json, os, math, logging, re

from clint.textui import progress

from PIL import Image

from uristmaps.config import conf
from uristmaps import filefinder

paths = conf["Paths"]

df_tilesize = 16

# Offset of the world within the rendered map area.
offset = None

# Minimum zoom level to fit all world coodinates in a rendered map using 1px big tiles.
# This zoom level can be seen as the equivalent of 100% zoom where each coordinate
# is 1px big.
zoom = None

output_dir = conf.get("Paths", "output")
build_dir = conf.get("Paths", "build")

def calc_globals():
    global offset
    global zoom
    with open(os.path.join(build_dir, "biomes.json")) as biomjs:
        biomes = json.loads(biomjs.read())
    worldsize = biomes["worldsize"]

    zoom = 0
    while 2 ** zoom < worldsize:
        zoom += 1

    mapsize = 2**zoom
    offset = (mapsize - worldsize) // 2

def create_geojson():
    """ Create the regionsgeo.json that the leaflet markers are created
    from.
    """
    from jinja2 import Environment, FileSystemLoader
    env = Environment(loader=FileSystemLoader("templates"))
    tooltip_template = env.get_template("_site_tooltip.html")

    with open("{}/regions.json".format(paths["build"]),"r") as regionjson:
        regions_by_id = json.loads(regionjson.read())

    # Read the detailed maps dimensions
    with open(os.path.join(build_dir, "detailed_maps.json")) as sitesjs:
        detailed_maps = json.loads(sitesjs.read())

    features = []
    for site in sites:
        feature = {"type":"Feature",
                   "properties": {
                       "name": site["name"],
                       "type": site["type"],
                       "id": site["id"],
                       "img": "/icons/{}.png".format(site["type"].replace(" ", "_")),
                       "popupContent": tooltip_template.render({"site":site, "detailed_maps": detailed_maps}),
                   },
                   "geometry": {
                       "type": "Point",
                       "coordinates": xy2lonlat(*site["coords"])
                   }
        }

        # Add the bounding rect for the detailed map to the geojson info.
        if site["id"] in detailed_maps:
            # The detailed maps use 48px big blocks
            width  = detailed_maps[site["id"]]["px_width"]  // 48
            height = detailed_maps[site["id"]]["px_height"] // 48

            # These coords are not really geojson as they are used directly by leaflet
            # and leaflet uses the coordinates switched around (y,x)
            # oh and the bouning rect is defined by the bottom-left and upper-right
            # corner. Hurray...
            southwest = [site["coords"][0] - width // 2, site["coords"][1] - height // 2]
            northeast = [site["coords"][0] + width // 2, site["coords"][1] + height // 2]

            sw_lat_lon = xy2lonlat(*southwest)
            ne_lat_lon = xy2lonlat(*northeast)
            feature["properties"]["map_bounds"] = [[sw_lat_lon[1], sw_lat_lon[0]],
                                                   [ne_lat_lon[1], ne_lat_lon[0]]]

        features.append(feature)

    with open(os.path.join(build_dir, "sitesgeo.json"), "w") as sitesjson:
        sitesjson.write(json.dumps({"type": "FeatureCollection",
                                    "features": features}))