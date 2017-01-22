# NetDim
# Copyright (C) 2016 Antoine Fourmy (antoine.fourmy@gmail.com)
# Released under the GNU General Public License GPLv3

from pythonic_tkinter.preconfigured_widgets import *
from collections import OrderedDict

class GraphAlgorithmWindow(FocusTopLevel):
    def __init__(self, master):
        super().__init__()
        self.ms = master
        self.title('Advanced graph options')

        ## Shortest path section
        
        # shortest path algorithms include:
        #   - shortest path with A* (Dijkstra)
        #   - shortest path with Bellman-Ford
        #   - shortest path with Floyd-Warshall
        #   - shortest path with Linear programming
        
        self.sp_algorithms = OrderedDict([
        ('Constrained A*', self.ms.cs.ntw.A_star),
        ('Bellman-Ford algorithm', self.ms.cs.ntw.bellman_ford),
        ('Floyd-Warshall algorithm', self.ms.cs.ntw.floyd_warshall),
        ('Linear programming', self.ms.cs.ntw.LP_SP_formulation)
        ])

        # label frame for shortest path algorithms
        lf_sp = Labelframe(self)
        lf_sp.text = 'Shortest path algorithms'

        # List of shortest path algorithms
        self.sp_list = Combobox(self, width=30)
        self.sp_list['values'] = tuple(self.sp_algorithms.keys())
        self.sp_list.current(0)
                                
        sp_src_label = Label(self)
        sp_src_label.text = 'Source :'
        self.sp_src_entry = Entry(self)
        
        sp_dest_label = Label(self)
        sp_dest_label.text = 'Destination :'
        self.sp_dest_entry = Entry(self)
        
        bt_sp = Button(self)
        bt_sp.text = 'Compute path'
        bt_sp.command = self.compute_sp
        
        lf_sp.grid(1, 0, 1, 2)
        self.sp_list.grid(0, 0, 1, 2, in_=lf_sp)
        sp_src_label.grid(1, 0, in_=lf_sp)
        self.sp_src_entry.grid(1, 1, in_=lf_sp)
        sp_dest_label.grid(2, 0, in_=lf_sp)
        self.sp_dest_entry.grid(2, 1, in_=lf_sp)
        bt_sp.grid(3, 0, 1, 2, in_=lf_sp)
        
        ## Maximum flow section
        
        # maximum flow algorithms include:
        #   - maximum flow with Ford-Fulkerson
        #   - maximum flow with Edmond-Karps
        #   - maximum flow with Dinic
        #   - maximum flow with Linear programming
        
        self.mflow_algorithms = OrderedDict([
        ('Ford-Fulkerson', self.ms.cs.ntw.ford_fulkerson),
        ('Edmond-Karps', self.ms.cs.ntw.edmonds_karp),
        ('Dinic', self.ms.cs.ntw.dinic),
        ('Linear programming', self.ms.cs.ntw.LP_MF_formulation)
        ])
        
        # label frame for maximum flow algorithms
        lf_mflow = Labelframe(self)
        lf_mflow.text = 'Maximum flow algorithms'
        
        # List of flow path algorithms
        self.mflow_list = Combobox(self, width=30)
        self.mflow_list['values'] = tuple(self.mflow_algorithms.keys())
        self.mflow_list.current(0)
        self.mflow_list.bind('<<ComboboxSelected>>', self.readonly)
                                        
        mflow_src_label = Label(self)
        mflow_src_label.text = 'Source :'
        self.mflow_src_entry = Entry(self)
        
        mflow_dest_label = Label(self)
        mflow_dest_label.text = 'Destination :'
        self.mflow_dest_entry = Entry(self)
        
        bt_mflow = Button(self)
        bt_mflow.text = 'Compute flow'
        bt_mflow.command = self.compute_mflow
        
        lf_mflow.grid(1, 2, 1, 2)
        self.mflow_list.grid(0, 0, 1, 2, in_=lf_mflow)
        mflow_src_label.grid(1, 0, in_=lf_mflow)
        self.mflow_src_entry.grid(1, 1, in_=lf_mflow)
        mflow_dest_label.grid(2, 0, in_=lf_mflow)
        self.mflow_dest_entry.grid(2, 1, in_=lf_mflow)
        bt_mflow.grid(4, 0, 1, 2, in_=lf_mflow)
        
        ## K link-disjoint shortest paths section
        
        # K link-disjoint shortest paths algorithms include:
        #   - constrained A*
        #   - Bhandari algorithm
        #   - Suurbale algorithm
        #   - Linear programming
        
        self.spair_algorithms = OrderedDict([
        ('Constrained A*', self.ms.cs.ntw.A_star_shortest_pair),
        ('Bhandari algorithm', self.ms.cs.ntw.bhandari),
        ('Suurbale algorithm', self.ms.cs.ntw.suurbale),
        ('Linear programming', lambda: 'to repair')
        ])

        # label frame for shortest pair algorithms
        lf_spair = Labelframe(self) 
        lf_spair.text = 'K link-disjoint shortest paths algorithms'

        # List of shortest path algorithms
        self.spair_list = Combobox(self, width=30)
        self.spair_list['values'] = tuple(self.spair_algorithms.keys())
        self.spair_list.current(0)
                                
        spair_src_label = Label(self)
        spair_src_label.text = 'Source :'
        self.spair_src_entry = Entry(self)
        
        spair_dest_label = Label(self)
        spair_dest_label.text = 'Destination :'
        self.spair_dest_entry = Entry(self)

        nb_paths_label = Label(self)
        nb_paths_label.text = 'Number of paths :'
        self.nb_paths_entry = Entry(self)

        bt_spair = Button(self)
        bt_spair.text = 'Compute paths'
        bt_spair.command = self.compute_spair
        
        lf_spair.grid(2, 0, 1, 2)
        self.spair_list.grid(0, 0, 1, 2, in_=lf_spair)
        spair_src_label.grid(1, 0, in_=lf_spair)
        self.spair_src_entry.grid(1, 1, in_=lf_spair)
        spair_dest_label.grid(2, 0, in_=lf_spair)
        self.spair_dest_entry.grid(2, 1, in_=lf_spair)
        nb_paths_label.grid(3, 0, in_=lf_spair)
        self.nb_paths_entry.grid(3, 1, in_=lf_spair)
        bt_spair.grid(4, 0, 1, 2, in_=lf_spair)
        
        ## Minimum-cost flow section
        
        # minimum-cost flow algorithms include:
        #   - minimum-cost flow with Linear programming
        #   - minimum-cost flow with Klein (cycle-cancelling algorithm)
        
        self.mcflow_algorithms = OrderedDict([
        ('Linear programming', self.ms.cs.ntw.LP_MCF_formulation),
        ('Klein', lambda: 'to be implemented')
        ])
        
        # label frame for maximum flow algorithms
        lf_mcflow = Labelframe(self)
        lf_mcflow.text = 'Minimum-cost flow algorithms'
        
        # List of flow path algorithms
        self.mcflow_list = Combobox(self, width=30)
        self.mcflow_list['values'] = tuple(self.mcflow_algorithms.keys())
        self.mcflow_list.current(0)
        self.mcflow_list.bind('<<ComboboxSelected>>', self.readonly)
                                        
        mcflow_src_label = Label(self)
        mcflow_src_label.text = 'Source :'
        self.mcflow_src_entry = Entry(self)
        
        mcflow_dest_label = Label(self)
        mcflow_dest_label.text = 'Destination :'
        self.mcflow_dest_entry = Entry(self)

        bt_mcflow = Button(self)
        bt_mcflow.text = 'Compute cost'
        bt_mcflow.command = self.compute_mcflow

        flow_label = Label(self)
        flow_label.text = 'Flow :'
        self.flow_entry = Entry(self)

        lf_mcflow.grid(2, 2, 1, 2)
        self.mcflow_list.grid(0, 0, 1, 2, in_=lf_mcflow)
        mcflow_src_label.grid(1, 0, in_=lf_mcflow)
        self.mcflow_src_entry.grid(1, 1, in_=lf_mcflow)
        mcflow_dest_label.grid(2, 0, in_=lf_mcflow)
        self.mcflow_dest_entry.grid(2, 1, in_=lf_mcflow)
        bt_mcflow.grid(4, 0, 1, 2, in_=lf_mcflow)
        flow_label.grid(3, 0, in_=lf_mcflow)
        self.flow_entry.grid(3, 1, in_=lf_mcflow)

        # hide the window when closed
        self.protocol('WM_DELETE_WINDOW', self.withdraw)
        self.withdraw()
        
    def readonly(self, event):
        if self.flow_list.text[-4:-1] == 'MCF':
            self.max_flow_entry.config(state=tk.NORMAL)
        else:
            self.max_flow_entry.config(state='readonly')
                                        
    def compute_sp(self):
        source = self.ms.cs.ntw.nf(name=self.sp_src_entry.text)
        destination = self.ms.cs.ntw.nf(name=self.sp_dest_entry.text)
        algorithm = self.sp_list.text
        nodes, plinks = self.sp_algorithms[algorithm](source, destination)
        self.ms.cs.highlight_objects(*(nodes + plinks))
        
    def compute_spair(self):
        source = self.ms.cs.ntw.nf(name=self.spair_src_entry.text)
        destination = self.ms.cs.ntw.nf(name=self.spair_dest_entry.text)
        algorithm = self.spair_list.text
        nodes, plinks = self.spair_algorithms[algorithm](source, destination)
        self.ms.cs.highlight_objects(*(nodes + plinks))
        
    def compute_mflow(self):
        source = self.ms.cs.ntw.nf(name=self.mflow_src_entry.text)
        destination = self.ms.cs.ntw.nf(name=self.mflow_dest_entry.text)
        algorithm = self.mflow_algorithms[self.mflow_list.text]
        flow = algorithm(source, destination)   
        print(flow)
        
    def compute_mcflow(self):
        source = self.ms.cs.ntw.nf(name=self.mcflow_src_entry.text)
        destination = self.ms.cs.ntw.nf(name=self.mcflow_dest_entry.text)
        flow = self.flow_entry.text
        algorithm = self.mcflow_algorithms[self.mcflow_list.text]
        cost = algorithm(source, destination, flow)   
        print(cost)
