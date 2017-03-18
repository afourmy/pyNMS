from .geo_scenario import GeoScenario
from networks import main_network

class NetworkScenario(GeoScenario):

    def __init__(self, *args, **kwargs):
        self.ntw = main_network.MainNetwork(self)
        super().__init__(*args, **kwargs)
