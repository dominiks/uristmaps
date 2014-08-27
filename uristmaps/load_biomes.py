import json, os, logging

from PIL import Image

from uristmaps.config import conf

def load():
    orig = Image.open("{}/world_graphic-bm-region5-250--10081.bmp".format(conf["Paths"]["region"]))
    logging.debug("Loaded world sized {0}x{0}".format(orig.size[0]))
    pixels = orig.load()

    BIOMES = {
        (128,128,128): "mountain",
        (0,224,255): "temperate_freshwater_lake",
        (0,192,255): "temperate brackish_lake",
        (0,160,255): "temperate saltwater_lake",
        (0,96,255): "tropical_freshwater_lake",
        (0,64,255): "tropical_brackish_lake", 
        (0,32,255): "tropical_saltwater_lake", 
        (0,255,255): "arctic_ocean", 
        (0,0,255): "tropical_ocean", 
        (0,128,255): "temperate_ocean",  
        (64,255,255): "glacier",
        (128,255,255): "tundra",
        (96,192,128): "temperate_freshwater_swamp",
        (64,192,128): "temperate_saltwater_swamp",
        (96,255,128): "temperate_freshwater_marsh", 
        (64,255,128): "temperate_saltwater_marsh",
        (96,192,64): "tropical_freshwater_swamp",
        (64,192,64): "tropical_saltwater_swamp", 
        (64,255,96): "mangrove_swamp",
        (96,255,64): "tropical_freshwater_marsh",
        (64,255,64): "tropical_saltwater_marsh",
        (0,96,64): "taiga_forest",
        (0,96,32): "temperate_conifer_forest",
        (0,160,32): "temperate_broadleaf_forest",
        (0,96,0): "tropical_conifer_forest",
        (0,128,0): "tropical_dry_broadleaf_forest",
        (0,160,0): "tropical_moist_broadleaf_forest",
        (0,255,32): "temperate_grassland",
        (0,224,32): "temperate_savanna",
        (0,192,32): "temperate_shrubland",
        (255,160,0): "tropical_grassland",
        (255,176,0): "tropical_savanna",
        (255,192,0): "tropical_shrubland",
        (255,96,32): "badland_desert",
        (255,255,0): "sand_desert",
        (255,128,64): "rock_desert",
    }

    biomes = []
    for y in range(orig.size[1]):
        row = []
        for x in range(orig.size[0]):
            row.append(BIOMES[pixels[(x,y)]])
        biomes.append(row)

    result = {"worldsize": orig.size[0],
              "map": biomes}
    build_dir = conf["Paths"]["build"]
    if not os.path.exists(build_dir):
        os.makedirs(build_dir)
    with open("{}/biomes.json".format(build_dir), "w") as heightjson:
        heightjson.write(json.dumps(result))
        logging.debug("Dumped biomes into {}/biomes.json".format(build_dir))

