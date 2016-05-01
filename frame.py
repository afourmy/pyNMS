import tkinter as tk
from tkinter import ttk

class MainFrame(tk.Frame):
    
    def __init__(self, master):
        super().__init__(width=200,height=600, borderwidth=3, relief="solid", background="#A1DBCD")
        self.bg_color = "#E6E6FA"

        # choix du mode: motion / node creation / link creation
        self.motion_mode = tk.Button(self, bg="#A1DBCD", text="Motion mode", width=200, height=200, relief=tk.FLAT, command=lambda: self.switch_to_motion(master))
        self.creation_mode = tk.Button(self, bg="#A1DBCD", text ="Creation mode", width=200, height=200, relief=tk.FLAT, command=lambda: self.switch_to_creation(master))
        self.create_router = tk.Button(self, bg="#A1DBCD", height=45, width=45, relief=tk.FLAT, command=lambda: self.change_creation_mode(master, "router"))
        self.create_oxc = tk.Button(self, bg="#A1DBCD", height=45, width=45, relief=tk.FLAT, command=lambda: self.change_creation_mode(master, "oxc"))
        self.create_host = tk.Button(self, bg="#A1DBCD", height=45, width=45, relief=tk.FLAT, command=lambda: self.change_creation_mode(master, "host"))
        self.create_antenna = tk.Button(self, bg="#A1DBCD", height=45, width=45, relief=tk.FLAT, command=lambda: self.change_creation_mode(master, "antenna"))
        self.create_trunk = tk.Button(self, bg="#A1DBCD", text ="Create trunk", fg="blue", font=("Courier", 8, "bold"), compound="top", relief=tk.FLAT, command=lambda: self.change_creation_mode(master, "trunk"))
        self.create_route = tk.Button(self, bg="#A1DBCD", text ="Create route", fg="green", font=("Courier", 8, "bold"), compound="top", relief=tk.FLAT, command=lambda: self.change_creation_mode(master, "route"))
        self.create_traffic = tk.Button(self, bg="#A1DBCD", text ="Create traffic", fg="purple", font=("Courier", 8, "bold"), compound="top", relief=tk.FLAT, command=lambda: self.change_creation_mode(master, "traffic"))
        
        # drawing du graphe
        self.draw_graph = tk.Button(self, text ="Draw graph", width=12, height=1, command=lambda: master.current_scenario.draw_all())
        self.force_based_drawing = tk.Button(self, text ="Eades drawing", width=12, height=1, command=lambda: master.current_scenario.spring_based_drawing(master))
        self.FR_drawing = tk.Button(self, text ="F-R drawing", width=12, height=1, command=lambda: master.current_scenario.frucht())
        self.stop_drawing = tk.Button(self, text ="Stop drawing", width=12, height=1, command=lambda: master.current_scenario._cancel())
        
        # Dimension du générateur de graphe
        self.dimension = tk.Label(self, text="Dimension", bg="#A1DBCD")
        self.var_dimension = tk.IntVar()
        self.var_dimension.set(3)
        self.entry_dimension = tk.Entry(self, textvariable=self.var_dimension, width=15)
        
        # Bouton pour générer les graphes
        self.bouton_meshed_square = tk.Button(self, text='Square tiling', bg=self.bg_color, width=12, height=1, command = lambda: self.generate_square_tiling(master.current_scenario))
        self.bouton_hypercube = tk.Button(self, text='Hypercube', bg=self.bg_color, width=12, height=1, command = lambda: self.generate_hypercube(master.current_scenario))
        self.bouton_tree = tk.Button(self, text='Tree', bg=self.bg_color, width=12, height=1, command = lambda: self.generate_tree(master.current_scenario))
        self.bouton_star = tk.Button(self, text='Star', bg=self.bg_color, width=12, height=1, command = lambda: self.generate_star(master.current_scenario))
        self.bouton_full_mesh = tk.Button(self, text='Full mesh', bg=self.bg_color, width=12, height=1, command = lambda: self.generate_full_mesh(master.current_scenario))
        self.bouton_ring = tk.Button(self, text='Ring', bg=self.bg_color, width=12, height=1, command = lambda: self.generate_ring(master.current_scenario))
        
        # netdim mode: motion or creation
        label_netdim = tk.Label(self, text="Tool mode", bg="#A1DBCD", font=("Helvetica", 16, "bold")).grid(row=0, columnspan=4, sticky="ew")
        self.motion_mode.grid(row=1, column=0, columnspan=2, rowspan=2, padx=20, pady=20, sticky=(tk.N, tk.S, tk.E, tk.W))
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
        label_drawing_options = tk.Label(self, text="Drawing options", bg="#A1DBCD", font=("Helvetica", 8, "bold")).grid(row=9, columnspan=4, sticky="ew")
        self.draw_graph.grid(row=10, column=0, columnspan=2, pady=5, padx=5, sticky=tk.W)
        self.force_based_drawing.grid(row=10, column=2, columnspan=2, pady=5, padx=5, sticky=tk.W)
        self.FR_drawing.grid(row=11, column=0, columnspan=2, pady=5, padx=5, sticky=tk.W)
        self.stop_drawing.grid(row=11, column=2, columnspan=2, pady=5, padx=5, sticky=tk.W)
        sep = ttk.Separator(self, orient=tk.HORIZONTAL).grid(row=12, columnspan=4, sticky="ew")
        
        # graph generation
        label_graph_generation = tk.Label(self, text="Graph generation", bg="#A1DBCD", font=("Helvetica", 8, "bold")).grid(row=12, columnspan=4, sticky="ew")
        self.dimension.grid(row=13, column=0, columnspan=2, pady=5, padx=5, sticky=tk.W)
        self.entry_dimension.grid(row=13, column=2, columnspan=2, sticky=tk.W)
        self.bouton_meshed_square.grid(row=14, column=0, columnspan=2, pady=5, padx=5, sticky=tk.W)
        self.bouton_hypercube.grid(row=14,column=2, columnspan=2, pady=5, padx=5, sticky=tk.W)
        self.bouton_tree.grid(row=15,column=0, columnspan=2, pady=5, padx=5, sticky=tk.W)
        self.bouton_star.grid(row=15,column=2, columnspan=2, pady=5, padx=5, sticky=tk.W)
        self.bouton_full_mesh.grid(row=16,column=0, columnspan=2, pady=5, padx=5, sticky=tk.W)
        self.bouton_ring.grid(row=16,column=2, columnspan=2, pady=5, padx=5, sticky=tk.W)
        sep = ttk.Separator(self, orient=tk.HORIZONTAL).grid(row=17, columnspan=4, sticky="ew")
        
    def switch_to_creation(self, master):
        self.creation_mode.config(relief=tk.SUNKEN)
        self.motion_mode.config(relief=tk.RAISED)
        master.current_scenario._mode = "creation"
        master.current_scenario.switch_binding()
        
    def switch_to_motion(self, master):
        self.creation_mode.config(relief=tk.RAISED)
        self.motion_mode.config(relief=tk.SUNKEN)
        master.current_scenario._mode = "motion"
        master.current_scenario.switch_binding()
        
    def change_creation_mode(self, master, mode):
        master.current_scenario._creation_mode = mode
        if(mode == "router"):
            self.create_router.config(relief=tk.SUNKEN)
            self.create_oxc.config(relief=tk.FLAT)
            self.create_trunk.config(relief=tk.FLAT)
            self.create_route.config(relief=tk.FLAT)
        elif(mode == "oxc"):
            self.create_router.config(relief=tk.SUNKEN)
            self.create_oxc.config(relief=tk.SUNKEN)
            self.create_route.config(relief=tk.FLAT)
            self.create_trunk.config(relief=tk.FLAT)
        elif(mode == "trunk"):
            self.create_router.config(relief=tk.FLAT)
            self.create_oxc.config(relief=tk.FLAT)
            self.create_route.config(relief=tk.FLAT)
            self.create_trunk.config(relief=tk.SUNKEN)
        elif(mode == "route"):
            self.create_route.config(relief=tk.SUNKEN)
            self.create_oxc.config(relief=tk.FLAT)
            self.create_router.config(relief=tk.FLAT)
            self.create_trunk.config(relief=tk.FLAT)
        elif(mode == "host"):
            self.create_route.config(relief=tk.SUNKEN)
            self.create_oxc.config(relief=tk.FLAT)
            self.create_router.config(relief=tk.FLAT)
            self.create_trunk.config(relief=tk.FLAT)
        elif(mode == "antenna"):
            self.create_route.config(relief=tk.SUNKEN)
            self.create_oxc.config(relief=tk.FLAT)
            self.create_router.config(relief=tk.FLAT)
            self.create_trunk.config(relief=tk.FLAT)
        master.current_scenario.switch_binding()
        
    def generate_square_tiling(self, scenario):
        self.erase_graph(scenario)
        scenario.generate_meshed_square(self.var_dimension.get())
        
    def generate_hypercube(self, scenario):
        self.erase_graph(scenario)
        scenario.generate_hypercube(self.var_dimension.get())
        
    def generate_star(self, scenario):
        scenario.generate_star(self.var_dimension.get())
        
    def generate_tree(self, scenario):
        self.erase_graph(scenario)
        scenario.generate_tree(self.var_dimension.get())
        
    def generate_full_mesh(self, scenario):
        self.erase_graph(scenario)
        scenario.generate_full_mesh(self.var_dimension.get())
        
    def generate_ring(self, scenario):
        self.erase_graph(scenario)
        scenario.generate_ring(self.var_dimension.get())
        
    def erase_graph(self, scenario):
        scenario.erase_graph()
        scenario.erase_network()