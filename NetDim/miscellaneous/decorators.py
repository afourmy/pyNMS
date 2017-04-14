def overrider(interface_class):
    def overrider(method):
        assert(method.__name__ in dir(interface_class))
        return method
    return overrider
    
def update_coordinates(function):
    def wrapper(self, event, *others):
        event.x, event.y = self.cvs.canvasx(event.x), self.cvs.canvasy(event.y)
        function(self, event, *others)
    return wrapper

def update_paths(function):
    def wrapper(self, *args, **kwargs):
        if 'master' in kwargs:
            self.controller = kw.pop('master')
        self.project = self.controller.current_project
        self.view = self.project.current_view
        self.network_view = self.project.network_view
        self.site_view = self.project.site_view
        self.network = self.view.network
        self.site_network = self.site_view.network
        function(self, *args, **kwargs)
    return wrapper
