from pyQT_widgets.Q_dict_tree_view import QDictTreeView

class InternalStructure(QDictTreeView):
    
    def __init__(self, node, controller):
        super().__init__(node.structure)