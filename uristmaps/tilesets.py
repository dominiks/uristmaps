import os, glob, math, json

from PIL import Image

from uristmaps.config import conf

tiles_dir = conf["Paths"]["tiles"]
tilesets_dir = conf["Paths"]["tilesets"]

def make_tileset(directory):
    """ Create a tileset image from all images in the
    given directory. The name of the directory is the size of the single tiles.

    Also creates an index json file specifying the coordinates of each image file
    in this tileset.
    """
    tile_size = int(os.path.basename(directory))

    files = glob.glob("{}/*.*".format(directory))

    # Create the smallest square image that can contain all tiles
    image_size = math.ceil(math.sqrt(len(files)))
    tile_image = Image.new("RGB", (image_size * tile_size, image_size * tile_size), "white")

    # The image index stores the locations of the tiles within the tileset
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

    # Make sure the tilesets directory exists
    if not os.path.exists(tilesets_dir):
        os.makedirs(tilesets_dir)

    with open(os.path.join(tilesets_dir, "{}.json".format(tile_size)), "w") as jsonfile:
        jsonfile.write(json.dumps(img_index))
    tile_image.save(os.path.join(tilesets_dir, "{}.png".format(tile_size)))

def get_tileset(image_size):
    """ Create a dictionary of tiles from the tileset with the given size.

    Returns a dict {image_name : PIL.Image}
    """
    tile_image = Image.open(os.path.join(tilesets_dir, "{}.png".format(image_size)))
    with open(os.path.join(tilesets_dir, "{}.json".format(image_size))) as jsonfile:
        index = json.loads(jsonfile.read())

    result = {}
    for name in index:
        x,y = index[name]
        # Create a copy of the cropped image as it is lazy and will result in errors when
        # the tile_image object is destroyed after this function is done.
        result[name] = tile_image.crop((x,y,x+image_size, y+image_size)).copy()
    return result
