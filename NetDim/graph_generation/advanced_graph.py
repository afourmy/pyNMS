# NetDim
# Copyright (C) 2017 Antoine Fourmy (contact@netdim.fr)
# Released under the GNU General Public License GPLv3

from pythonic_tkinter.preconfigured_widgets import *
from os.path import join
from PIL import ImageTk
from graph_generation.network_dimension import NetworkDimension

class AdvancedGraph(FocusTopLevel):
    
    def __init__(self, master):
        
        self.ms = master
        super().__init__()
        font = ('Helvetica', 8, 'bold')
        
        images = (
        ('square-tiling', (100, 100)),
        ('hypercube', (100, 100)),
        ('kneser', (100, 100)),
        ('petersen', (100, 100))
        )

        self.dict_images = {}
        
        for image_type, image_size in images:
            img_path = join(self.ms.path_icon, image_type + '.png')
            img_pil = ImageTk.Image.open(img_path).resize(image_size)
            img = ImageTk.PhotoImage(img_pil)
            self.dict_images[image_type] = img
            
        button_config = (
        ('square-tiling', (0, 0), 'Square tiling'),
        ('hypercube', (0, 1), 'Hypercube'),
        ('kneser', (1, 0), 'Kneser'),
        ('petersen', (1, 1), 'Petersen')
        )
        
        # label frame for the infinite graph generation button
        lf_inf_graph = Labelframe(self)
        lf_inf_graph.text = 'Infinite graph generation'
        lf_inf_graph.grid(1, 0, 1, 2)
                                                        
        for bt_type, (row, col), bt_text in button_config:
            bt = TKButton(self)
            bt.text = bt_text
            bt.command = lambda t=bt_type: NetworkDimension(self.ms.cs, t)
            
            bt.grid(row, col, in_=lf_inf_graph)
            bt.config(image=self.dict_images[bt_type], compound='top', font=font)
                                                        
        lf_classic_graph = Labelframe(self)
        lf_classic_graph.text = 'Classic graph generation'
        lf_classic_graph.grid(1, 3, 1, 2)
                                        
        self.graph_properties = {
        'Desargues': (3, 4, 2),
        'graph-test': (4, 5, 4)
        }
        
        # List of classic graphs
        self.graph_list = Combobox(self, width=9)
        self.graph_list['values'] = tuple(self.graph_properties.keys())
        self.graph_list.current(0)
        self.graph_list.grid(0, 0, 1, 2, in_=lf_classic_graph)
        self.graph_list.bind('<<ComboboxSelected>>', lambda e: self.update_properties())
                                        
        
        properties = (
        'Number of nodes :',
        'Number of links :',
        'Chromatic number :'
        )
        
        self.var_labels = []
        
        for idx, property in enumerate(properties, 1):
            
            label_property = Label(self)
            label_property.text = property
            label_property.grid(idx, 0, in_=lf_classic_graph)

            label_value = Label(self, width=3)
            label_value.grid(idx, 1, in_=lf_classic_graph)
            self.var_labels.append(label_value)
            
        bt_gen = Button(self)
        bt_gen.text = 'Generate'
        bt_gen.command = self.generate
        bt_gen.grid(len(properties)+1, 0, 1, 2, in_=lf_classic_graph)
                                        
        self.graph_generation = {
        'Desargues': lambda: self.ms.cs.ntw.petersen(5, 2, 'oxc'),
        'graph-test': lambda: self.ms.cs.ntw.petersen(6, 3, 'router')
        }
            
        self.update_properties()
        # hide the window when closed
        self.protocol('WM_DELETE_WINDOW', self.withdraw)
        self.withdraw()
                                        
    # when a graph is selected, the properties are updated accordingly
    def update_properties(self):
        selected_graph = self.graph_list.text
        for idx, value in enumerate(self.graph_properties[selected_graph]):
            self.var_labels[idx].configure(text=value)
            
    def generate(self):
        selected_graph = self.graph_list.text
        self.graph_generation[selected_graph]()
        self.ms.cs.draw_all(random=False)