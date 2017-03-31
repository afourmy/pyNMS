from pythonic_tkinter.preconfigured_widgets import *
from tkinter import ttk
import tkinter as tk
import re
from Exscript import Host, Account
from Exscript.protocols import SSH2
from Exscript.util.start import start
from Exscript.util.match import first_match, any_match

class SendScript(CustomTopLevel):
    
    def __init__(self, scenario, nodes):
        super().__init__()
        self.cs = scenario
        self.title('Send a script')
        
        # main label frame
        lf_send_script = Labelframe(self)
        lf_send_script.text = 'Send  a script'
        lf_send_script.grid(0, 0)
        
        # List of AS type
        self.script_list = Combobox(self, width=21)
        self.script_list['values'] = tuple(self.cs.ms.scripts)
        # line below triggers an error when no script defined
        # add a check in the menu when the whole thing is working properly
        # self.script_list.current(0)

        # retrieve and save node data
        button_send = Button(self, width=23)
        button_send.text = 'Send script'
        button_send.command = lambda: self.send_script(nodes)
                        
        # Label for the name/type of the AS
        label_username = Label(self)
        label_username.text = 'Username :'
        
        label_password = Label(self)
        label_password.text = 'Password :'
        
        # Entry box for the name of the AS
        self.entry_username  = Entry(self, width=13)
        self.entry_password  = Entry(self, width=13)
        
        self.script_list.grid(0, 0, 1, 2, in_=lf_send_script)
        label_username.grid(1, 0, in_=lf_send_script)
        label_password.grid(2, 0, in_=lf_send_script)
        self.entry_username.grid(1, 1, in_=lf_send_script)
        self.entry_password.grid(2, 1, in_=lf_send_script)
        button_send.grid(3, 0, 1, 2, in_=lf_send_script)
        
    def execute_script(self, job, host, conn):
        conn.execute('terminal length 0')
        conn.send("enable\r")
        conn.app_authorize(self.account)
        for command in self.ip_to_instructions[host.address]:
            conn.execute(command)

    def send_script(self, nodes):
        script = self.cs.ms.scripts[self.script_list.text]
        # self.account = Account(self.entry_username.text, self.entry_password.text)
        self.account = Account('antoine', 'cisco')
        hosts = []
        
        for node in nodes:
            host = Host('ssh://{}'.format(node.ipaddress))
            host.set_account(self.account)
            hosts.append(host)
            
            # adapt the script by replacing all '$(property' with 
            # the node's property
            self.ip_to_instructions = {}
            
            def get_property(match):
                return str(getattr(node, match.group(0)[1:]))
            
            replace = lambda ins: re.sub(r'@\w+', get_property, ins)
            new_instructions = map(replace, script.instructions)
            self.ip_to_instructions[node.ipaddress] = new_instructions
    
        self.destroy()
        
        # send the script
        conn = SSH2()
        start([self.account], hosts, self.execute_script)#, max_threads=2)
        