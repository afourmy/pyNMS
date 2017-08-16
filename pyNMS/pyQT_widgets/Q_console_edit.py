from PyQt5.QtWidgets import QTextEdit

class QConsoleEdit(QTextEdit):
    
    def __init__(self):
        super().__init__()
        style = '''QTextEdit { background-color: rgb(0, 0, 0); 
                                color: rgb(255, 255, 255); 
                                font: 10pt "Courier New";
                              }'''
        self.setStyleSheet(style)
        