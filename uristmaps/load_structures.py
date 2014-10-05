import json, os, logging, itertools

from PIL import Image

from clint.textui import progress

from uristmaps.config import conf
from uristmaps import filefinder


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
        (0,96,255)   : "lake",
# The following are not really 'structures'
#        (255,255,192): "mountain",
#        (128,64,32)  : "land",# remove this? 
#        (0,64,255)   : "ocean",# remove this?
#
    }

    RIVERS = {
        (0,224,255)  : "river",
        (0,255,255)  : "river",
        (0,112,255)  : "river",
    }

    structs = {}

    struct_image = Image.open(filefinder.struct_map())
    struct_pixels = struct_image.load()
    world_size = struct_image.size[0]
    del(struct_image)
    hydro_image = Image.open(filefinder.hydro_map())
    hydro_pixels = hydro_image.load()
    del(hydro_image)
    for (x,y) in progress.dots(itertools.product(range(world_size), repeat=2), every=20000):
        try:
            structs[(x,y)] = STRUCTS[struct_pixels[(x,y)]]
        except KeyError:
            # We are not interested in this structure
            structs[(x,y)] = ""
        # Check if there is a river
        try:
            river = RIVERS[hydro_pixels[(x,y)]]
            if structs[(x,y)] != "" and structs[(x,y)] != "river":
                #print("Overwriting {} with river.".format(structs[(x,y)]))
                pass
            structs[(x,y)] = "river"
        except KeyError:
            pass

    final_tiles = {}
    # Now pass over all structures and see where tiles of the same type
    # neighbour each other
    for (x,y) in progress.dots(itertools.product(range(world_size), repeat=2), every=20000):
        suffixes = ""
        if same_type(structs, (x,y), (0,-1)):
            suffixes += "n"
        if same_type(structs, (x,y), (-1,0)):
            suffixes += "w"
        if same_type(structs, (x,y), (0,1)):
            suffixes += "s"
        if same_type(structs, (x,y), (1,0)):
            suffixes += "e"

        if suffixes:
            tile_type = "{}_{}".format(structs[(x,y)], suffixes)
            try:
                final_tiles[x][y] = tile_type
            except KeyError:
                final_tiles[x] = {y : tile_type}

    result = {"worldsize": world_size,
              "map": final_tiles}

    build_dir = conf["Paths"]["build"]
    if not os.path.exists(build_dir):
        os.makedirs(build_dir)
    with open("{}/structs.json".format(build_dir), "w") as heightjson:
        heightjson.write(json.dumps(result))
        logging.debug("Dumped structs into {}/biomes.structs".format(build_dir))

