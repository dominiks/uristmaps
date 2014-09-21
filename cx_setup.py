#!/usr/bin/env python
import sys

from cx_Freeze import setup, Executable

import uristmaps

build_exe_options = {"packages" : ["uristmaps", "doit"],
                     "includes" : ["pkg_resources", "doit"],
                     "include_files" : ["dodo.py"],
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

