# Copyright (C) 2017 Antoine Fourmy <antoine dot fourmy at gmail dot com>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

from pythonic_tkinter.preconfigured_widgets import *

class RWAWindow(FocusTopLevel):
    
    def __init__(self, controller):
        super().__init__(master=controller)     
        self.title('Routing and Wavelength Assignment')
                        
        # label frame
        lf_rwa = Labelframe(self)
        lf_rwa.text = 'Routing and Wavelength Assignment'
                                                        
        ## Graph transformation and view name
                
        sco_name = Label(self)
        sco_name.text = 'Scenario name :'

        self.entry_sco = Entry(self, width=20)
        
        button_gt = Button(self, width=20)
        button_gt.text = 'Graph transformation'
        button_gt.command = self.transform_graph

        # label 'algorithm'
        algorithm = Label(self) 
        algorithm.text = 'Algorithm :'
        
        # combobox for the user to change the RWA algorithm
        self.rwa_list = Combobox(self, width=17)
        algorithms = ('Linear programming', 'Largest degree first')
        self.rwa_list['values'] = algorithms
        self.rwa_list.current(0)
                                                    
        button_run_alg = Button(self, width=20)
        button_run_alg.text = 'Run algorithm'
        button_run_alg.command = self.run_algorithm
                                        
        # grid placement
        lf_rwa.grid(1, 0, 1, 2)
        sco_name.grid(0, 0, in_=lf_rwa)
        self.entry_sco.grid(0, 1, sticky='e', in_=lf_rwa)
        button_gt.grid(1, 0, 1, 2, in_=lf_rwa)
        algorithm.grid(2, 0, in_=lf_rwa)
        self.rwa_list.grid(2, 1, sticky='e', in_=lf_rwa)
        button_run_alg.grid(3, 0, 1, 2, in_=lf_rwa)
        
        # hide the window when closed
        self.protocol('WM_DELETE_WINDOW', self.withdraw)
        # hide at creation
        self.withdraw()
        
    def transform_graph(self):
        name = self.entry_sco.text
        self.network.RWA_graph_transformation(name)

    def run_algorithm(self):
        algorithm = self.rwa_list.text
        if algorithm == 'Linear programming':
            self.network.LP_RWA_formulation()
        else:
            self.network.largest_degree_first()
        