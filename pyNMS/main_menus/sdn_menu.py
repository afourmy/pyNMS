# NetDim (contact@netdim.fr)

from miscellaneous.decorators import update_paths
from objects.objects import *
from os.path import join
from PIL import ImageTk
from pythonic_tkinter.preconfigured_widgets import *
from subprocess import Popen
import warnings
try:
    import paramiko 
except ImportError:
    warnings.warn('paramiko missing: graphic mininet disabled')

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
        lf_network_creation = Labelframe(self.infr)
        lf_network_creation.text = 'Network creation'
        lf_network_creation.grid(0, 0, sticky='nsew')
        
        # label frame to configure the VM parameters
        lf_VM_management = Labelframe(self.infr)
        lf_VM_management.text = 'Mininet VM parameters'
        lf_VM_management.grid(1, 0, sticky='nsew')
        
        # label frame to configure the controller parameters
        lf_pox_management = Labelframe(self.infr)
        lf_pox_management.text = 'POX controller parameters'
        lf_pox_management.grid(2, 0, sticky='nsew')
        
        self.type_to_button = {}
        self.images = {}
                
        for obj_type in ('sdn_switch', 'sdn_controller'):
            img_name = 'default_{}.gif'.format(obj_type)
            img_path = join(self.controller.path_icon, img_name)
            img_pil = ImageTk.Image.open(img_path).resize((100, 100))
            self.images[obj_type] = ImageTk.PhotoImage(img_pil)
            label = TKLabel(image=self.images[obj_type])
            label.config(width=150, height=150)
            set_dnd = lambda _, type=obj_type: self.change_creation_mode(type)
            label.bind('<Button-1>', set_dnd)
            self.type_to_button[obj_type] = label
                    
        label_mininet_IP = Label(self.infr)
        label_mininet_IP.text = 'VM IP'
        self.entry_mininet_IP = Entry(self.infr, width=18)
        self.entry_mininet_IP.text = '192.168.56.101'
        
        label_mininet_username = Label(self.infr)
        label_mininet_username.text = 'VM Username'
        self.entry_mininet_username = Entry(self.infr, width=18)
        self.entry_mininet_username.text = 'mininet'
        
        label_mininet_password = Label(self.infr)
        label_mininet_password.text = 'VM Password'
        self.entry_mininet_password = Entry(self.infr, width=18)
        self.entry_mininet_password.text = 'mininet'
        
        self.X11_bool = tk.BooleanVar()
        self.X11_bool.set(True)
        button_X11_forwarding = Checkbutton(self.infr, variable=self.X11_bool)
        button_X11_forwarding.text = 'Enable X11 forwarding'
        
        start_mininet_button = Button(self, width=35)
        start_mininet_button.text = 'Start Mininet'
        start_mininet_button.command = self.start_mininet
        
        start_wireshark_button = Button(self, width=35)
        start_wireshark_button.text = 'Start Wireshark'
        start_wireshark_button.command = self.start_wireshark
        
        label_mininet_IP.grid(0, 0, padx=20, in_=lf_VM_management)
        label_mininet_username.grid(1, 0, padx=20, in_=lf_VM_management)
        label_mininet_password.grid(2, 0, padx=20, in_=lf_VM_management)
        self.entry_mininet_IP.grid(0, 1, in_=lf_VM_management)
        self.entry_mininet_username.grid(1, 1, in_=lf_VM_management)
        self.entry_mininet_password.grid(2, 1, in_=lf_VM_management)
        button_X11_forwarding.grid(3, 0, 1, 2, sticky='ew', in_=lf_VM_management)
        start_mininet_button.grid(4, 0, 1, 2, sticky='ew', in_=lf_VM_management)
        start_wireshark_button.grid(5, 0, 1, 2, sticky='ew', in_=lf_VM_management)
        
        self.pox_parameters = (
                        ' forwarding.l2_learning',
                        ' openflow.spanning_tree --no-flood --hold-down',
                        ' log.level --DEBUG samples.pretty_log',
                        ' openflow.discovery host_tracker',
                        ' info.packet_dump'
                        )
        
        self.pox_parameters_booleans = []
        for id, parameter in enumerate(self.pox_parameters):
            parameter_bool = tk.BooleanVar()
            parameter_bool.set(True)
            self.pox_parameters_booleans.append(parameter_bool)
            button = Checkbutton(self.infr, variable=parameter_bool)
            button.text = parameter.split(' ')[1]
            button.grid(id, 0, in_=lf_pox_management)
            
        start_POX_button = Button(self, width=35)
        start_POX_button.text = 'Start POX'
        start_POX_button.command = self.start_POX
        start_POX_button.grid(5, 0, 1, 2, sticky='ew', in_=lf_pox_management)
                
        # node creation
        self.type_to_button['sdn_switch'].grid(0, 0, padx=20, in_=lf_network_creation)
        self.type_to_button['sdn_controller'].grid(0, 1, padx=2, in_=lf_network_creation)
        
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
        
    @update_paths
    def start_mininet(self):
        sdn_nodes = ('host', 'sdn_switch', 'sdn_controller')
        path_file = join(self.controller.path_app, 'SDN', 'mininet.py')
        # allocation mininet's name to every host, switch and controller
        self.main_network.mininet_configuration()
        with open(path_file, 'w') as file:
            file.write('from mininet.net import Mininet\n')
            file.write('from mininet.cli import CLI\n')
            file.write('from mininet.node import DefaultController, RemoteController\n')
            file.write('net = Mininet()\n')
            for node in self.network.ftr('node', *sdn_nodes):
                file.write(node.mininet_conf())
            for link in self.network.ftr('plink', 'ethernet link'):
                if (link.source.subtype in ('host', 'sdn_switch')
                    and link.destination.subtype in ('host', 'sdn_switch')):
                    file.write('net.addLink({},{})\n'.format(
                                        link.source.mininet_name,
                                        link.destination.mininet_name
                                        ))
            file.write('net.start()\n')
            file.write('CLI(net)\n')
            file.close()
            
        # start an ssh session
        ssh = paramiko.SSHClient() 
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        # connect to the VM
        ssh.connect(
                    self.entry_mininet_IP.text, 
                    username = self.entry_mininet_username.text, 
                    password = self.entry_mininet_password.text
                    )
        sftp = ssh.open_sftp()
        # send the file the Mininet's VM
        sftp.put(path_file, '/home/test_mininet/test.py')
        # close the SFTP and SSH sessions
        sftp.close()
        ssh.close()
        path_putty_file = join(self.controller.path_app, 'SDN', 'start_mininet.txt')
        start_shell_commands = [
                                'putty',
                                '-ssh',
                                '{}@{}'.format(
                                               self.entry_mininet_username.text,
                                               self.entry_mininet_IP.text
                                               ),
                                '-pw',
                                self.entry_mininet_password.text,
                                '-m',
                                path_putty_file,
                                '-t',
                                ]
        if self.X11_bool.get():
            start_shell_commands.insert(5, '-X')
        p = Popen(start_shell_commands)
        
    def start_wireshark(self):
        path_putty_file = join(self.controller.path_app, 'SDN', 'start_wireshark.txt')
        start_shell_commands = [
                                'putty',
                                '-ssh',
                                '{}@{}'.format(
                                               self.entry_mininet_username.text,
                                               self.entry_mininet_IP.text
                                               ),
                                '-pw',
                                self.entry_mininet_password.text,
                                '-X',
                                '-m',
                                path_putty_file,
                                '-t',
                                ]
        p = Popen(start_shell_commands)
        
    @update_paths
    def start_POX(self):
        path_putty_file = join(self.controller.path_app, 'SDN', 'pox.txt')
        pox_command = 'sudo ~/pox/pox.py'
        for id, parameter in enumerate(self.pox_parameters):
            if self.pox_parameters_booleans[id].get():
                pox_command += parameter
        for controller in self.network.ftr('node', 'sdn_controller'):
            if controller.controller_type == 'RemoteController':
                with open(path_putty_file, 'w') as file:
                    file.write(pox_command)
                    file.close()
                start_shell_commands = [
                                        'putty',
                                        '-ssh',
                                        '{}@{}'.format(
                                            self.entry_mininet_username.text,
                                            self.entry_mininet_IP.text
                                            ),
                                        '-pw',
                                        self.entry_mininet_password.text,
                                        '-m',
                                        path_putty_file,
                                        '-t'
                                        ]
                p = Popen(start_shell_commands)
        