import tkinter as tk
from tkinter import ttk

class MainFrame(tk.Frame):
    
    def __init__(self, master):
        super().__init__(width=200,height=600, borderwidth=1, relief="solid", background="#A1DBCD")
        self.bg_color = "#E6E6FA"
        self.type_to_button = {}

        # choix du mode: motion / node creation / link creation
        self.motion_mode = tk.Button(self, bg="#A1DBCD", text="Motion mode", width=200, height=200, relief=tk.FLAT, command=lambda: self.switch_to_motion(master))
        self.creation_mode = tk.Button(self, bg="#A1DBCD", text ="Creation mode", width=200, height=200, relief=tk.FLAT, command=lambda: self.switch_to_creation(master))
        
        self.create_router = tk.Button(self, bg="#A1DBCD", height=45, width=45, relief=tk.FLAT, command=lambda: self.change_creation_mode(master, "router"))
        self.type_to_button["router"] = self.create_router
        
        self.create_oxc = tk.Button(self, bg="#A1DBCD", height=45, width=45, relief=tk.FLAT, command=lambda: self.change_creation_mode(master, "oxc"))
        self.type_to_button["oxc"] = self.create_oxc
        
        self.create_host = tk.Button(self, bg="#A1DBCD", height=45, width=45, relief=tk.FLAT, command=lambda: self.change_creation_mode(master, "host"))
        self.type_to_button["host"] = self.create_host
        
        self.create_antenna = tk.Button(self, bg="#A1DBCD", height=45, width=45, relief=tk.FLAT, command=lambda: self.change_creation_mode(master, "antenna"))
        self.type_to_button["antenna"] = self.create_antenna
        
        self.create_trunk = tk.Button(self, bg="#A1DBCD", text ="Create trunk", fg="blue", font=("Courier", 8, "bold"), compound="top", relief=tk.FLAT, command=lambda: self.change_creation_mode(master, "trunk"))
        self.type_to_button["trunk"] = self.create_trunk
        
        self.create_route = tk.Button(self, bg="#A1DBCD", text ="Create route", fg="green", font=("Courier", 8, "bold"), compound="top", relief=tk.FLAT, command=lambda: self.change_creation_mode(master, "route"))
        self.type_to_button["route"] = self.create_route
        
        self.create_traffic = tk.Button(self, bg="#A1DBCD", text ="Create traffic", fg="purple", font=("Courier", 8, "bold"), compound="top", relief=tk.FLAT, command=lambda: self.change_creation_mode(master, "traffic"))
        self.type_to_button["traffic"] = self.create_traffic
        
        # drawing du graphe
        self.draw_graph = tk.Button(self, bg="#A1DBCD", text ="Start drawing", font=("Courier", 8, "bold"), compound="top", relief=tk.FLAT, width=12, height=1, command=lambda: master.cs.spring_based_drawing(master))
        self.type_to_button["draw"] = self.draw_graph
        
        self.stop_drawing = tk.Button(self, bg="#A1DBCD", text ="Stop drawing", font=("Courier", 8, "bold"), compound="top", relief=tk.FLAT, width=12, height=1, command=lambda: master.cs._cancel())
        self.type_to_button["stop"] = self.stop_drawing
        
        self.create_tree = tk.Button(self, text='Tree', bg="#A1DBCD", width=50, height=50, relief=tk.FLAT, command = lambda: NetworkDimension(master.cs, "tree"))
        self.type_to_button["tree"] = self.create_tree
        
        self.create_star = tk.Button(self, text='Star', bg="#A1DBCD", width=50, height=50, relief=tk.FLAT, command = lambda: NetworkDimension(master.cs, "star"))
        self.type_to_button["star"] = self.create_star
        
        self.create_full_mesh = tk.Button(self, text='Full mesh', bg="#A1DBCD", width=50, height=50, relief=tk.FLAT, command = lambda: NetworkDimension(master.cs, "full-mesh"))
        self.type_to_button["full-mesh"] = self.create_full_mesh
        
        self.create_ring = tk.Button(self, text='Ring', bg="#A1DBCD", width=50, height=50, relief=tk.FLAT, command = lambda: NetworkDimension(master.cs, "ring"))
        self.type_to_button["ring"] = self.create_ring
        
        # netdim mode: motion or creation
        label_netdim = tk.Label(self, text="NetDim", bg="#A1DBCD", font=("Courier", 16, "bold")).grid(row=0, columnspan=4, sticky="ew")
        self.motion_mode.grid(row=1, column=0, columnspan=2, rowspan=2, padx=20, pady=20, sticky="nsew")
        self.creation_mode.grid(row=1, column=2, columnspan=2, rowspan=2, pady=5, padx=5, sticky=tk.W)
        sep = ttk.Separator(self, orient=tk.HORIZONTAL).grid(row=3, columnspan=4, sticky="ew")
        
        # creation mode: type of node or link
        label_creation_mode = tk.Label(self, text="Creation mode", bg="#A1DBCD", font=("Helvetica", 8, "bold")).grid(row=4, columnspan=4, sticky="ew")
        self.create_router.grid(row=5, column=0, padx=2, sticky=tk.N)
        self.create_oxc.grid(row=5, column=1, padx=2, sticky=tk.W)
        self.create_host.grid(row=5, column=2, padx=2, sticky=tk.W)
        self.create_antenna.grid(row=5, column=3, padx=2, sticky=tk.W)
        self.create_trunk.grid(row=6, column=0, columnspan=2, padx=2, sticky=tk.W)
        self.create_route.grid(row=6, column=2, columnspan=2, pady=5, padx=5, sticky=tk.W)
        self.create_traffic.grid(row=7, column=0, columnspan=2, pady=5, padx=5, sticky=tk.W)
        sep = ttk.Separator(self, orient=tk.HORIZONTAL).grid(row=8, columnspan=4, sticky="ew")
        
        # drawing options
        label_drawing_options = tk.Label(self, text="Force-directed layout", bg="#A1DBCD", font=("Helvetica", 8, "bold")).grid(row=9, columnspan=4, sticky="ew")
        self.draw_graph.grid(row=10, column=0, columnspan=2, pady=5, padx=20, sticky="nsew")
        self.stop_drawing.grid(row=10, column=2, columnspan=2, pady=5, padx=20, sticky="nsew")
        sep = ttk.Separator(self, orient=tk.HORIZONTAL).grid(row=11, columnspan=4, sticky="ew")
        
        # graph generation
        label_graph_generation = tk.Label(self, text="Graph generation", bg="#A1DBCD", font=("Helvetica", 8, "bold")).grid(row=11, columnspan=4, sticky="ew")
        self.create_tree.grid(row=12,column=0, columnspan=2, rowspan=2, padx=20, pady=20, sticky="nsew")
        self.create_star.grid(row=12,column=2, columnspan=2, rowspan=2, padx=20, pady=20, sticky="nsew")
        self.create_full_mesh.grid(row=14,column=0, columnspan=2, rowspan=2, padx=20, pady=20, sticky="nsew")
        self.create_ring.grid(row=14,column=2, columnspan=2, rowspan=2, padx=20, pady=20, sticky="nsew")
        sep = ttk.Separator(self, orient=tk.HORIZONTAL).grid(row=16, columnspan=4, sticky="ew")
        
    def switch_to_creation(self, master):
        self.creation_mode.config(relief=tk.SUNKEN)
        self.motion_mode.config(relief=tk.RAISED)
        master.cs._mode = "creation"
        master.cs.switch_binding()
        
    def switch_to_motion(self, master):
        self.creation_mode.config(relief=tk.RAISED)
        self.motion_mode.config(relief=tk.SUNKEN)
        master.cs._mode = "motion"
        master.cs.switch_binding()
        
    def change_creation_mode(self, master, mode):
        # change the mode to creation 
        self.switch_to_creation(master)
        master.cs._creation_mode = mode
        for obj_type in self.type_to_button:
            if(mode == obj_type):
                self.type_to_button[obj_type].config(relief=tk.SUNKEN)
            else:
                self.type_to_button[obj_type].config(relief=tk.FLAT)
        master.cs.switch_binding()
        
    def generate_square_tiling(self, scenario):
        self.erase_graph(scenario)
        scenario.generate_meshed_square(self.var_dimension.get())
        
    def generate_hypercube(self, scenario):
        self.erase_graph(scenario)
        scenario.generate_hypercube(self.var_dimension.get())
        
    def erase_graph(self, scenario):
        scenario.erase_graph()
        scenario.erase_network()
        
