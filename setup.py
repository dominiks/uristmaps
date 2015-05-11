#!/usr/bin/env python

from setuptools import setup

import uristmaps

setup(name="UristMaps",
      version=uristmaps.__version__,
      author="Dominik Schacht",
      author_email="domschacht@gmail.com",
      description="Map renderer for Dwarf Fortress worlds.",
      url="http://www.bitbucket.org/dominiks/uristmap",
      install_requires=["pillow",         # Image processing
                        "clint",          # Pretty cli output
                        "doit",           # Quick management of tasks and execution order
                        "Jinja2",          # Rendering html files
     ]
)

