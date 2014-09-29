import os, sys
import configparser

from doit import get_var

conf = configparser.ConfigParser()
""" The path to the config file is usually read from
the application argument "conf=<file>" - this is done in the Try block.

When we are in a subprocess (especially in windows) this argument is not available
and get_var does not work properly. So when get_var fails we are (usually) in a
subprocess and the parent process has stored the conf path in a file ".<parent_pid>.txt"
so we use that to determine the conf path.

We use the parent_pid as the identifier for the file to allow multiple instances of
uristmaps to be running at the same time.

TODO: Delete the pidfile when done!

"""

try:
    conf_path = get_var("conf", "config.cfg")
except:
    # Reading conf path from pid file
    with open(".{}.txt".format(os.getppid())) as pidfile:
        conf_path = pidfile.read()

if not os.path.exists(conf_path):
    print("Config file '{}' not found!".format(conf_path))
    sys.exit(1)

conf.read(conf_path)
