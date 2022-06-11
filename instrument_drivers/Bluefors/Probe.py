import json
import requests

class Probe:

    TIME_OUT = 10
    
    _CHANNEL_TO_N = {"Probe": 1}
                    
    _HEATER_TO_N = {"Probe-Heater": 4}
    
    def __init__(self, name, address, **kwargs):
        
        self._name = name
        self._url = address
        
    def set_temperature(self, temperature) -> float:
        
        req = requests.post('http://' + self._url + ':5001/heater/update', 
                            json = {'heater_nr': self._HEATER_TO_N["Probe-Heater"],
                                    'active': True, 'setpoint': temperature}, 
                            timeout = self.TIME_OUT)
        data = req.json()
        return data['setpoint']
        
        
        
    def heater_off(self) -> bool:
        
        req = requests.post('http://' + self._url + ':5001/heater/update', 
                            json = {'heater_nr': self._HEATER_TO_N["Probe-Heater"],
                                    'active': False}, 
                            timeout = self.TIME_OUT)
        data = req.json()
        return not data['active']
    
    def temperature(self) -> float:
        t = -1.0
        i = 0
        while (t < 0) and (i < 3):
            try:
                req = requests.get('http://' + self._url + ':5001/channel/measurement/latest', 
                                    timeout = self.TIME_OUT)
                data = req.json()
                t = data['temperature']
            except:
                pass
            i += 1
        return t
     
    
