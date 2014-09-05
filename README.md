Urist Maps
==========

**See http://www.uristmaps.org/ for more information!**

Renders a Google Maps like view of a Dwarf Fortress world using Leaflet.js.

Quickstart
----------

### 1. Setup UristMaps

Clone the repository into a virtualenv and execute

    python setup.py install

To install the dependencies.

### 2. Export the world in DF

Start a new game in your world and select Legends-mode. Export:

1. XML-Dump
2. Biome Map

### 3. Create the UristMap

Copy the `config.cfg.sample` file to `config.cfg` and set the `region` folder to the location of the files you exported in step 1. Then execute

    doit

To start a render of the world. To then start a webserver that you can view the map with
execute

    doit host

The map will be accessible under http://localhost:8000/

Advanced
--------

### Multiple configurations

If you want to render multiple worlds each one needs its own config file. You can specify which config file to use when starting uristmaps:

    doit conf=config_file.cfg



### Subtasks

Some `doit`-tasks allow subtasks to be run. Use

    doit render_biome:3

To render zoom-level 3 of the biome layer.

