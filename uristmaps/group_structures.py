""" Read the structures.json and and form groups of same typed structures.
"""
import os, json, itertools, collections

from clint.textui import progress

from uristmaps.config import conf

build_dir = conf["Paths"]["build"]

# Maps valid site types to structure types
TYPE_TO_STRUCT = {
    "hamlet"         : "village",
    "dark fortress"  : "castle",
    "dark pits"      : "castle",
    "tomb"           : "castle",
    "hillocks"       : "village",
    "town"           : "village",
    "forest retreat" : "village",
}


def make_groups():
    # load structures json into a map
    with open(os.path.join(conf["Paths"]["build"], "structs.json")) as structjs:
        structures = json.loads(structjs.read())

    # Maps { x -> y -> group_index }
    # Better would be {(x,y) -> group_index} but json cannot use tuples as keys!
    groups = {}

    # Maps { group_index -> struct type}
    group_defs = {}

    next_grp_index = 0

    world_size = structures["worldsize"]

    # These structures should not be grouped (usually because there is no marker for them)
    blacklist = ["river", "meadow", "crops", "orchard", "pasture", "road"]

    # first step is to grow groups on the map
    with progress.Bar(label="Pass 1 ", expected_size=world_size, every=100) as bar:
        for (x,y) in itertools.product(range(world_size), repeat=2):
            bar.show(x)
            this_type = get_type(structures["map"], x, y)

            # Skip this tile when there's no structure
            if this_type == "" or this_type in blacklist:
                continue

            current_grp = get_grp(groups, x, y)            
            if current_grp == "":
                current_grp = next_grp_index
                group_defs[current_grp] = this_type
                next_grp_index += 1
                groups[x][y] = current_grp

            allow_x = False
            if x < world_size:
                allow_x = True
                right = get_type(structures["map"], x+1, y)
                if right == this_type:
                    set_grp(groups, x+1, y, current_grp)

            allow_y = False
            if y < world_size:
                allow_y = True
                below = get_type(structures["map"], x, y+1)
                if below == this_type:
                    set_grp(groups, x, y+1, current_grp)

            if allow_x and allow_y:
                right_below = get_type(structures["map"], x+1, y+1)
                if right_below == this_type:
                    set_grp(groups, x+1, y+1, current_grp)

        # for each tile, get the type of the one above and to the right
        # to check if we have a new group here. write the grp index
        # on these cells
        bar.show(world_size)

    # second step is to go over them and merge neighbouring groups
    # of the same type
    with progress.Bar(label="Pass 2 ", expected_size=world_size, every=100) as bar:
        for (x,y) in itertools.product(range(world_size), repeat=2):
            bar.show(x)
            this_grp = get_grp(groups, x, y)

            # skip non-groups
            if this_grp == "":
                continue

            allow_x = False
            if x < world_size:
                allow_x = True
                right = get_grp(groups, x+1, y)
                if right != "" and right != this_grp and \
                    group_defs[this_grp] == group_defs[right]:
                    replace_grp(groups, right, this_grp)
                    del(group_defs[right])

            allow_y = False
            if y < world_size:
                allow_y = True
                below = get_grp(groups, x, y+1)
                if below != "" and below != this_grp and \
                    group_defs[this_grp] == group_defs[below]:
                    replace_grp(groups, below, this_grp)
                    del(group_defs[below])

            if allow_x and allow_y:
                right_below = get_grp(groups, x+1, y+1)
                if right_below != "" and right_below != this_grp and \
                    group_defs[this_grp] == group_defs[right_below]:
                    replace_grp(groups, right_below, this_grp)
                    del(group_defs[right_below])

        # Remove empty x-coordinates from the map
        groups_final ={k:v for k,v in groups.items() if v}


    result = {"groups": groups_final, "defs": group_defs}
    with open(os.path.join(build_dir, "groups.json"), "w") as groupjs:
        groupjs.write(json.dumps(result))


