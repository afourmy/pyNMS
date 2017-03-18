from .geo_scenario import GeoScenario
from networks import site_network

class SiteScenario(GeoScenario):

    def __init__(self, *args, **kwargs):
        self.ntw = site_network.SiteNetwork(self)
        super().__init__(*args, **kwargs)