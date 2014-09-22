#!/usr/bin/env python
import sys, os

from cx_Freeze import setup, Executable

import uristmaps

def add_dir_recursive(dirname):
    result = []
    for root, dirnames, filenames in os.walk(dirname):
        for filename in filenames:
            result.append((os.path.join(root, filename), os.path.join(root, filename)))
    return result

build_exe_options = {"packages" : ["uristmaps", "doit"],
                     "includes" : ["pkg_resources", "doit"],
                     "include_files" : ["dodo.py"] + add_dir_recursive("templates") + add_dir_recursive("res"),
                     "compressed" : True
                    }

base = None
if sys.platform == "win32":
    base = "Win32GUI"

setup(name="UristMaps",
      version=uristmaps.__version__,
      author="Dominik Schacht",
      author_email="domschacht@gmail.com",
      description="Map renderer for Dwarf Fortress worlds.",
      url="http://www.bitbucket.org/dominiks/uristmap",
      options={"build_exe" : build_exe_options},
      executables=[Executable("uristmaps/uristmaps.py", base=base)]
)

