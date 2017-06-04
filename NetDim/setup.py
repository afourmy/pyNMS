# NetDim (contact@netdim.fr)

import sys
from inspect import stack
from os.path import abspath, dirname
from cx_Freeze import setup, Executable

# prevent python from writing *.pyc files / __pycache__ folders
sys.dont_write_bytecode = True

path_app = dirname(abspath(stack()[0][1]))

if path_app not in sys.path:
    sys.path.append(path_app)
        
build_options = dict(
                     compressed = True,
                     path = sys.path + [path_app]
                     )

setup(
      name = 'NetDim',
      version = '0.1',
      description = 'Netdim - a multi-layer network planning software',
      options = dict(build_exe=build_options),
      executables = [Executable('main.py')],
      )