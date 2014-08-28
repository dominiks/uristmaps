import os, sys, logging, traceback
import json
import math
import itertools
from multiprocessing import Pool

from clint.textui import progress

from PIL import Image

from uristmaps import tilesets
from uristmaps.config import conf


paths = conf["Paths"] # Reference to that conf section to make the lines a bit shorter. Unlinke this one which still gets really long.


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

    # Read max number of processes
    process_count = conf.getint("Performance", "processes")

    # Chunk the amount of tiles to render in equals parts
    # for each process
    chunk = tile_amount ** 2
    
    # Have maximum as many processes as there are chunks to keep the chunk size over 1
    process_count = min(process_count, chunk)
    chunk //= process_count

    # Setup multiprocessing pool
    pool = Pool(process_count)

    graphic_size = int(math.pow(2, level - zoom_offset))
    TILES = tilesets.get_tileset(graphic_size)

    # Send the tile render jobs to the pool. Generates the parameters for each tile
    # with the get_tasks function.
    pool.imap_unordered(render_tile_mp, get_tasks(tile_amount, level, zoom_offset, biomes, TILES), chunksize=chunk)
    pool.close()
    pool.join()


def get_tasks(tileamount, level, zoom_offset, biomes, tiles):
    for x, y in itertools.product(range(tileamount), repeat=2):
        yield (x, y, level, zoom_offset, biomes, tiles)


def render_tile_mp(opts):
    try:
        render_tile(*opts)
    except Exception as e:
        print("Exception in working process: {}".format(type(e)))
        traceback.print_exc()


def render_tile(tile_x, tile_y, level, zoom_offset, biomes, tiles):
    """ Render the world map tile with the given indeces at the provided level.
    """
    worldsize = biomes["worldsize"] # Convenience shortname
    image = Image.new("RGB", (256, 256), "white")

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
            img = tiles[biomes["map"][world_y][world_x]]
            image.paste(img, location)

            # TODO: Read the structures export to place tower/town sprites ontop the biomes

    target_dir = "{}/tiles/{}/{}/".format(paths["output"], level, tile_x)
    if not os.path.exists(target_dir):
        os.makedirs(target_dir)

    fname = "{}/tiles/{}/{}/{}.png".format(paths["output"], level, tile_x, tile_y)
    image.save(fname)


if __name__ == "__main__":
    render_layer(5)

