# NetDim (contact@netdim.fr)

from menus.network_selection_rightclick_menu import NetworkSelectionRightClickMenu
from miscellaneous.decorators import update_paths
from pythonic_tkinter.preconfigured_widgets import *
from objects.objects import *

class NetworkTreeView(CustomTopLevel):

    @update_paths
    def __init__(self, controller):
        super().__init__()
        self.geometry('1200x500')
        self.title('Network Tree View')
        # TODO add AS property too, botrh in manage AS and here
        self.ntv = Treeview(self)
        n = max(map(len, object_ie.values()))

        self.ntv['columns'] = tuple(map(str, range(n)))
        for i in range(n):
            self.ntv.column(str(i), width=100)
            
        # object selection in the treeview
        self.ntv.bind('<ButtonRelease-1>', lambda e: self.select(e))
        # right-click menu
        self.ntv.bind('<ButtonPress-3>', lambda e: NetworkSelectionRightClickMenu(e, self.view, False))
        
        for obj_subtype, properties in object_ie.items():
            obj_type = subtype_to_type[obj_subtype]
            if tuple(self.network.ftr(obj_type, obj_subtype)):
                properties = ('type',) + properties
                self.ntv.insert('', 'end', obj_subtype, text=obj_subtype.title(), 
                                                                values=properties)
            for obj in self.network.ftr(obj_type, obj_subtype):
                values = tuple(map(lambda p: getattr(obj, p), properties))
                iid = self.ntv.insert(obj_subtype, 'end', text=obj.name, values=values)
                self.ntv.item(iid, tags=obj_type)
        
        self.ntv.pack(expand='yes', fill='both')
        
        self.deiconify()
        
    def select(self, event):
        print('before' + str(self.view.so))
        self.view.unhighlight_all()
        for item in self.ntv.selection():
            tags = self.ntv.item(item, 'tags')
            if tags:
                obj_type ,= tags
                item = self.ntv.item(item)
                obj = self.network.pn[obj_type][self.network.name_to_id[item['text']]]
                self.view.highlight_objects(obj)
        print('after' + str(self.view.so))