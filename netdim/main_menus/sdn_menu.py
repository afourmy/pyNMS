# NetDim (contact@netdim.fr)

from miscellaneous.decorators import update_paths
from objects.objects import *
from os.path import join
from pythonic_tkinter.preconfigured_widgets import *
from subprocess import Popen
import paramiko 

class SDN_Menu(ScrolledFrame):
        
    def __init__(self, notebook, controller):
        self.controller = controller
        super().__init__(
                         notebook, 
                         width = 200, 
                         height = 600, 
                         borderwidth = 1, 
                         relief = 'solid'
                         )
        font = ('Helvetica', 8, 'bold')
        
        # label frame for object selection
        lf_management = Labelframe(self.infr)
        lf_management.text = 'SDN mangement'
        lf_management.grid(1, 0, sticky='nsew')
        
        self.type_to_button = {}
                
        for obj_type in ('sdn_switch', 'sdn_controller'):
            label = TKLabel(image=self.controller.dict_image['default'][obj_type])
            label.image = self.controller.dict_image['default'][obj_type]
            label.config(width=75, height=75)
            set_dnd = lambda _, type=obj_type: self.change_creation_mode(type)
            label.bind('<Button-1>', set_dnd)
            self.type_to_button[obj_type] = label
            
        start_mininet_button = Button(self)
        start_mininet_button.text = 'Start Mininet'
        start_mininet_button.command = self.start_mininet
        start_mininet_button.grid(1, 0, 1, 2, sticky='ew', in_=lf_management)
                
        # node creation
        self.type_to_button['sdn_switch'].grid(0, 0, padx=2, in_=lf_management)
        self.type_to_button['sdn_controller'].grid(0, 1, padx=2, in_=lf_management)
        
    def activate_dnd(self, node_type):
        self.controller.dnd = node_type
        
    @update_paths
    def change_creation_mode(self, mode):
        # activate drag and drop
        self.activate_dnd(mode)
        # change the view and update the current view
        if self.controller.view_menu.current_view == 'site':
            self.controller.view_menu.switch_view('network')
        self.view.creation_mode = mode
        self.view.switch_binding(mode)
        
    def start_mininet(self):
        # path_file = join(self.controller.path_app, 'mininet.txt')
        # with open(path_file, 'w') as file:
        #     file.write('sudo mn --custom /home/test_mininet/custom.py')
        #     file.close()
        #     
        #     # start an ssh session
        #     ssh = paramiko.SSHClient() 
        #     ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        #     # connect to the VM
        #     ssh.connect('192.168.56.101', username='mininet', password='mininet')
        #     sftp = ssh.open_sftp()
        #     # send the file the Mininet's VM
        #     sftp.put(path_file, '/home/test_mininet/test.py')
        #     # close the SFTP and SSH sessions
        #     sftp.close()
        #     ssh.close()
        path_putty = join(self.controller.path_app, 'SDN', 'start_mininet.txt')
        p = Popen(['putty', '-ssh', 'mininet@192.168.56.101', 
        '-pw', 'mininet', '-m', path_putty, '-t'])
        