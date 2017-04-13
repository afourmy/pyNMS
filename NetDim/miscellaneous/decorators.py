def update_paths(function):
    def wrapper(self, *args, **kwargs):
        if 'master' in kwargs:
            self.controller = kw.pop('master')
        self.project = self.controller.current_project
        self.scenario = self.project.current_scenario
        self.network_scenario = self.project.network_scenario
        self.site_scenario = self.project.site_scenario
        self.network = self.scenario.network
        self.site_network = self.site_scenario.network
        function(self, *args, **kwargs)
    return wrapper