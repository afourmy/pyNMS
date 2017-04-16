# NetDim (contact@netdim.fr)

import tkinter as tk
import warnings
from project import Project
from collections import defaultdict
from os.path import abspath, pardir, join
from objects.objects import *
from pythonic_tkinter.preconfigured_widgets import *
from miscellaneous import search
from miscellaneous import graph_algorithms as galg
from miscellaneous import network_tree_view as ntv
from miscellaneous import debug
from ip_networks import ssh_management
from graph_generation import advanced_graph as adv_gr
from optical_networks import rwa_window as rwaw
from automation import script_creation
from menus import (
                   creation_menu, 
                   routing_menu,
                   display_menu, 
                   drawing_menu, 
                   view_menu
                   )
from PIL import ImageTk

class Controller(MainWindow):
    
    def __init__(self, path_app):
        super().__init__()
        self.path_app = path_app
        path_parent = abspath(join(path_app, pardir))
        self.path_icon = join(path_parent, 'Icons')
        self.path_workspace = join(path_parent, 'Workspace')
            
        ## ----- Initialization : -----
        self.title('NetDim')
        netdim_icon = tk.PhotoImage(file=join(self.path_icon, 'netdim_icon.gif'))
        self.tk.call('wm', 'iconphoto', self._w, netdim_icon)
        
        # dict of script (script name -> Script object)
        self.scripts = {}
        
        # project notebook
        self.project_notebook = Notebook(self)
        self.project_notebook.bind('<ButtonRelease-1>', self.change_current_project)
        
        # associate a project name to a Project object
        self.dict_project = {}
        # project counter
        self.cpt_project = 0
        
        ## ----- Persistent windows : -----
                
        # advanced graph options
        self.advanced_graph_options = galg.GraphAlgorithmWindow(self)
        
        # routing and wavelength assignment window
        self.rwa_window = rwaw.RWAWindow(self)
        
        # graph generation window
        self.advanced_graph = adv_gr.AdvancedGraph(self)
        
        # debug window
        self.debug_window = debug.Debug(self)
        
        # SSH management window
        self.ssh_management_window = ssh_management.SSHWindow(self)
        
        # Script creation window
        self.script_creation_window = script_creation.ScriptCreation(self)
        
        # Search window
        self.search_window = search.SearchWindow(self)

        # add the first project
        self.add_project()
        
        ## ----- Menus : -----
        
        netdim_menu = Menu(self)
        
        # general menu: 
        # - add / delete projects, 
        # - import / export projects, 
        # - exit the application
        
        general_menu = Menu(netdim_menu)
        
        add_project = MenuEntry(general_menu)
        add_project.text = 'Add project'
        add_project.command = self.add_project
        
        delete_project = MenuEntry(general_menu)
        delete_project.text = 'Delete project'
        delete_project.command = self.delete_project
        
        general_menu.separator()
        
        import_project = MenuEntry(general_menu)
        import_project.text = 'Import project'
        import_project.command = self.current_project.import_project
        
        export_project = MenuEntry(general_menu)
        export_project.text = 'Export project'
        export_project.command = self.current_project.export_project
        
        import_site = MenuEntry(general_menu)
        import_site.text = 'Import sites'
        import_site.command = self.current_project.import_site

        general_menu.separator()
        
        import_map = MenuEntry(general_menu)
        import_map.text = 'Import shapefile'
        import_map.command = self.current_project.current_view.import_shapefile
        
        delete_map = MenuEntry(general_menu)
        delete_map.text = 'Delete map'
        delete_map.command = self.current_project.current_view.delete_map
        
        general_menu.separator()
        
        debug_entry = MenuEntry(general_menu)
        debug_entry.text = 'Debug'
        debug_entry.command = self.debug_window.deiconify
        
        exit = MenuEntry(general_menu)
        exit.text = 'Exit'
        exit.command = self.destroy

        main_cascade = MenuCascade(netdim_menu)
        main_cascade.text = 'Main'
        main_cascade.inner_menu = general_menu
                
        # advanced menu:
        
        advanced_menu = Menu(netdim_menu)
        
        advanced_graph_entry = MenuEntry(advanced_menu)
        advanced_graph_entry.text = 'Advanced graph'
        advanced_graph_entry.command = self.advanced_graph.deiconify
        
        advanced_algorithms_entry = MenuEntry(advanced_menu)
        advanced_algorithms_entry.text = 'Advanced algorithms'
        advanced_algorithms_entry.command = self.advanced_graph_options.deiconify

        network_tree_view_entry = MenuEntry(advanced_menu)
        network_tree_view_entry.text = 'Network Tree View'
        network_tree_view_entry.command = lambda: ntv.NetworkTreeView(self)
        
        wavelenght_assignment_entry = MenuEntry(advanced_menu)
        wavelenght_assignment_entry.text = 'Wavelength assignment'
        wavelenght_assignment_entry.command = self.rwa_window.deiconify
        
        ssh_management_entry = MenuEntry(advanced_menu)
        ssh_management_entry.text = 'SSH connection management'
        ssh_management_entry.command = self.ssh_management_window.deiconify
        
        script_creation_entry = MenuEntry(advanced_menu)
        script_creation_entry.text = 'Script creation'
        script_creation_entry.command = self.script_creation_window.deiconify
        
        main_cascade = MenuCascade(netdim_menu)
        main_cascade.text = 'Network routing'
        main_cascade.inner_menu = advanced_menu

        # choose which label to display per type or subtype of object:
        # - a first menu contains all types of objects, each type unfolding
        # a sub-menu that contains all i/e properties common to a type
        # - a second menu contains all types of objects, each type unfolding
        # a sub-menu that contains all i/e properties common to a subtypes
        
        per_type_label_menu = Menu(netdim_menu)
        for obj_type, labels in type_labels.items():
            menu_type = Menu(netdim_menu)
            entry_name = '{type} label'.format(type=type_to_name[obj_type])
            per_type_label_menu.add_cascade(label=entry_name, menu=menu_type)
            for label in labels:
                def update_label(o=obj_type, l=label):
                    self.current_project.current_view.refresh_type_labels(o, l)
                type_entry = MenuEntry(menu_type)
                type_entry.text = prop_to_name[label]
                type_entry.command = update_label
                    
        per_type_cascade = MenuCascade(netdim_menu)
        per_type_cascade.text = 'Per-type labels'
        per_type_cascade.inner_menu = per_type_label_menu
        
        self.config(menu=netdim_menu)
        
        ## Images
        
        # dict of nodes image for node creation
        self.dict_image = defaultdict(dict)
        self.dict_pil = defaultdict(dict)
                
        for color in ('default', 'red', 'purple'):
            for node_type in node_subtype:
                obj_class = node_class[node_type]
                x, y = obj_class.imagex, obj_class.imagey
                img_path = join(self.path_icon, ''.join((
                                                        color, 
                                                        '_', 
                                                        node_type, 
                                                        '.gif'
                                                        ))
                                )
                img_pil = ImageTk.Image.open(img_path).resize((x, y))
                img = ImageTk.PhotoImage(img_pil)
                self.dict_image[color][node_type] = img
                self.dict_pil[color][node_type] = img_pil
                
        # image for a link failure
        img_pil = ImageTk.Image.open(join(
                                          self.path_icon, 
                                          'failure.png'
                                          )
                                    ).resize((20, 20))
        self.img_failure = ImageTk.PhotoImage(img_pil)
        
        self.menu_notebook = Notebook(self)
        
        # main menu for creation and selection of objects
        self.creation_menu = creation_menu.CreationMenu(self.menu_notebook, self)
        self.creation_menu.pack()
    
        # routing menu (addresss allocation + tables creation + routing)
        self.routing_menu = routing_menu.RoutingMenu(self.menu_notebook, self)
        self.routing_menu.pack()
        
        # drawing menu (force-based algorithm parameters + paint-like drawing)
        self.drawing_menu = drawing_menu.DrawingMenu(self.menu_notebook, self)
        self.drawing_menu.pack()
        
        # display menu to control the display
        self.display_menu = display_menu.DisplayMenu(self.menu_notebook, self)
        self.display_menu.pack()
        
        # display menu to control the display
        self.view_menu = view_menu.ViewMenu(self.menu_notebook, self)
        self.view_menu.pack()
        
        self.menu_notebook.add(self.creation_menu, text=' Creation ')
        self.menu_notebook.add(self.routing_menu, text=' Routing ')
        self.menu_notebook.add(self.drawing_menu, text=' Drawing ')
        self.menu_notebook.add(self.display_menu, text=' Display ')
        self.menu_notebook.add(self.view_menu, text=' View ')
        
        self.menu_notebook.pack(side='left', fill='both')
        
        # notebooks of projects
        self.project_notebook.pack(side='left', fill='both', expand=1)
            
    def change_current_project(self, event=None):
        # if there's an ongoing drawing process, kill it
        self.current_project.current_view.cancel()
        name = self.project_notebook.tab(self.project_notebook.select(), 'text')
        self.current_project = self.dict_project[name]
        
    def add_project(self, name=None):
        self.cpt_project += 1
        if not name:
            name = ' '.join(('project', str(self.cpt_project)))
        new_project = Project(self, name)
        self.project_notebook.add(new_project.gf, text=name, compound='top')
        self.dict_project[name] = new_project
        return new_project
        
    def delete_project(self):
        del self.dict_project[self.current_project.name]
        self.project_notebook.forget(self.current_project)
        self.change_current_project()
                            