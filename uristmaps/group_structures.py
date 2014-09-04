""" Read the structures.json and and form groups of same typed structures.
"""
import os, json, itertools

from uristmaps.config import conf


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
    blacklist = ["river", "meadow", "crops", "orchard", "pasture"]

    # first step is to grow groups on the map
    for (x,y) in itertools.product(range(world_size), repeat=2):
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

    # second step is to go over them and merge neighbouring groups
    # of the same type
    for (x,y) in itertools.product(range(world_size), repeat=2):
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

    print("Groups: {}".format(group_defs))
    print("num: {}".format(len(group_defs)))


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


