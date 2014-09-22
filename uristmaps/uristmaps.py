#! /usr/bin/env python3
""" This file is a copy of doit/__main__.py which is the normal entry point
of doit. This replicates the behaviour of doit but makes it easier accessible
for cx_Freeze.
"""
from multiprocessing import freeze_support

def main():
    # Fixes issues with multiprocessing with cx_freeze on windows
    freeze_support()
    """ Start doit.
    """
    import sys
    from doit.doit_cmd import DoitMain
    sys.exit(DoitMain().run(sys.argv[1:]))

if __name__ == '__main__':
    main()

