import tkinter as tk

class NodeManagement(tk.Toplevel):
    def __init__(self, master):
        super().__init__()
        self.geometry("190x140")
        self.title("Manage node properties")
        
        # this allows to change the behavior of closing the window. 
        # I don't want the window to be destroyed, simply hidden
        self.protocol("WM_DELETE_WINDOW", self.withdraw)
        
        # current node which properties are displayed
        self.current_node = None
        
        # retrieve and save node data
        self.button_select_node = tk.Button(self, text="Select node", command=lambda: self.select_node(master))
        self.button_save_node = tk.Button(self, text="Save node", command=lambda: self.save_node(master))
        
        # Label for name and position
        self.label_name = tk.Label(self, text = "Name")
        self.label_x = tk.Label(self, text = "Position x")
        self.label_y = tk.Label(self, text = "Position y")
        
        # Entry boxes and textvar for all parameters
        self.var_name = tk.StringVar()
        self.var_x = tk.StringVar()
        self.var_y = tk.StringVar()
        self.var_name.set("")
        self.var_x.set("")
        self.var_y.set("")
        
        self.entry_name  = tk.Entry(self, textvariable=self.var_name, width=15)
        self.entry_x = tk.Entry(self, textvariable=self.var_x, width=15)
        self.entry_y = tk.Entry(self, textvariable=self.var_y, width=15)
        
        self.label_name.grid(row=0, column=0, pady=5, padx=5, sticky=tk.W)
        self.label_x.grid(row=1, column=0, pady=5, padx=5, sticky=tk.W)
        self.label_y.grid(row=2, column=0, pady=5, padx=5, sticky=tk.W)
        
        self.entry_name.grid(row=0, column=1, sticky=tk.W)
        self.entry_x.grid(row=1, column=1, sticky=tk.W)
        self.entry_y.grid(row=2, column=1, sticky=tk.W)
    
        self.button_select_node.grid(row=5,column=0, pady=5, padx=5, sticky=tk.W)
        self.button_save_node.grid(row=5,column=1, pady=5, padx=5, sticky=tk.W)
        
        self.withdraw()
        
    def select_node(self, master):
        self.current_node = master.current_scenario.node_factory(self.var_name.get())
        self.update()
        
    # when there is no current node, get it by the name with select
    # update the current nodes properties with whatever the user entered
    def save_node(self, master):
        if not self.current_node:
            self.select_node(master)
        self.current_node.x = int(self.var_x.get())
        self.current_node.y = int(self.var_y.get())
        # self.update() # useless ?
        # move the node on the canvas once it's coordinates were updated
        self.master.current_scenario.move_node(self.current_node)
        
    # update the entry widgets
    def update(self):
        # I put int because coordinates are not always integer
        self.var_name.set(self.current_node.name)
        self.var_x.set(str(int(self.current_node.x)))
        self.var_y.set(str(int(self.current_node.y)))
        
class LinkManagement(tk.Toplevel):
    def __init__(self, master):
        super().__init__()
        self.geometry("290x230")
        self.title("Manage link properties")
        
        # current link which properties are displayed
        self.current_link = None
        
        # retrieve and save link data
        self.button_select_link = tk.Button(self, text="Select link", command=lambda: self.select_link(master))
        self.button_save_link = tk.Button(self, text="Save link", command=lambda: self.save_link(master))
        
        # this allows to change the behavior of closing the window. 
        # I don't want the window to be destroyed, simply hidden
        self.protocol("WM_DELETE_WINDOW", self.withdraw)
        
        # Label for name, source, destination, excluded links/links and path constraints
        self.label_name = tk.Label(self, text = "Name")
        self.label_source_node = tk.Label(self, text = "Source node")
        self.label_destination_node = tk.Label(self, text = "Destination node")
        self.label_capacitySD = tk.Label(self, text = "Capacity source -> destination")
        self.label_capacityDS = tk.Label(self, text = "Capacity destination -> source")
        self.label_cost = tk.Label(self, text = "Cost")
        
        # Entry boxes and textvar for all parameters / constraints
        self.var_name = tk.StringVar()
        self.var_source_node = tk.StringVar()
        self.var_destination_node = tk.StringVar()
        self.var_capacitySD = tk.StringVar()
        self.var_capacityDS = tk.StringVar()
        self.var_cost = tk.StringVar()

        self.entry_name  = tk.Entry(self, textvariable=self.var_name, width=15)
        self.entry_source_node  = tk.Entry(self, textvariable=self.var_source_node, width=15)
        self.entry_destination_node = tk.Entry(self, textvariable=self.var_destination_node, width=15)
        self.entry_capacitySD = tk.Entry(self, textvariable=self.var_capacitySD, width=15)
        self.entry_capacityDS = tk.Entry(self, textvariable=self.var_capacityDS, width=15)
        self.entry_cost = tk.Entry(self, text=self.var_cost, width=15)
        
        self.label_name.grid(row=0, column=0, pady=5, padx=5, sticky=tk.W)
        self.label_source_node.grid(row=1, column=0, pady=5, padx=5, sticky=tk.W)
        self.label_destination_node.grid(row=2, column=0, pady=5, padx=5, sticky=tk.W)
        self.label_capacitySD.grid(row=3, column=0, pady=5, padx=5, sticky=tk.W)
        self.label_capacityDS.grid(row=4, column=0, pady=5, padx=5, sticky=tk.W)
        self.label_cost.grid(row=5, column=0, pady=5, padx=5, sticky=tk.W)
        
        self.entry_name.grid(row=0, column=1, sticky=tk.W)
        self.entry_source_node.grid(row=1, column=1, sticky=tk.W)
        self.entry_destination_node.grid(row=2, column=1, sticky=tk.W)
        self.entry_capacitySD.grid(row=3, column=1, sticky=tk.W)
        self.entry_capacityDS.grid(row=4, column=1, sticky=tk.W)
        self.entry_cost.grid(row=5, column=1, sticky=tk.W)
    
        self.button_select_link.grid(row=6,column=0, pady=5, padx=5, sticky=tk.W)
        self.button_save_link.grid(row=6,column=1, pady=5, padx=5, sticky=tk.W)
        
        self.withdraw()
        
    def select_link(self, master):
        link_name = self.var_name.get()
        self.current_link = master.current_scenario.link_factory(name=link_name)
        self.update()
            
    def save_link(self, master):
        if(not self.current_link):
            link_name = self.var_name.get()
            self.current_link = master.current_scenario.link_factory(name=link_name)
        self.current_link.capacity["SD"] = int(self.var_capacitySD.get())
        self.current_link.capacity["DS"] = int(self.var_capacityDS.get())
        self.current_link.cost = int(self.var_cost.get())
        # refresh label for current link
        master.current_scenario._refresh_link_label(self.current_link)
        
    def update(self):
        self.var_name.set(self.current_link.name)
        self.var_source_node.set(str(self.current_link.source))
        self.var_destination_node.set(str(self.current_link.destination))
        self.var_capacitySD.set(str(self.current_link.capacity["SD"]))
        self.var_capacityDS.set(str(self.current_link.capacity["DS"]))
        self.var_cost.set(str(self.current_link.cost))