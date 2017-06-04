# NetDim (contact@netdim.fr)

from miscellaneous.decorators import update_paths
from pythonic_tkinter.preconfigured_widgets import *
from objects.objects import *

class NetworkDimension(CustomTopLevel):  

    @update_paths
    def __init__(self, type, controller):
        super().__init__()
        self.title('Dimension')
        self.type = type
        
        # main label frame
        lf_network_dimension = Labelframe(self)
        lf_network_dimension.text = 'Dimension'
        lf_network_dimension.grid(0, 0)
        
        self.dict_type_to_function = {
        'star': lambda n, st: self.network.star(n - 1, st),
        'ring': lambda n, st: self.network.ring(n, st),
        'full-mesh': lambda n, st: self.network.full_mesh(n, st),
        'tree': lambda n, st: self.network.tree(n, st),
        'square-tiling': lambda n, st: self.network.square_tiling(n + 1, st),
        'hypercube': lambda n, st: self.network.hypercube(n - 1, st),
        'kneser': lambda n, k, st: self.network.kneser(n+1, k, st),
        'petersen': lambda n, k, st: self.network.petersen(n, k, st)
        }
        
        # offset used to add the addition 'k' parameter in the gui
        self.offset = type in ('kneser', 'petersen')
    
        # Network dimension
        dimension = Label(self)
        if type == 'tree':
            dimension.text = 'Depth of the tree'
        elif self.offset:
            dimension.text = 'N'
        elif type in ('square-tiling', 'hypercube'):
            dimension.text = 'Dimension'
        else:
            dimension.text = 'Number of nodes'
            
        if self.offset:
            k = Label(self)
            k.text = 'K'
            self.entry_k = Entry(self, width=9)
            k.grid(1, 0, in_=lf_network_dimension)
            self.entry_k.grid(1, 1, in_=lf_network_dimension)
            
        self.entry_dimension = Entry(self, width=9)
        
        # List of node type
        node_type = Label(self)
        node_type.text = 'Type of node'
        self.node_type_list = Combobox(self, width=7)
        self.node_type_list['values'] = node_subtype
        self.node_type_list.current(0)
    
        # confirmation button
        button_OK = Button(self)
        button_OK.text = 'OK'
        button_OK.command = lambda: self.create_graph()
        
        # position in the grid
        dimension.grid(0, 0, in_=lf_network_dimension)
        self.entry_dimension.grid(0, 1, in_=lf_network_dimension)
        node_type.grid(1 + self.offset, 0, in_=lf_network_dimension)
        self.node_type_list.grid(1 + self.offset, 1, in_=lf_network_dimension)
        button_OK.grid(2, 0, 1, 2, sticky='ew', in_=lf_network_dimension)
                                                        
    def create_graph(self):
        if self.offset:
            params = (
                      int(self.entry_dimension.text),
                      int(self.entry_k.get()),
                      self.node_type_list.text
                      )
        else:
            params = (
                      int(self.entry_dimension.get()),
                      self.node_type_list.text
                      )

        objects = set(self.dict_type_to_function[self.type](*params))
        self.view.draw_objects(objects, random=False)
        self.view.move_nodes(filter(lambda o: o.class_type == 'node', objects))
        self.destroy()