import json

from PIL import Image

orig = Image.open("maps/world_graphic-el-region5-250--10081.bmp")
pixels = orig.load()
print("Found elevation map @{}x{}".format(orig.size[0], orig.size[1]))

print("Generating heightmap.")
heightmap = []
for y in range(orig.size[1]):
    row = []
    for x in range(orig.size[0]):
        row.append(pixels[(x,y)][2])
        # When r=g=b then the image is gray and means land.
        if pixels[(x,y)][0] == pixels[(x,y)][1] == pixels[(x,y)][2]:
            pass
        else:
            #print(pixels[(x,y)])
            pass
    heightmap.append(row)

result = {"width": orig.size[0], "height": orig.size[1],
          "map": heightmap}
with open("build/heightmap.json", "w") as heightjson:
    heightjson.write(json.dumps(result))
    print("Dumped heightmap into build/heightmap.json")

