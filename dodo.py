def task_read_biome_info():
    """read info"""

    return {
        "actions": [["python", "modules/load_biomes.py"]],
        "targets": ["build/biomes.json"],
        "verbosity": 2,
        }

def task_load_legends():

    return {
        "actions": [["python", "modules/load_legends.py"]],
        "verbosity": 2,
        "targets": ["build/sites.json"],
        }

def task_render_biomes():

    return {
        "actions": [["python", "modules/render_biome_layer.py"]],
        "verbosity": 2,
        "file_dep": ["build/biomes.json"]
        }

def task_dist_legends():
    return {
        "actions": [["cp", "build/sites.json", "output/assets/sites.json"]],
        "file_dep": ["build/sites.json"],
        "targets": ["output/assets/sites.json"]
    }
