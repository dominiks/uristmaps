import json, os, logging

from PIL import Image

from uristmaps.config import conf
from uristmaps.filefinder import biome_map

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
        (255,255,192): "mountain",
        (0,96,255)   : "lake", # remove this?
        (128,64,32)  : "land",# remove this? 
        (0,64,255)   : "ocean",# remove this?
    }

    structs = []
    for y in range(orig.size[1]):
        row = []
        for x in range(orig.size[0]):
            row.append(STRUCTS[pixels[(x,y)]])
        structs.append(row)

    result = {"worldsize": orig.size[0],
              "map": structs}
    build_dir = conf["Paths"]["build"]
    if not os.path.exists(build_dir):
        os.makedirs(build_dir)
    with open("{}/structs.json".format(build_dir), "w") as heightjson:
        heightjson.write(json.dumps(result))
        logging.debug("Dumped structs into {}/biomes.structs".format(build_dir))

