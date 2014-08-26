import os
import json
import math
import itertools

from clint.textui import progress

from PIL import Image

from uristmaps.config import conf

# Caches the surface objects created from png files so they are
# only created once.
IMAGE_CACHE = {}

paths = conf["Paths"] # Reference to that conf section to make the lines a bit shorter. Unlinke this one which still gets really long.

def get_image(biome, size):
    """ Resolve the surface image for the given biome and image size.
    """
    if size not in IMAGE_CACHE:
        IMAGE_CACHE[size] = {}
    elif biome in IMAGE_CACHE[size]:
        return IMAGE_CACHE[size][biome]

    if size == 1 or size == 2:
        biome = "arctic_ocean"
    fname = "{}/{}/{}.png".format(paths["biome_tiles"], size, biome)

    if not os.path.exists(fname):
            print("File not found: {}".format(fname))
    image = Image.open(fname)
    print(image.mode)
    if image.size[0] != size or image.size[1] != size:
        print("WARN: image {} not in requested size ({}). Is {}.".format(fname, size, image.size))
    IMAGE_CACHE[size][biome] = image
    return image


def load_biomes_map():
    """ Load heightmap json.
    """
    with open("{}/biomes.json".format(paths["build"]),"r") as biomejson:
        biomes = json.loads(biomejson.read())

    return biomes


def render_layer(level):
    """ Render all image tiles for the specified level.
    """
    biomes = load_biomes_map()

    # Determine wich will be the first zoom level to use graphic tiles
    # bigger than 1px:
    zoom_offset = 0
    mapsize = 256
    while mapsize < biomes["worldsize"]:
        mapsize *= 2
        zoom_offset += 1

    # Zoom level 'zoom_offset' will be the first in which the world can
    # be rendered onto the map using 1px sized tiles.

    tile_amount = int(math.pow(2,level))

    for x, y in progress.bar(itertools.product(range(tile_amount), repeat=2), expected_size=math.pow(tile_amount,2)):
        render_tile(x, y, level, zoom_offset, biomes)


def render_tile(tile_x, tile_y, level, zoom_offset, biomes):
    """ Render the world map tile with the given indeces at the provided level.
    """
    worldsize = biomes["worldsize"] # Convenience shortname
    image = Image.new("RGB", (256, 256), "black")

    # The size of graphic-tiles that will be used for rendering
    graphic_size = int(math.pow(2, level - zoom_offset))

    # Calculate the size of the rendered world in tiles
    render_size = 256 * math.pow(2, level)

    # How many render tiles are kept clear left and top to center the world render
    clear_tiles = 256 * math.pow(2, zoom_offset) - worldsize
    clear_tiles //= 2 # Half it to get the offset left and top of the world.

    tiles_per_block = 256 // graphic_size

    for render_tile_x in range(tiles_per_block):
        global_tile_x = render_tile_x + tile_x * tiles_per_block
        if global_tile_x < clear_tiles:
            continue
        if global_tile_x >= biomes["worldsize"] + clear_tiles:
            break

        for render_tile_y in range(tiles_per_block):
            global_tile_y = render_tile_y + tile_y * tiles_per_block
            if global_tile_y < clear_tiles:
                continue
            if global_tile_y >= biomes["worldsize"] + clear_tiles:
                break

            world_x = int(global_tile_x - clear_tiles)
            world_y = int(global_tile_y - clear_tiles)
            
            location = (render_tile_x * graphic_size, render_tile_y * graphic_size)
            image.paste(get_image(biomes["map"][world_y][world_x], graphic_size), location)

    target_dir = "{}/tiles/{}/{}/".format(paths["output"], level, tile_x)
    if not os.path.exists(target_dir):
        os.makedirs(target_dir)

    fname = "{}/tiles/{}/{}/{}.png".format(paths["output"], level, tile_x, tile_y)
    image.save(fname)


if __name__ == "__main__":
    render_layer(5)

