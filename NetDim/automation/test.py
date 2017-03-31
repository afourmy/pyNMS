from tkinter import ttk
import tkinter as tk
from Exscript import Host, Account
from Exscript.protocols import SSH2
from Exscript.util.start import start
from Exscript.util.match import first_match, any_match

class ScriptingResult(tk.Toplevel):
    
    def __init__(self, nodes):
        super().__init__() 
        
        notebook = ttk.Notebook(self)
        self.dict_st = {}
        
        for node in nodes:
            frame = ttk.Frame(notebook)
            st_result = CustomScrolledText(frame)
            notebook.add(frame, text=node.name)
            self.dict_st[node.name] = st_result

        # disable the scrolledtext so that it cannot be edited
        st_result.config(state='disabled')
        # pack the scrolled text in the frame
        st_result.pack(fill='both', expand='yes')

def execute_script(job, host, conn):
    conn.execute('terminal length 0')
    # conn.send("enable\r")
    # conn.app_authorize(self.account)

def send_script():#, nodes):
    # self.script = self.cs.ms.scripts[self.script_list.text]
    account = Account('antoine', 'cisco')
    hosts = []
    # for node in nodes:
    host = Host('ssh://192.168.1.88')
    host.set_account(account)
    hosts.append(host)

    # create result window
    # self.result = ScriptingResult(nodes)
    # print(self.account, hosts)
    # send the script
    conn = SSH2()
    start([account], hosts, execute_script)#, max_threads=2)
    
send_script()

