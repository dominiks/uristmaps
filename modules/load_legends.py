import json, os, math

from clint.textui import puts, colored, progress, indent

from bs4 import BeautifulSoup

from config import conf

# TODO: Determine this from somewhere
worldsize = 272
zoom = 0
while 2 ** zoom < worldsize:
    zoom += 1

mapsize = 2**zoom
offset = (mapsize - worldsize) // 2

# Determines how big a site' coordinates point is in world tiles.
coordinate_scale = worldsize // 16

def load_legends_xml():
    fname = "{}/region5-legends.xml".format(conf["Paths"]["region"])
    if not os.path.exists(fname):
        puts(colored.red("region5-legends.xml not found!"))
        return
   
    puts("Reading legends xml ({} Mb)".format(os.path.getsize(fname) // 1024 // 1024))
    lines = []
    with open(fname, "r") as xmlfile:
        for line in progress.dots(xmlfile, every=1000):
            lines.append(line)
    puts("Processing xml...")
    soup = BeautifulSoup("".join(lines), "xml")
    puts(colored.green("Loaded xml file."))

    return soup


def num2deg(xtile, ytile):
    """ Transform the world coordinate into lat-lon coordinates that can
    be used as GeoJSON.
    """

    # The world coordinates are transformed:
    #   1. Multiply by the coordinate_scale to properly project them on the
    #      df world map (which uses 16 units big tiles)
    #   2. Move them by the offset along to get them into the centered world render
    #   3. Move them by half tile size to center them into this df world tile.
    xtile = int(xtile) * coordinate_scale + offset + coordinate_scale // 2
    ytile = int(ytile) * coordinate_scale + offset + coordinate_scale // 2

    # latlon magic from osm ( http://wiki.openstreetmap.org/wiki/Slippy_map_tilenames#Tile_numbers_to_lon..2Flat._2 )
    n = 2.0 ** zoom
    lon_deg = xtile / n * 360.0 - 180.0
    lat_rad = math.atan(math.sinh(math.pi * (1 - 2 * ytile / n)))
    lat_deg = math.degrees(lat_rad)
    return (lon_deg, lat_deg)

def export_sites(soup):
    """ Iterate over all sites and create a GeoJSON FeatureCollection.
    """
    puts("Loading sites...")

    features = []
    for site in progress.bar(soup.find_all("site")):
        feature = {"type":"Feature",
                "properties": {
                    "name": site.find_next("name").text,
                    "amenity": site.find_next("type").text,
                    "id": site.find_next("id").text,
                    "img": "/assets/icons/{}.png".format(site.find_next("type").text.replace(" ", "_")),
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

    with open("{}/sites.json".format(conf["Paths"]["build"]), "w") as sitesjson:
        sitesjson.write(json.dumps({"type": "FeatureCollection",
                                    "features": features}))
    puts(colored.green("OK"))


if __name__ == "__main__":
    soup = load_legends_xml()
    export_sites(soup)
