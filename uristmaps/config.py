import configparser

from doit import get_var

conf = configparser.ConfigParser()
conf.read(get_var("conf", "config.cfg"))

