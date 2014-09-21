import os, sys
import configparser

from doit import get_var

conf = configparser.ConfigParser()

conf_path = get_var("conf", "config.cfg")
if not os.path.exists(conf_path):
    print("Config file '{}' not found!".format(conf_path))
    sys.exit(1)

conf.read(conf_path)

