from qcodes import VisaInstrument

class Keithley6221(VisaInstrument):
    """
    QCoDeS driver for the Keithley 6221 current source.
    """
    _STEP = 0.1
    _INTER_DEALY = 0.1
    _STOP = False
    def __init__(self, name, address, **kwargs):
        super().__init__(name, address, terminator='\n', **kwargs)

        self.add_parameter('delta_high',
                           get_cmd='SOUR:DELT:HIGH?',
                           get_parser=float,
                           set_cmd='SOUR:DELT:HIGH {:.15f}',
                           label='Delta High')

        self.add_parameter('delta_low',
                           get_cmd='SOUR:DELT:LOW?',
                           get_parser=float,
                           set_cmd='SOUR:DELT:LOW {:.15f}',
                           label='Delta Low')

        self.add_parameter('delta_delay',
                           get_cmd='SOUR:DELT:DEL?',
                           get_parser=float,
                           set_cmd='SOUR:DELT:DEL {:.15f}',
                           label='Delta Delay')

        self.add_parameter('delta_arm',
                           get_cmd='SOUR:DELT:ARM?',
                           get_parser=int,
                           label='Delta Arm')
        
        self.add_parameter('delta_read',
                           get_cmd='SENS:DATA?',
                           get_parser=self._volt_parser,
                           label='Delta Voltage',
                           unit='V')
                          
        self.add_parameter('ampl',
                           set_cmd ='SOUR:WAVE:AMPL',
                           label='Amplitude',
                           unit='A')
        
        self.add_parameter('freq',
                           set_cmd ='SOUR:WAVE:FREQ',
                           label='Frequency',
                           unit='Hz')
                           
        self.add_parameter('offs',
                           set_cmd ='SOUR:WAVE:OFFS',
                           label='Offset',
                           unit='A')
                           
        self.add_parameter('range',
                           get_cmd='CURR:RANG?',
                           get_parser=float,
                           set_cmd='CURR:RANG {:.15f}',
                           label='Current Range')
        
        self.add_parameter('curr',
                           get_cmd='CURR?',
                           get_parser=float,
                           set_cmd='CURR {:.15f}',
                           label='Current')
        
        self.add_parameter('compliance',
                           get_cmd='CURR:COMP?',
                           get_parser=float,
                           set_cmd='CURR:COMP {:.15f}',
                           label='Compliance')
        
        self.add_parameter('output',
                           get_cmd='OUTP?',
                           get_parser=float,
                           set_cmd='OUTP {:d}',
                           label='output')
                           
        self.connect_message()

    def arm_delta(self):
        self.write('SOUR:DELT:ARM')   
        
    def trigger_delta(self):
        self.write('INIT:IMM')
    
    def arm_wave(self):
        self.write('SOUR:WAVE:ARM')
        
    def trigger_wave(self):
        self.write('SOUR:WAVE:INIT')
        
    def abort_wave(self):
        self.write('SOUR:WAVE:ABOR')
        
    def abort_sweep(self):   
        self.write('SOUR:SWE:ABOR')
        
    def _volt_parser(self, msg):
        fields = [float(x) for x in msg.split(',')]
        return fields[0]
        
    def reset(self):
        self.write(':*RST')
        
    def sine_wave(self):
        self.write("SOUR:WAVE:FUNC SIN")
        