class NetworkDimension(tk.Toplevel):
    def __init__(self, scenario, type):
        super().__init__()
        self.geometry("145x70")
        self.title("Dimension")
        self.configure(background="#A1DBCD")
    
        # Network dimension
        if(type != "tree"):
            self.dimension = tk.Label(self, bg="#A1DBCD", text="Number of nodes")
        else:
            self.dimension = tk.Label(self, bg="#A1DBCD", text="Depth of the tree")
        self.var_dimension = tk.IntVar()
        self.var_dimension.set(4)
        self.entry_dimension = tk.Entry(self, textvariable=self.var_dimension, width=4)
    
        # confirmation button
        self.button_confirmation = ttk.Button(self, text="OK", command=lambda: self.create_graph(scenario, type))
        ttk.Style().configure("TButton", background="#A1DBCD")
        
        # position in the grid
        self.dimension.grid(row=0, column=0, pady=5, padx=5, sticky=tk.W)
        self.entry_dimension.grid(row=0, column=1, sticky=tk.W)
        self.button_confirmation.grid(row=1, column=0, columnspan=2, pady=5, padx=5, sticky="nsew")
        
    def create_graph(self, scenario, type):
        if(type == "star"):
            scenario.generate_star(self.var_dimension.get() - 1)
        elif(type == "ring"):
            scenario.generate_ring(self.var_dimension.get() - 1)
        elif(type == "full-mesh"):
            scenario.generate_full_mesh(self.var_dimension.get())
        else:
            scenario.generate_tree(self.var_dimension.get())
        scenario.draw_all(random=False)
        self.destroy()
        