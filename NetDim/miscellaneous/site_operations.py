# NetDim (contact@netdim.fr)

from pythonic_tkinter.preconfigured_widgets import *

class SiteOperations(CustomTopLevel):
    
    # Add objects to an AS, or remove objects from an AS
    
    def __init__(self, view, mode, obj, sites=set()):
        super().__init__()
        
        title = {
        'add': 'Add to site',
        'remove': 'Remove from site'
        }[mode]
        
        # main label frame
        lf_site_operation = Labelframe(self)
        lf_site_operation.text = title
        lf_site_operation.grid(0, 0)
        
        self.title(title)
        
        if mode == 'add':
            # All sites are proposed 
            values = tuple(view.ms.ss.ntw.nodes.values())
        else:
            # Only the common sites among all selected objects
            values = tuple(map(str, sites))
        
        # List of existing AS
        self.site_list = Combobox(self, width=15)
        self.site_list['values'] = values
        self.site_list.current(0)

        button_OK = Button(self)
        button_OK.text = 'OK'
        button_OK.command = lambda: self.site_operation(view, mode, *obj)
        
        self.site_list.grid(0, 0, 1, 2, in_=lf_site_operation)
        button_OK.grid(1, 0, 1, 2, in_=lf_site_operation)
        
    def site_operation(self, view, mode, *objects):
        site_id = view.ms.ss.ntw.name_to_id[self.site_list.text]
        selected_site = view.ms.ss.ntw.pn['node'][site_id]

        if mode == 'add':
            selected_site.add_to_site(*objects)
        else: 
            # mode is 'remove'
            selected_site.remove_from_site(*objects)
            
        self.destroy()