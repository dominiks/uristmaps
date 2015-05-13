import os, sys, logging, traceback
import json
import math
import itertools
from multiprocessing import Pool

from clint.textui import progress

from PIL import Image

from doit import get_var

from . import tilesets
from uristmaps.config import conf


paths = conf["Paths"] # Reference to that conf section to make the lines a bit shorter. Unlinke this one which still gets really long.


def load_biomes_map():
    """ Load heightmap json.
    """
    with open("{}/biomes.json".format(paths["build"]),"r") as biomejson:
        biomes = json.loads(biomejson.read())

    return biomes

def load_structures_map():
    with open("{}/structs.json".format(paths["build"]),"r") as structjson:
        structs = json.loads(structjson.read())
    return structs


def render_layer(level):
    """ Render all image tiles for the specified level.
    """
    biomes = load_biomes_map()
    structures = load_structures_map()

    # The rendersettings
    settings = {"level" : level, # The zoom level to render
                "biomes" : load_biomes_map(), # The biome information
                "structures": load_structures_map(), # The structures information
                "tile_amount" : int(math.pow(2, level)) # How many tiles the renderjob is wide (or high)
    }

    # Determine wich will be the first zoom level to use graphic tiles
    # bigger than 1px:
    zoom_offset = 0

    # One rendered tile has a side length of 256px. The smallest zoom
    # uses only 1 tile.
    mapsize = 256 
    while mapsize < biomes["worldsize"]:
        mapsize *= 2
        zoom_offset += 1

    settings["zoom_offset"] = zoom_offset
    # Zoom level 'zoom_offset' will be the first in which the world can
    # be rendered onto the map using 1px sized tiles.

    # The size of the tileset images to use for rendering.
    graphic_size = int(math.pow(2, level - zoom_offset))

    settings["stepsize"] = 1
    # The world would not fit into this layer, even if the used tiles were only 1px big.
    if graphic_size == 0:
        # We'll render only every second, or fourth etc. world coordinate
        settings["stepsize"] = int(math.pow(2, zoom_offset - level))
        graphic_size = 1
    settings["graphic_size"] = graphic_size

    # Load the tilesheet
    settings["tiles"] = tilesets.get_tileset(graphic_size)

    # Read max number of processes
    process_count = conf.getint("Performance", "processes")

    # Chunk the amount of tiles to render in equals parts
    # for each process. This would be the ideal chunk size to keep
    # processes from coming back the pool to get more work. That just
    # costs time apparently.
    chunk = settings["tile_amount"] ** 2

    # Limiting the chunksize helps getting more frequent updates for the progress bar
    # This slows the operation a bit down, though (about 1.5sek for zoom lvl 6...)
    chunk = min(chunk, 2048)

    # Have maximum as many processes as there are chunks so we don't have more
    # processes than there is work available.
    process_count = min(process_count, chunk)
    chunk //= process_count

    # Setup multiprocessing pool
    pool = Pool(process_count)


    # Save the path to the config file in a pid file for this process' children
    with open(".{}.txt".format(os.getpid()), "w") as pidfile:
        pidfile.write(get_var("conf", "config.cfg"))

    # Send the tile render jobs to the pool. Generates the parameters for each tile
    # with the get_tasks function.
    a = pool.imap_unordered(render_tile_mp, get_tasks(settings), chunksize=chunk)

    counter = 0
    total = settings["tile_amount"] ** 2

    # Show a nice progress bar with integrated ETA estimation
    with progress.Bar(label="Using {}px sized tiles ".format(graphic_size), expected_size=total) as bar:
        for b in a:
            counter += 1
            bar.show(counter)

    pool.close()
    pool.join()

    # Remove the pidfile containing the config path
    if os.path.exists(".{}.txt".format(os.getpid())):
        os.remove(".{}.txt".format(os.getpid()))


def get_tasks(settings):
    """ Generate the parameters for render_tile_mp calls for every tile
    that will be rendered. Each set of parameters is a single task for a
    process.
    """
    for x, y in itertools.product(range(settings["tile_amount"]), repeat=2):
        yield (x, y, settings)


def render_tile_mp(opts):
    """ Wrapper function used by the process pool to call render_tile.
    Unpacks the list of parameters and retrieves the exceptions that
    might be raised in the processes and get otherwise lost.
    """
    try:
        render_tile(*opts)
    except Exception as e:
        print("Exception in working process: {}".format(type(e)))
        traceback.print_exc()


def render_tile(tile_x, tile_y, settings):
    """ Render the world map tile with the given indeces at the provided level.
    """
    worldsize = settings["biomes"]["worldsize"] / settings["stepsize"] # Convenience shortname
    image = Image.new("RGBA", (256, 256), "white")

    # The size of graphic-tiles that will be used for rendering
    graphic_size = settings["graphic_size"]

    # Calculate the size of the rendered world in tiles
    render_size = 256 * math.pow(2, settings["level"])

    tiles = settings["tiles"]
    biomes = settings["biomes"]
    structures = settings["structures"]

    # How many render tiles are kept clear left and top to center the world render
    clear_tiles = 256 * math.pow(2, settings["zoom_offset"]) - settings["biomes"]["worldsize"]
    clear_tiles //= settings["stepsize"]
    clear_tiles //= 2 # Half it to get the offset left and top of the world.

    tiles_per_block = 256 // graphic_size

    for render_tile_x in range(tiles_per_block):
        # The global x coordinate of this rendered graphics tile in the render output
        global_tile_x = render_tile_x + tile_x * tiles_per_block

        # Skip this tile when it comes before anything should be visible
        if global_tile_x < clear_tiles:
            continue
        # And stop this whole row if nothing comes after
        if global_tile_x >= biomes["worldsize"] / settings["stepsize"] + clear_tiles:
            break

        for render_tile_y in range(tiles_per_block):
            # The global y coordinate for this rendered graphics tile in the render output
            global_tile_y = render_tile_y + tile_y * tiles_per_block

            # Skip this tile when it comes before anything should be visible
            if global_tile_y < clear_tiles:
                continue
            # Stop this column if nothing will be visible
            if global_tile_y >= biomes["worldsize"] / settings["stepsize"] + clear_tiles:
                break

            world_x = int(global_tile_x - clear_tiles) * settings["stepsize"]
            world_y = int(global_tile_y - clear_tiles) * settings["stepsize"]

            location = (render_tile_x * graphic_size, render_tile_y * graphic_size)

            # Render biome
            img = tiles[biomes["map"][world_y][world_x]]
            image.paste(img, location)

            # Check if theres a structure to render on it

            # TODO: Read the structures export to place tower/town sprites ontop the biomes
            try:
                struct_name = structures["map"][str(world_x)][str(world_y)]
                try:
                    struct = tiles[struct_name]
                    image.paste(struct, location, struct)
                except:
                    #print("Could not render image: {}".format(struct_name))
                    pass
            except:
                # No structure found
                pass

    target_dir = "{}/tiles/{}/{}/".format(paths["output"], settings["level"], tile_x)
    if not os.path.exists(target_dir):
        os.makedirs(target_dir)

    fname = "{}/tiles/{}/{}/{}.png".format(paths["output"], settings["level"], tile_x, tile_y)
    image.save(fname)
