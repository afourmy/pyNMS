from pythonic_tkinter.preconfigured_widgets import *

class Label():
    
    class_type = 'shape'
    subtype = 'label'
    color = 'black'
    
    def __init__(self, id, x, y, text):
        self.id = id
        self.x = x
        self.y = y
        self.text = text
        
    def __repr(self):
        return self.text
        
class Rectangle():
    
    class_type = 'shape'
    subtype = 'rectangle'
    color = 'black'
    
    def __init__(self, id, x, y):
        self.id = id
        self.x = x
        self.y = y
        
class Oval():
    
    class_type = 'shape'
    subtype = 'oval'
    color = 'black'
    
    def __init__(self, id, x, y):
        self.id = id
        self.x = x
        self.y = y

class LabelCreation(CustomTopLevel):
            
    def __init__(self, scenario, x, y):
        super().__init__()
        self.cs = scenario
        
        # labelframe
        lf_label_creation = Labelframe(self)
        lf_label_creation.text = 'Create a label'
        lf_label_creation.grid(0, 0)

        self.entry_label = Entry(self, width=20)
        
        OK_button = Button(self, width=20)
        OK_button.text = 'OK'
        OK_button.command = lambda: self.OK(x, y)
        
        lf_label_creation.grid(0, 0)
        self.entry_label.grid(0, 0, in_=lf_label_creation)
        OK_button.grid(1, 0, in_=lf_label_creation)

    def OK(self, x, y):
        label = Label(
                      self.cs.cvs.create_text(
                                            x, 
                                            y, 
                                            text = self.entry_label.text,
                                            font = ("Purisa", '12', 'bold'), 
                                            tag = ('shape',)
                                            ),
                      x, 
                      y,
                      self.entry_label.text
                      )
        self.cs.object_id_to_object[label.id] = label
        self.destroy()