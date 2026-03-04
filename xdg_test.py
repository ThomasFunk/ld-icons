#!/usr/bin/env python

import io
import os
import re
import configparser as ConfigParser

from xdg.BaseDirectory import xdg_config_home

config = ConfigParser.RawConfigParser(allow_no_value=True)

f = open(os.path.join(xdg_config_home, "user-dirs.dirs"))
user_config = "[XDG_USER_DIR]\n" + f.read()
f.close()
user_config = re.sub('\\$HOME', os.path.expanduser("~"), user_config)
user_config = re.sub('"', '', user_config)

config.read_file(io.StringIO(user_config))
print("XDG_USER_DIR: %s" % config.get("XDG_USER_DIR", "XDG_USER_DIR"))
print("XDG_PICTURES_DIR %s" % config.get("XDG_PICTURES_DIR", "XDG_PICTURES_DIR"))
#print(config.get("XDG_USER_DIR", "XDG_PICTURES_DIR"))