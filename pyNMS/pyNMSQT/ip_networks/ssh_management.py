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
from tkinter import filedialog

class SSHWindow(FocusTopLevel):
    
    def __init__(self, controller):
        super().__init__()   

        self.controller = controller
        self.title('SSH connection management')
                        
        # label frame
        lf_ssh = Labelframe(self)
        lf_ssh.text = 'SSH connection management'
                                                               
        username = Label(self)
        username.text = 'Username :'

        self.entry_username = Entry(self, width=20)
        self.entry_username.text = 'cisco'

        # label 'algorithm'
        password = Label(self) 
        password.text = 'Password :'
        
        self.entry_password = Entry(self, width=20)
        self.entry_password.text = 'cisco'
                                                    
        path_to_putty = Button(self, width=20)
        path_to_putty.text = 'Path to PuTTY'
        path_to_putty.command = self.set_path
        
        self.path = Entry(self)
        self.path.text = 'C:/Users/minto/Desktop/Apps/putty.exe'
                                        
        # grid placement
        lf_ssh.grid(1, 0, 1, 2)
        username.grid(0, 0, in_=lf_ssh)
        self.entry_username.grid(0, 1, sticky='e', in_=lf_ssh)
        password.grid(1, 0, in_=lf_ssh)
        self.entry_password.grid(1, 1, in_=lf_ssh)
        path_to_putty.grid(2, 0, 1, 2, in_=lf_ssh)
        self.path.grid(3, 0, 1, 2, in_=lf_ssh)
        
        # hide the window when closed
        self.protocol('WM_DELETE_WINDOW', self.withdraw)
        # hide at creation
        self.withdraw()

    def set_path(self):
        # hidden top-level instance: 
        # - no decorations
        # - size: 0 
        # - top left corner
        fake_window = tk.Tk()
        fake_window.withdraw()
        fake_window.overrideredirect(True)
        fake_window.geometry('0x0+0+0')
        fake_window.deiconify()
        fake_window.lift()
        fake_window.focus_force()
        
        filepath = filedialog.askopenfilenames(
                                        parent = fake_window,
                                        initialdir = self.controller.path_workspace, 
                                        title = 'Import graph', 
                                        filetypes = (
                                        ('all files','*.*'),
                                        ('xls files','*.xls'),
                                        ))
        
        # no error when closing the window
        if not filepath: 
            return
        else: 
            filepath ,= filepath
            self.path.text = filepath
            
        fake_window.destroy()
        
    def get(self):
        return {
                'username': self.entry_username.text,
                'password': self.entry_password.text,
                'path': self.path.text
                }
        