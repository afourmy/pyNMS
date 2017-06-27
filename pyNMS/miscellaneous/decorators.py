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
        if not hasattr(self, 'controller'):
            self.controller = list(args).pop()
        self.project = self.controller.current_project
        self.view = self.project.current_view
        self.network_view = self.project.network_view
        self.site_view = self.project.site_view
        self.network = self.view.network
        self.main_network = self.network_view.network
        self.site_network = self.site_view.network
        function(self, *args, **kwargs)
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
    
# @empty_selection_and_destroy_menu
# used to clear the selection after clicking on an entry of the right-click
# menu, unselect everything and destroy the instance of the menu
def empty_selection_and_destroy_menu(function):
    def wrapper(self, *others):
        function(self, *others)
        self.view.unhighlight_all()
        self.destroy()
    return wrapper
    