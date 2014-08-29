import json, os, logging, itertools

from PIL import Image

from uristmaps.config import conf
from uristmaps.filefinder import struct_map


def same_type(structs, orig, other):
    """ Check if the tile at point orig is of the same type as
    the tile at point other.

    Also does not crash when either of the coordinates is not
    within the structs map.
    """
    try:
        return structs[orig] != "" and \
               structs[orig] == structs[(orig[0] + other[0],
                                         orig[1] + other[1])]
    except:
        return False



def load():
    orig = Image.open(struct_map())
    logging.debug("Loaded world sized {0}x{0}".format(orig.size[0]))
    pixels = orig.load()

    STRUCTS = {
        (128,128,128): "castle",
        (255,255,255): "village",
        (255,128,0)  : "crops",
        (255,160,0)  : "crops",
        (255,192,0)  : "crops",
        (0,255,0)    : "pasture", 
        (64,255,0)   : "meadow", 
        (0,160,0)    : "orchard", 
        (20,20,20)   : "tunnel", 
        (224,224,224): "stone_bridge",  
        (180,167,20) : "other_bridge",
        (192,192,192): "stone_road",
        (150,127,20) : "other_road",
        (96,96,96)   : "stone_wall",
        (160,127,20) : "other_wall", 
# The following are not really 'structures'
#        (255,255,192): "mountain",
#        (0,96,255)   : "lake", # remove this?
#        (128,64,32)  : "land",# remove this? 
#        (0,64,255)   : "ocean",# remove this?
#
    }

    structs = {}
    for (x,y) in itertools.product(range(orig.size[0]), repeat=2):
        try:
            structs[(x,y)] = STRUCTS[pixels[(x,y)]]
        except KeyError:
            # We are not interested in this structure
            structs[(x,y)] = ""
            pass

    final_tiles = {}
    # Now pass over all structures and see where tiles of the same type
    # neighbour each other
    for (x,y) in itertools.product(range(orig.size[0]), repeat=2):
        suffixes = ""
        if same_type(structs, (x,y), (0,-1)):
            suffixes += "n"
        if same_type(structs, (x,y), (-1,0)):
            suffixes += "w"
        if same_type(structs, (x,y), (0,1)):
            suffixes += "s"
        if same_type(structs, (x,y), (1,-1)):
            suffixes += "e"

        if suffixes:
            print("Suffixes to add {}".format(suffixes))
            tile_type = "{}_{}".format(structs[(x,y)], suffixes)
            try:
                final_tiles[x][y] = tile_type
            except KeyError:
                final_tiles[x] = {y : tile_type}

    result = {"worldsize": orig.size[0],
              "map": final_tiles}

    build_dir = conf["Paths"]["build"]
    if not os.path.exists(build_dir):
        os.makedirs(build_dir)
    with open("{}/structs.json".format(build_dir), "w") as heightjson:
        heightjson.write(json.dumps(result))
        logging.debug("Dumped structs into {}/biomes.structs".format(build_dir))

