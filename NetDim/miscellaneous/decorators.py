import controller

# @overrider
def overrider(interface_class):
    def overrider(method):
        assert(method.__name__ in dir(interface_class))
        return method
    return overrider

# @update_coordinates
def update_coordinates(function):
    def wrapper(self, event, *others):
        event.x, event.y = self.cvs.canvasx(event.x), self.cvs.canvasy(event.y)
        function(self, event, *others)
    return wrapper

# @update_paths
# used to update all paths for a function in the class of a persistent
# window, or a persistent frame (the 5 persistent menu for instance)
def update_paths(function):
    def wrapper(self, *args, **kwargs):
        self.project = self.controller.current_project
        self.view = self.project.current_view
        self.network_view = self.project.network_view
        self.site_view = self.project.site_view
        self.network = self.view.network
        self.site_network = self.site_view.network
        function(self, *args, **kwargs)
    return wrapper
    
# @initialize_paths decorates init, which last 'args' argument is the controller
# used to update all paths at initialization of the instance of a non-persistent
# window, or a non-persistent widget (the right-click menu for instance),
# or a class with fixed paths (network, scenario)
def initialize_paths(init):
    def wrapper(self, *args, **kwargs):
        self.controller = controller = list(args).pop()
        self.project = project = self.controller.current_project
        self.view = view = self.project.current_view
        self.network_view = network_view = self.project.network_view
        self.site_view = site_view = self.project.site_view
        self.network = network = self.view.network
        self.site_network = site_network = self.site_view.network
        init(self, *args, **kwargs)
    return wrapper
        
# @defaultizer(**default arguments)
# decorating __init__ to initialize properties
def defaultizer(**default_kwargs_values):
    def inner_decorator(init):
        def wrapper(self, *args, **kwargs):
            for property, default_value in default_kwargs_values.items():
                if property not in kwargs:
                    kwargs[property] = default_value
            init(self, *args, **kwargs)
        return wrapper
    return inner_decorator
    