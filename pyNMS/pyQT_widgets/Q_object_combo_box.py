from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QComboBox

class QObjectComboBox(QComboBox):
    
    def __init__(self):
        super().__init__()
        
    def setText(self, text):
        index = self.findText(text, Qt.MatchExactly)
        self.setCurrentIndex(index)
        
    @property
    def text(self):
        return self.currentText()
        
    @text.setter
    def text(self, value):
        self.setText(value)
        
    
    