# NetDim (contact@netdim.fr)

from miscellaneous.decorators import update_paths
from pythonic_tkinter.preconfigured_widgets import *
from objects.objects import *

class MultipleNodes(CustomTopLevel):  

    @update_paths
    def __init__(self, x, y, controller):
        super().__init__()
        self.x = x
        self.y = y
        self.title('Multiple nodes')
        
        # label frame for multiple nodes creation
        lf_multiple_nodes = Labelframe(self)
        lf_multiple_nodes.text = 'Creation of multiple nodes'
        lf_multiple_nodes.grid(0, 0)
        
        nb_nodes = Label(self)
        nb_nodes.text = 'Number of nodes'
        self.entry_nodes = Entry(self, width=4)
        
        # List of node type
        node_type = Label(self)
        node_type.text = 'Type of node'
        self.node_type_list = Combobox(self, width=7)
        self.node_type_list['values'] = node_subtype
        self.node_type_list.current(0)
    
        # confirmation button
        button_confirmation = Button(self)
        button_confirmation.text = 'OK'
        button_confirmation.command = self.create_nodes
        
        # position in the grid
        nb_nodes.grid(0, 0, in_=lf_multiple_nodes)
        self.entry_nodes.grid(0, 1, in_=lf_multiple_nodes)
        node_type.grid(1, 0, in_=lf_multiple_nodes)
        self.node_type_list.grid(1, 1, in_=lf_multiple_nodes)
        button_confirmation.grid(2, 0, 1, 2, in_=lf_multiple_nodes)
        
    def create_nodes(self):
        self.view.multiple_nodes(
                               int(self.entry_nodes.text), 
                               self.node_type_list.text,
                               self.x,
                               self.y
                               )
        
        self.view.draw_all(random=False)
        self.destroy()
        
class MultipleLinks(CustomTopLevel): 

    @update_paths
    def __init__(self, source_nodes, controller):
        super().__init__()
        self.source_nodes = source_nodes
        self.title('Multiple links')
        
        # label frame for multiple links creation
        lf_multiple_links = Labelframe(self)
        lf_multiple_links.text = 'Creation of multiple links'
        lf_multiple_links.grid(0, 0)
        
        dest_nodes = Label(self)
        dest_nodes.text = 'Destination nodes :'

        self.listbox = ObjectListbox(self, width=15, height=7)
        yscroll = Scrollbar(self)
        yscroll.command = self.listbox.yview
        self.listbox.configure(yscrollcommand=yscroll.set)
        self.listbox.grid(1, 0, in_=lf_multiple_links)
        yscroll.grid(1, 1, in_=lf_multiple_links)
        
        # add all nodes of the view to the listbox
        for node in self.network.nodes.values():
            self.listbox.insert(node.name)
    
        # confirmation button
        button_confirmation = Button(self)
        button_confirmation.text = 'OK',
        button_confirmation.command = lambda: self.create_links(source_nodes)
        
        # position in the grid
        dest_nodes.grid(0, 0, in_=lf_multiple_links)
        button_confirmation.grid(2, 0, 1, 2, in_=lf_multiple_links)
        
    def create_links(self):
        for selected_node in self.listbox.selected():
            # retrieve the node object based on its name
            dest_node = self.network.nf(name=selected_node)
            # create links from all selected nodes to the selected node
            self.network.multiple_links(self.source_nodes, dest_node)
        
        self.view.draw_all(random=False)
        self.destroy()