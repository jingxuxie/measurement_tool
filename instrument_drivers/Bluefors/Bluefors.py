import json
import requests

class Bluefors:

    TIME_OUT = 10
    
    _CHANNEL_TO_N = {"50K-flange": 1, "4K-flange": 2, "Magnet": 3,
                    "Still-flange": 5, "MXC-flange": 6}
    
    _N_TO_CHANNEL = {1: "50K-flange", 2: "4K-flange", 3: "Magnet",
                    5: "Still-flange", 6: "MXC-flange"}
                    
    _HEATER_TO_N = {"Heatswitch Still": 1, "Heatswitch MXC": 2, 
                    "Still-heater": 3, "MXC-heater": 4}
    
    def __init__(self, name, address, **kwargs):
        
        self._name = name
        self._url = address
        
    def set_temperature(self, temperature) -> float:
        
        req = requests.post('http://' + self._url + ':5001/heater/update', 
                            json = {'heater_nr': self._HEATER_TO_N["MXC-heater"],
                                    'active': True, 'setpoint': temperature}, 
                            timeout = self.TIME_OUT)
        data = req.json()
        return data['setpoint']
        
    def heater_off(self) -> bool:
        
        req = requests.post('http://' + self._url + ':5001/heater/update', 
                            json = {'heater_nr': self._HEATER_TO_N["MXC-heater"],
                                    'active': False}, 
                            timeout = self.TIME_OUT)
        data = req.json()
        return not data['active']
        
    def measure(self):
    
        req = requests.get('http://' + self._url + ':5001/channel/measurement/latest', 
                            timeout = self.TIME_OUT)
        data = req.json()
        return {self._N_TO_CHANNEL[data['channel_nr']], data['temperature']}
    
