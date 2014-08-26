Urist Maps
==========

Renders a Google Maps like view of a Dwarf Fortress world using Leaflet.js.

Installation
------------

Clone the repository into a virtualenv and execute

    python setup.py install

To install the dependencies.

How to run
----------

See the `config.cfg` file and configure the directories to point to the correct locations. Then start 

    doit

To start a render of the world.

### Advanced

Some `doit`-tasks allow subtasks to be run. Use

    doit render_biome:3

To render zoom-level 3 of the biome layer.

