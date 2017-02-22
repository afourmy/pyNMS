import sys
from cx_Freeze import setup, Executable
from inspect import getsourcefile
from os.path import abspath

# prevent python from writing *.pyc files / __pycache__ folders
sys.dont_write_bytecode = True

path_app = abspath(getsourcefile(lambda: _))[:-8]
    
import autonomous_system
    
build_options=dict(
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