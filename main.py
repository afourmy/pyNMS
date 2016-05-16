import sys
from inspect import getsourcefile
from os.path import abspath

# add path to the module in sys.path
path_app = abspath(getsourcefile(lambda: 0))[:-7]
if path_app not in sys.path:
    sys.path.append(path_app)

import gui
if __name__ == "__main__":
    netdim = gui.NetDim(path_app)
    netdim.mainloop()