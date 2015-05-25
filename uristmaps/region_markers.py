import json
import os
import math

from clint.textui import progress
from PIL import Image, ImageDraw, ImageFont

from uristmaps.config import conf

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
    

def xy2lonlat(xtile, ytile):
    """ Transform the world coordinate into lat-lon coordinates that can
    be used as GeoJSON.
    """
    global offset
    global zoom

    if offset is None:
        calc_globals()

    # Move the coordinates by the offset along to get them into the centered world render
    xtile = int(xtile) + offset
    ytile = int(ytile) + offset

    # latlon magic from osm ( http://wiki.openstreetmap.org/wiki/Slippy_map_tilenames#Tile_numbers_to_lon..2Flat._2 )
    n = 2.0 ** zoom
    lon_deg = xtile / n * 360.0 - 180.0
    lat_rad = math.atan(math.sinh(math.pi * (1 - 2 * ytile / n)))
    lat_deg = math.degrees(lat_rad)
    return (lon_deg, lat_deg)


def calc_label_coords(region):
    """ Calculate coordinates for the name label of this region.
    """
    # Inflate the coordinates from world- to unit coordinates
    coords = [list(map(lambda x: x * df_tilesize, pair)) for pair in region["coords"]]
    if region["size"] == 1:
        return coords[0][0] + df_tilesize//2, coords[0][1] + df_tilesize // 2
    return 0, 0


def create_geojson():
    """ Create the regionsgeo.json that the leaflet markers are created
    from.
    """
    #from jinja2 import Environment, FileSystemLoader
    #env = Environment(loader=FileSystemLoader("templates"))
    #tooltip_template = env.get_template("_site_tooltip.html")

    with open("{}/regions.json".format(paths["build"]),"r") as regionjson:
        regions_by_id = json.loads(regionjson.read())

    font = ImageFont.truetype(conf["Map"]["map_font"], 28)

    target_dir = "{}/regionicons/".format(paths["output"])
    if not os.path.exists(target_dir):
        os.makedirs(target_dir)

    features = []
    for region in progress.bar(regions_by_id.values()):
        # Calculate coordinates for the label
        coords = calc_label_coords(region)

        label_size = font.getsize(region["name"])
        image = Image.new("RGBA", label_size)
        draw = ImageDraw.Draw(image, "RGBA")
        draw.text((0,0), region["name"], font=font, fill=(0,0,0,255))
        image.save("{}/regionicons/{}.png".format(paths["output"], region["id"]))

        print("Region: {}".format(region["id"]))
        feature = {"type":"Feature",
                   "properties": {
                       "name": region["name"],
                       "id": region["id"],
                       "img": "/regionicons/{}.png".format(region["id"]),
                       #"popupContent": tooltip_template.render({"region":site, "detailed_maps": detailed_maps}),
                   },
                   "geometry": {
                       "type": "Point",
                       "coordinates": xy2lonlat(*coords)
                   }
        }

        features.append(feature)

    with open(os.path.join(build_dir, "regionsgeo.json"), "w") as sitesjson:
        sitesjson.write(json.dumps({"type": "FeatureCollection",
                                    "features": features}))