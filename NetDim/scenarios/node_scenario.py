# NetDim
# Copyright (C) 2017 Antoine Fourmy (contact@netdim.fr)

from .scenario import Scenario

class NodeScenario(Scenario):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)