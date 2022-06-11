from qcodes import VisaInstrument

class Keithley2182(VisaInstrument):
    """
    QCoDeS driver for the Keithley 2182 voltmeter.
    """
    def __init__(self, name, address, **kwargs):
        super().__init__(name, address, terminator='\n', **kwargs)

        self.add_parameter('volt',
                           get_cmd=':FETC?',
                           get_parser=float,
                           label='Voltage')

    def zero(self):
        self.write(':SENS:VOLT:REF:ACQ')
        self.write(':SENS:VOLT:REF:STAT ON')
        