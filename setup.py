#!/usr/bin/env python

from setuptools import setup

setup(name="UristMaps",
      version="0.1",
      author="Dominik Schacht",
      author_email="domschacht@gmail.com",
      description="Map renderer for Dwarf Fortress worlds.",
      url="http://www.bitbucket.org/dominiks/uristmap",
      install_requires=["pillow",        # Image processing
                        "cairocffi",     # Drawing tile images
                        "clint",         # Pretty cli output
                        "doit",          # Quick management of tasks and execution order
                        "lxml",          # Better xml performance for bs4
                        "beautifulsoup4" # Processing xml
     ]
)

