import tkinter as tk

class DrawingOptions(tk.Toplevel):
    def __init__(self, master):
        super().__init__()
        self.geometry("600x300")
        self.title("Graph drawing with force-directed algorithms")
        self.ender_variables = []
        
        # this allows to change the behavior of closing the window. 
        # I don't want the window to be destroyed, simply hidden
        self.protocol("WM_DELETE_WINDOW", self.withdraw)
    
        # Variables de masse
        # Alpha
        self.label_alpha = tk.Label(self, text="Alpha")
        self.var_alpha = tk.DoubleVar()
        self.var_alpha.set(master.alpha)
        self.ender_variables.append(self.var_alpha)
        self.entry_alpha = tk.Entry(self, textvariable=self.var_alpha, width=15)
        
        # Beta
        self.label_beta = tk.Label(self, text = "Beta")
        self.var_beta = tk.IntVar()
        self.var_beta.set(master.beta)
        self.ender_variables.append(self.var_beta)
        self.entry_beta = tk.Entry(self, textvariable=self.var_beta, width=15)
        
        # k
        self.label_k = tk.Label(self, text = "k")
        self.var_k = tk.DoubleVar()
        self.var_k.set(master.k)
        self.ender_variables.append(self.var_k)
        self.entry_k = tk.Entry(self, textvariable=self.var_k, width=15)
        
        # Variables de dumping
        # Eta
        self.label_eta = tk.Label(self, text = "Eta")
        self.var_eta = tk.DoubleVar()
        self.var_eta.set(master.eta)
        self.ender_variables.append(self.var_eta)
        self.entry_eta = tk.Entry(self, textvariable=self.var_eta, width=15)
        
        # Delta
        self.label_delta = tk.Label(self, text = "Delta")
        self.var_delta = tk.DoubleVar()
        self.var_delta.set(master.delta)
        self.ender_variables.append(self.var_delta)
        self.entry_delta = tk.Entry(self, textvariable=self.var_delta, width=15)
        
        # optimal pairwise distance
        self.label_opd = tk.Label(self, text = "Optimal pairwise distance")
        self.var_opd = tk.DoubleVar()
        self.var_opd.set(master.opd)
        self.entry_opd = tk.Entry(self, textvariable=self.var_opd, width=15)
        
        # Raideur du ressort d
        self.label_raideur = tk.Label(self, text = "Raideur")
        self.var_raideur = tk.DoubleVar()
        self.var_raideur.set(master.raideur)
        self.ender_variables.append(self.var_raideur)
        self.entry_raideur = tk.Entry(self, textvariable=self.var_raideur, width=15)
        
        # drawing button
        self.bouton_force_based = tk.Button(self, text="Force-based", command = lambda: self.spring_based_drawing(), width=18, height=1)
        self.bouton_reingold = tk.Button(self, text="Fruchtemann-reingold", command = lambda: self.frucht(), width=18, height=1)
        self.bouton_draw_graph = tk.Button(self, text="Draw graph", command = lambda: self.draw_all(), width=18, height=1)
        self.bouton_stop = tk.Button(self, text="Stop drawing", command = lambda: self._cancel(), width=18, height=1)
        
        # affichage des boutons / label dans la grille
        self.label_alpha.grid(row=0, column=0, pady=5, padx=5, sticky=tk.W)
        self.entry_alpha.grid(row=0, column=1, sticky=tk.W)
        self.label_beta.grid(row=1, column=0, pady=5, padx=5, sticky=tk.W)
        self.entry_beta.grid(row=1, column=1, sticky=tk.W)
        self.label_k.grid(row=2, column=0, pady=5, padx=5, sticky=tk.W)
        self.entry_k.grid(row=2, column=1, sticky=tk.W)
        self.label_eta.grid(row=3, column=0, pady=5, padx=5, sticky=tk.W)
        self.entry_eta.grid(row=3, column=1, sticky=tk.W)
        self.label_delta.grid(row=4, column=0, pady=5, padx=5, sticky=tk.W)
        self.entry_delta.grid(row=4, column=1, sticky=tk.W)
        self.label_raideur.grid(row=5, column=0, pady=5, padx=5, sticky=tk.W)
        self.entry_raideur.grid(row=5, column=1, sticky=tk.W)
        self.label_opd.grid(row=0, column=2, pady=5, padx=5, sticky=tk.W)
        self.entry_opd.grid(row=0, column=3, sticky=tk.W)

        self.bouton_force_based.grid(row=7,column=1, pady=5, padx=5, sticky=tk.E)
        self.bouton_reingold.grid(row=7,column=3, pady=5, padx=5, sticky=tk.E)
        self.bouton_draw_graph.grid(row=7,column=0, pady=5, padx=5, sticky=tk.E)
        self.bouton_stop.grid(row=7,column=2, pady=5, padx=5, sticky=tk.E)
        
        self.withdraw()
    
    def save_value(self, master):
        # retrieve variables values
        master.alpha, master.beta, master.k, master.eta, master.delta, master.raideur = [v.get() for v in self.ender_variables]
        
        
