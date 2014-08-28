import json, os, math, logging

from clint.textui import progress
from bs4 import BeautifulSoup

from uristmaps.config import conf
from uristmaps.filefinder import legends_xml

df_tilesize = 16

# Offset of the world within the rendered map area.
offset = None

# Minimum zoom level to fit all world coodinates in a rendered map using 1px big tiles.
zoom = None

def load_legends_xml():
    global offset
    global coordinate_scale
    global zoom

    with open("{}/biomes.json".format(conf["Paths"]["build"])) as biomjs:
        biomes = json.loads(biomjs.read())
    worldsize = biomes["worldsize"]

    zoom = 0
    while 2 ** zoom < worldsize:
        zoom += 1

    mapsize = 2**zoom
    offset = (mapsize - worldsize) // 2

    fname = legends_xml()
    logging.debug("Reading legends xml ({} Mb)".format(os.path.getsize(fname) // 1024 // 1024))
    lines = []
    with open(fname, "r") as xmlfile:
        logging.info("Loading legends.xml file.")
        for line in progress.dots(xmlfile, every=1000):
            lines.append(line)
    logging.debug("Processing xml.")
    soup = BeautifulSoup("".join(lines), "xml")
    logging.debug("Loaded xml file.")

    return soup


def num2deg(xtile, ytile):
    """ Transform the world coordinate into lat-lon coordinates that can
    be used as GeoJSON.
    """

    # The world coordinates are transformed:
    #   1. Multiply by the size of a world tile to properly project them on the
    #      df world map (which uses 16 units big tiles)
    #   2. Move them by the offset along to get them into the centered world render
    #   3. Move them by half tile size to center them into this df world tile.
    xtile = int(xtile) * df_tilesize + offset + df_tilesize // 2
    ytile = int(ytile) * df_tilesize + offset + df_tilesize // 2

    # latlon magic from osm ( http://wiki.openstreetmap.org/wiki/Slippy_map_tilenames#Tile_numbers_to_lon..2Flat._2 )
    n = 2.0 ** zoom
    lon_deg = xtile / n * 360.0 - 180.0
    lat_rad = math.atan(math.sinh(math.pi * (1 - 2 * ytile / n)))
    lat_deg = math.degrees(lat_rad)
    return (lon_deg, lat_deg)

def export_sites(soup):
    """ Iterate over all sites and create a GeoJSON FeatureCollection.
    """
    sites = soup.find_all("site")
    logging.debug("Loading {} sites...".format(len(sites)))

    features = []
    for site in sites:
        feature = {"type":"Feature",
                "properties": {
                    "name": site.find_next("name").text,
                    "amenity": site.find_next("type").text,
                    "id": site.find_next("id").text,
                    "img": "/icons/{}.png".format(site.find_next("type").text.replace(" ", "_")),
                    "popupContent": """{}<br>
                    Type: {}<br>
                    Coords: {}
                    """.format(site.find_next("name").text.title(),
                           site.find_next("type").text.title(),
                           site.find_next("coords").text)
            },
            "geometry": {
                "type": "Point",
                "coordinates": num2deg(*site.find_next("coords").text.split(","))
                }
        }
        features.append(feature)

    if not os.path.exists(conf["Paths"]["build"]):
        os.makedirs(conf["Paths"]["build"])
    with open("{}/sites.json".format(conf["Paths"]["build"]), "w") as sitesjson:
        sitesjson.write(json.dumps({"type": "FeatureCollection",
                                    "features": features}))


def load():
    soup = load_legends_xml()
    export_sites(soup)
