# NetDim
# Copyright (C) 2016 Antoine Fourmy (antoine.fourmy@gmail.com)
# Released under the GNU General Public License GPLv3

import sys
from inspect import getsourcefile
from os.path import abspath

# prevent python from writing *.pyc files / __pycache__ folders
sys.dont_write_bytecode = True

path_app = abspath(getsourcefile(lambda: 0))[:-7]
if path_app not in sys.path:
    sys.path.append(path_app)

import gui

if __name__ == "__main__":
    netdim = gui.NetDim(path_app)
    netdim.mainloop()