def center_groups():
    """ Write a json that maps {groupId -> x,y} to mark the center
    coordinate of that group.
    """
    group_coords = collections.defaultdict(list)
    with open(os.path.join(build_dir, "groups.json")) as groupjs:
        groups = json.loads(groupjs.read())

    for x in groups["groups"]:
        for y in groups["groups"][x]:
            group_coords[groups["groups"][x][y]].append((x,y))

    # Maps group -> (left, top, right, bottom)
    group_minmax = {}
    for group in group_coords:
        for (x,y) in group_coords[group]:
            if group not in group_minmax:
                group_minmax[group] = [int(x),int(y),int(x),int(y)]
            else:
                c = group_minmax[group]
                group_minmax[group] = [min(int(x),c[0]), min(int(y), c[1]),
                                       max(int(x),c[2]), max(int(y), c[3])]

    group_centers = {}
    for group in group_minmax:
        c = group_minmax[group]
        group_centers[group] = ((c[0] + c[2]) // 2,
                                (c[1] + c[3]) // 2)

    with open(os.path.join(build_dir, "group_centers.json"), "w") as sitesjs:
        sitesjs.write(json.dumps(group_centers))

def center_group_sites():
    with open(os.path.join(build_dir, "sites.json")) as sitesjs:
        # Contains the info about sites markers
        sites = json.loads(sitesjs.read())
    
    with open(os.path.join(build_dir, "group_centers.json")) as centersjs:
        # Maps group ids to centered coordinates
        centers = json.loads(centersjs.read())

    with open(os.path.join(build_dir, "groups.json")) as groupsjs:
        # Contains info about groups (type)
        group_info = json.loads(groupsjs.read())

    # Iterate over all sites (skip those without structures)
    # find the closest group that is not in the visited group set
    # Move the site to the center coordinates

    # Contains the IDs of groups that have received a marker
    visited_groups = set()

    for site in sites:
        if site["type"] not in TYPE_TO_STRUCT:
            #print("Skipping type: {}".format(site["type"]))
            continue
        local_grps = []

        radius = 0
        site_moved = False
        while True:
            for group_id in find_groups(site["coords"], radius, group_info["groups"]):
                group_id = str(group_id)
                if group_id in visited_groups:
                    continue
                if group_info["defs"][group_id] not in TYPE_TO_STRUCT[site["type"]]:
                    continue
                # Move site marker and break loop
                site["coords"] = centers[group_id]
                site["coords_accurate"] = True
                visited_groups.add(group_id)
                site_moved = True
                break

            radius += 1
            if radius >= 16 or site_moved:
                #print("No group found for marker: {}".format(site))
                break
            

    with open(os.path.join(build_dir, "sites.json"), "w") as sitesjs:
        sitesjs.write(json.dumps(sites))


def find_groups(coords, radius, groups):
    """ Find the list of groups with the given radius around
    the coords.
    """
    result = []
    for x in range(radius):
        try:
            result.append(groups[str(coords[0]-x)][str(coords[1]-(radius-x))])
        except:
            pass
        try:
            result.append(groups[str(coords[0]-x)][str(coords[1]+(radius-x))])
        except:
            pass
        try:
            result.append(groups[str(coords[0]+x)][str(coords[1]+(radius-x))])
        except:
            pass
        try:
            result.append(groups[str(coords[0]+x)][str(coords[1]-(radius-x))])
        except:
            pass
    #print("Found {} groups.".format(len(result)))
    return result


def replace_grp(groups, old, new):
    """ Replace all instances of old-grp index with the new one
    in the group-map groups.
    """
    for x in groups:
        for y in groups[x]:
            if groups[x][y] == old:
                groups[x][y] = new


def set_grp(groups, x, y, group_index):
    if x not in groups:
        groups[x] = {}
    groups[x][y] = group_index

        
def get_grp(groups, x, y):
    if x not in groups:
        groups[x] = {}
        return ""
    if y not in groups[x]:
        return ""
    return groups[x][y]


def get_type(structs, x, y):
    """ Determine the type of the structure at the given coordinates.
    When there is no structure the result is ""
    """
    try:
        typ = structs[str(x)][str(y)].split("_")[0]
        return typ
    except Exception as e:
        return ""


