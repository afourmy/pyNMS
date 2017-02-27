# NetDim
# Copyright (C) 2017 Antoine Fourmy (contact@netdim.fr)
# Released under the GNU General Public License GPLv3

import sys
from inspect import stack
from os.path import abspath, dirname

# prevent python from writing *.pyc files / __pycache__ folders
sys.dont_write_bytecode = True

path_app = dirname(abspath(stack()[0][1]))

if path_app not in sys.path:
    sys.path.append(path_app)

import gui

if str.__eq__(__name__, '__main__'):
    netdim = gui.NetDim(path_app)
    netdim.mainloop()