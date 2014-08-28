import os, glob, math, json

from PIL import Image

from uristmaps.config import conf

tiles_dir = conf["Paths"]["biome_tiles"]
tilesets_dir = conf["Paths"]["tilesets"]

def make_tileset(directory):
    """ Create a tileset image from all images in the
    given directory. The name of the directory is the size of the single tiles.

    Also creates an index json file specifying the coordinates of each image file
    in this tileset.
    """
    tile_size = int(os.path.basename(directory))

    files = glob.glob("{}/*.*".format(directory))

    image_size = math.ceil(math.sqrt(len(files)))
    tile_image = Image.new("RGB", (image_size * tile_size, image_size * tile_size), "white")

    img_index = {}
    x,y = 0,0
    for img_file in files:
        tile_img = Image.open(img_file)
        tile_image.paste(tile_img, (x * tile_size, y * tile_size))

        img_index[os.path.splitext(os.path.basename(img_file))[0]] = (x * tile_size, y * tile_size)
        if x == image_size - 1:
            x = 0
            y += 1
        else:
            x += 1

    with open(os.path.join(tilesets_dir, "{}.json".format(tile_size)), "w") as jsonfile:
        jsonfile.write(json.dumps(img_index))

    tile_image.save(os.path.join(tilesets_dir, "{}.png".format(tile_size)))

def get_tileset(image_size):
    """ Create a dictionary of tiles from the tileset with the given size.

    Returns a dict {image_name : PIL.Image}
    """
    tile_image = Image.open(os.path.join(tilesets_dir, "{}.png".format(image_size)))
    with open(os.path.join(tilesets_dir, "{}.json".format(image_size))) as js:
        index = json.loads(js.read())

    result = {}
    for name in index:
        x,y = index[name]
        result[name] = tile_image.crop((x,y,x+image_size, y+image_size))
        print("{} : {}".format(name, result[name]))
    return result
