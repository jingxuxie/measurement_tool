from qcodes import VisaInstrument

temp_app_modes = ['fast settle', 'no overshoot']
field_app_modes = ['linear', 'no overshoot', 'oscillate']
mag_modes = ['persistent', 'driven']

class ppms(VisaInstrument):
    """
    This is the qcodes driver for Quantum Design PPMS
    """
        
    def __init__(self, name, address, **kwargs):
        super().__init__(name, address, **kwargs)
        
        self.add_parameter('field_config',
                           label='Field configuration',
                           get_cmd='FIELD?',
                           get_parser=self._get_field_config,
                           set_cmd=self._set_field_config)
        
        self.add_parameter('temp_config',
                           label='Temperature configuration',
                           get_cmd='TEMP?',
                           get_parser=self._get_temp_config,
                           set_cmd=self._set_temp_config)
        
        self.add_parameter('helium_level',
                           label='Helium level',
                           get_cmd='LEVEL?',
                           get_parser=self._get_helium_level)
        
        self.add_parameter('field',
                           label='Field',
                           get_cmd='GETDAT? 4',
                           get_parser=self._get_data)
        
        self.add_parameter('temp',
                           label='Temperature',
                           get_cmd='GETDAT? 2',
                           get_parser=self._get_data)
        
        self.add_parameter('status',
                           label='System status',
                           get_cmd='GETDAT? 1',
                           get_parser=self._get_status)
        

    def _get_field_config(self, config):
        field_sp, field_rate, field_app_mode, mag_mode = map(str.strip, config[:-1].split(','))
        config = {'field_sp': field_sp, 'field_rate': field_rate,
                  'field_app_mode': field_app_modes[int(field_app_mode)], 
                  'mag_mode': mag_modes[int(mag_mode)]}
        return config
    
    def _set_field_config(self, msg):
        field_sp, field_rate, field_app_mode, mag_mode = map(str.strip, msg.split(','))
        config = [field_sp, field_rate, str(field_app_modes.index(field_app_mode)), str(mag_modes.index(mag_mode))]
        super().write('FIELD ' + ' '.join(config))
        
    def _get_temp_config(self, config):
        temp_sp, temp_rate, temp_app_mode = map(str.strip, config[:-1].split(','))
        config = {'temp_sp': temp_sp, 'temp_rate': temp_rate,
                  'temp_app_mode': temp_app_modes[int(temp_app_mode)]}
        return config
    
    def _set_temp_config(self, msg):
        temp_sp, temp_rate, temp_app_mode = map(str.strip, msg.split(','))
        config = [temp_sp, temp_rate, str(temp_app_modes.index(temp_app_mode))]
        super().write('TEMP ' + ' '.join(config))
        
    def _get_helium_level(self, msg):
        lev, stat = map(str.strip, msg[:-1].split(','))
        return float(lev)
    
    def _get_data(self, s):
        return float(s[:-1].split(',')[2])
    
    def _get_status(self, s):
        temp_status = {'0': 'Unknown',
                       '1': 'Stable',
                       '2': 'Tracking',
                       '5': 'Near',
                       '6': 'Chasing',
                       '7': 'Precooling',
                       '10': 'Standby',
                       '13': 'Disabled',
                       '14': 'Not functioning',
                       '15': 'Failure'}
        
        field_status = {'0': 'Unknown',
                        '1': 'Persist',
                        '2': 'SW warming',
                        '3': 'SW cooling',
                        '4': 'Holding',
                        '5': 'Iterate',
                        '6': 'Charging',
                        '7': 'Discharging',
                        '8': 'Current error',
                        '15': 'Failure'}
        
        chamber_status = {'0': 'Unknown',
                          '1': 'Purged',
                          '2': 'Vented',
                          '3': 'Sealed',
                          '4': 'Purge/seal',
                          '5': 'Vent/seal',
                          '7': 'AtHivac',
                          '8': 'Pumping',
                          '9': 'Flooding',
                          '15': 'Failure'}
        
        sample_status = {'0': 'Unknown',
                         '1': 'Stopped',
                         '5': 'Moving',
                         '8': 'Limit switch',
                         '9': 'Index switch',
                         '15': 'Failure'}
        
        code_string = format(int(s[:-1].split(',')[2]), '016b')
        codes = [str(int(code_string[i:i+4], 2)) for i in range(0, 15, 4)]
        codes.reverse()
        
        status = {'temp_status': temp_status[codes[0]],
                  'field_status': field_status[codes[1]],
                  'chamber_status': chamber_status[codes[2]],
                  'sample_status': sample_status[codes[3]]}
        
        return status
    
    