import json, os, math, logging, re

from clint.textui import progress

from PIL import Image

from uristmaps.config import conf
from uristmaps import filefinder

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


def load_regions():
    """ Load the region information.
    """
    global offset
    global zoom

    if offset is None:
        calc_globals()

    # Open the legends xml
    fname = filefinder.legends_xml()
    logging.debug("Reading legends xml ({} Mb)".format(os.path.getsize(fname) // 1024 // 1024))

    # Store all read regions.
    regions = []
    regions_element_started = False
    with open(fname, "r", encoding="iso-8859-1") as xmlfile:
        for line in xmlfile:
            if not regions_element_started:
                if line.startswith("<regions>"):
                    regions_element_started = True
                continue
            try:
                if not add_to_regions(regions, line.strip()):
                    break
            except Exception as e:
                print(e)
                print("Line: '{}'".format(line))
                break

    # The result region map. Maps region id -> id.name,type,coords
    region_map = {}
    for region in regions:
        region_map[region["id"]] = region

    # Open the legends-PLUS file and parse for coordinates info
    # For every region there will be 2 tags: id and coords. When we find
    # an id-element, the next one will be the coords for this id.
    fname = filefinder.legends_plus_xml()
    logging.debug("Reading legends plus xml ({} Mb)".format(os.path.getsize(fname) // 1024 // 1024))

    regions_element_started = False
    region_id = None # The id of the region that we are now reading
    with open(fname, "r", encoding="iso-8859-1") as xmlfile:
        for line in xmlfile:
            line = line.strip()
            if not regions_element_started:
                if line.startswith("<regions>"):
                    regions_element_started = True
                continue
            if line.startswith("</regions>"):
                break

            if line.endswith("region>"):
                continue

            try:
                start = line.index(">")
                end = line.index("<", start)
                start += 1
                if line.startswith("<id>"):
                    region_id = line[start:end]
                elif line.startswith("<coords>"):
                    # Magic!
                    # 1. Split the string by |
                    # 2. Iterate over that, but ignore the last [:-1] element, as its empty (the line ends with a |
                    # 3. Iterate over these split items, split them by ,
                    # 4. Map int function on this pair of values to convert from str
                    # 5. list() on that result, as it is an iterator and will crash this construct.
                    coords = [list(map(int, item.split(","))) for item in line[start:end].split("|")[:-1]]
                    region_map[region_id]["coords"] = coords
                    region_map[region_id]["size"] = len(coords)
            except Exception as e:
                print(e)
                print("Line: '{}'".format(line))
                break

    with open(os.path.join(build_dir, "regions.json"), "w") as regionsjson:
        try:
            regionsjson.write(json.dumps(region_map))
        except Exception as e:
                print(region_map)
                print(e)


def add_to_regions(regions, line):
    """ Parse the current line add the information to the sites list.
    Return true when the line was handled, return false when the
    sites-block is over.
    """
    if line == "<region>":
        regions.append({})
        return True
    if line == "</region>":
        return True
    if line == "</regions>":
        return False

    start = line.index(">")
    end = line.index("<", start)
    start += 1
    if line.startswith("<id>"):
        regions[-1]["id"] = line[start:end]
        return True
    if line.startswith("<type>"):
        regions[-1]["type"] = line[start:end]
        return True
    if line.startswith("<name>"):
        regions[-1]["name"] = line[start:end]
        return True
    return False


def deflate_coords(x,y):
    """ Convert the coordinates from rough world coordinates to more
    exact world_tile coordinates.
    """
    return int(x) * df_tilesize + df_tilesize // 2, int(y) * df_tilesize + df_tilesize // 2


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


def load_detailed_maps():
    """ Convert the bmp in the region dir to the output dir as png.
    And add them to the detailed_maps.json
    """
    id_finder = re.compile("-(\d+)\.png$")

    # Iterate over all detailed map files, determine the size and site-id

    # Save the id,dimesions and filename to the json
    # export the image as png to the output dir
    maps = {}
    site_maps = filefinder.all_site_maps()

    if not site_maps:
        return

    for img_file in progress.bar(site_maps):
        site_id = id_finder.findall(img_file)
        if not site_id:
            # For some reason there was no id to find?
            continue
        site_id = site_id[0] # Get the first (and only item of that result list)

        image = Image.open(img_file)
        maps[site_id] = {"px_width": image.size[0], "px_height": image.size[1]}

        # Save image as png to output
        if not os.path.exists(os.path.join(output_dir, "sites")):
            os.makedirs(os.path.join(output_dir, "sites"))
        target_file = os.path.join(output_dir, "sites", "{}.png".format(site_id))
        if not os.path.exists(target_file):
            image.save(target_file, "PNG")

    # Dump maps dict into json
    with open(os.path.join(build_dir, "detailed_maps.json"), "w") as jsonfile:
        jsonfile.write(json.dumps(maps))
