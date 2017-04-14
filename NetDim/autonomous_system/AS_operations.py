from .AS import AS_subtypes
from pythonic_tkinter.preconfigured_widgets import *
from miscellaneous.decorators import update_paths

class AreaOperation(CustomTopLevel):
    
    # Add objects to an area, or remove objects from an area
    
    @update_paths
    # controller is initialized to None, because it must be the last argument
    # of args for the sake of updating all paths with @update_paths
    def __init__(self, mode, obj, AS=set(), controller=None):
        super().__init__()
        
        title = 'Add to area' if mode == 'add' else 'Remove from area'
        
        # main label frame
        lf_area_operation = Labelframe(self)
        lf_area_operation.text = title
        lf_area_operation.grid(0, 0)
        
        self.title(title)

        values = tuple(map(str, AS))
        
        # List of existing AS
        self.AS_list = Combobox(self, width=15)
        self.AS_list['values'] = values
        self.AS_list.current(0)
        self.AS_list.bind('<<ComboboxSelected>>', lambda e: self.update_value())
        
        self.area_list = Combobox(self, width=15)
        self.update_value()
        self.area_list.current(0)

        button_area_operation = Button(self)
        button_area_operation.text = 'OK'
        button_area_operation.command = lambda: self.area_operation(mode, *obj)
        
        self.AS_list.grid(0, 0, in_=lf_area_operation)
        self.area_list.grid(1, 0, in_=lf_area_operation)
        button_area_operation.grid(2, 0, in_=lf_area_operation)
        
    def update_value(self):
        selected_AS = self.network.AS_factory(name=self.AS_list.get())
        self.area_list['values'] = tuple(map(str, selected_AS.areas))
        
    def area_operation(self, mode, *objects):
        selected_AS = self.network.AS_factory(name=self.AS_list.get())
        selected_area = self.area_list.get()

        if mode == 'add':
            selected_AS.management.add_to_area(selected_area, *objects)
        else:
            selected_AS.management.remove_from_area(selected_area, *objects)
            
        self.destroy()
        
class ASOperation(CustomTopLevel):
    
    # Add objects to an AS, or remove objects from an AS
    
    @update_paths
    # controller is initialized to None, because it must be the last argument
    # of args for the sake of updating all paths with @update_paths
    def __init__(self, mode, obj, AS=set(), controller=None):
        super().__init__()
        
        title = {
        'add': 'Add to AS',
        'remove': 'Remove from AS',
        'manage': 'Manage AS'
        }[mode]
        
        # main label frame
        lf_AS_operation = Labelframe(self)
        lf_AS_operation.text = title
        lf_AS_operation.grid(0, 0)
        
        self.title(title)
        
        if mode == 'add':
            # All AS are proposed 
            values = tuple(map(str, self.network.pnAS))
        else:
            # Only the common AS among all selected objects
            values = tuple(map(str, AS))
        
        # List of existing AS
        self.AS_list = Combobox(self, width=15)
        self.AS_list['values'] = values
        self.AS_list.current(0)

        button_AS_operation = Button(self)
        button_AS_operation.text = 'OK'
        button_AS_operation.command = lambda: self.as_operation(mode, *obj)
        
        self.AS_list.grid(0, 0, 1, 2, in_=lf_AS_operation)
        button_AS_operation.grid(1, 0, 1, 2, in_=lf_AS_operation)
        
    def as_operation(self, mode, *objects):
        selected_AS = self.network.AS_factory(name=self.AS_list.get())

        if mode == 'add':
            selected_AS.management.add_to_AS(*objects)
        elif mode == 'remove':
            selected_AS.management.remove_from_AS(*objects)
        else:
            selected_AS.management.deiconify()
            
        self.destroy()
        
class ASCreation(CustomTopLevel):
    
    @update_paths
    def __init__(self, nodes, links, controller):
        super().__init__()
        self.title('Create AS')
        
        # main label frame
        lf_create_AS = Labelframe(self)
        lf_create_AS.text = 'Create AS'
        lf_create_AS.grid(0, 0)
        
        # List of AS type
        self.AS_type_list = Combobox(self, width=10)
        self.AS_type_list['values'] = AS_subtypes
        self.AS_type_list.current(0)

        # retrieve and save node data
        button_create_AS = Button(self)
        button_create_AS.text = 'Create AS'
        button_create_AS.command = lambda: self.create_AS(nodes, links)
                        
        # Label for the name/type of the AS
        label_name = Label(self)
        label_name.text = 'Name'
        
        label_type = Label(self)
        label_type.text = 'Type'
        
        label_id = Label(self)
        label_id.text = 'ID'
        
        # Entry box for the name of the AS
        self.entry_name  = Entry(self, width=13)
        self.entry_id  = Entry(self, width=13)
        
        label_name.grid(0, 0, in_=lf_create_AS)
        label_id.grid(1, 0, in_=lf_create_AS)
        self.entry_name.grid(0, 1, in_=lf_create_AS)
        self.entry_id.grid(1, 1, in_=lf_create_AS)
        label_type.grid(2, 0, in_=lf_create_AS)
        self.AS_type_list.grid(2, 1, in_=lf_create_AS)
        button_create_AS.grid(3, 0, 1, 2, in_=lf_create_AS)

    def create_AS(self, nodes, links):
        # automatic initialization of the AS id in case it is empty
        id = int(self.entry_id.get()) if self.entry_id.get() else len(self.network.pnAS) + 1
        
        new_AS = self.network.AS_factory(
                                         self.AS_type_list.get(), 
                                         self.entry_name.get(), 
                                         id,
                                         links, 
                                         nodes
                                         )
        self.destroy()
            