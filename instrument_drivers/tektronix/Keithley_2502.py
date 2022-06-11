from qcodes import VisaInstrument
from qcodes.utils.validators import Strings, Enum
from time import sleep
import numpy as np

class Keithley2502(VisaInstrument):
    """
    QCoDeS driver for the Keithley 2502 voltage source.
    """
    _STEP = 0.1
    _INTER_DELAY = 0.1
    _STOP = False
    def __init__(self, name, address, **kwargs):
        super().__init__(name, address, terminator='\n', **kwargs)

        
        self.add_parameter('volt',
                           #get_cmd=':MEAS:VOLT?',
                           #get_parser=float,
                           set_cmd=':SOUR:VOLT:LEV {:.12f}',
                           label='Voltage',
                           unit='V')

        self.add_parameter('curr',
                           get_cmd=':READ?',
                           #get_cmd = ':MEAS:CURR?',
                           get_parser=self._curr_parser,
                           set_cmd=':SOUR:CURR:LEV {:.12f}',
                           label='Current',
                           unit='A')
        self.add_parameter('rangei',
                           get_cmd='SENS:CURR:RANG?',
                           get_parser=float,
                           set_cmd='SENS:CURR:RANG {:.12f}',
                           label='Current measure range')
        self.add_parameter('res',
                           get_cmd=':MEAS:RES?',
                           get_parser=float,
                           label='Resistance',
                           unit='Ohm')

        self.add_parameter('sourcerange_v',
                           get_cmd='SOUR:VOLT:RANG?',
                           get_parser=float,
                           set_cmd='SOUR:VOLT:RANG {:.12f}',
                           label='Voltage source range')
        
        self.add_parameter('measurerange_v',
                           get_cmd='SENS:VOLT:RANG?',
                           get_parser=float,
                           set_cmd='SENS:VOLT:RANG {:.12f}',
                           label='Voltage measure range')

        self.add_parameter('sourcerange_i',
                           get_cmd='SOUR:CURR:RANG?',
                           get_parser=float,
                           set_cmd='SOUR:CURR:RANG {:.12f}',
                           label='Current source range')
        
        self.add_parameter('measurerange_i',
                           get_cmd='SENS:CURR:RANG?',
                           get_parser=float,
                           set_cmd='SENS:CURR:RANG {:.12f}',
                           label='Current measure range')

        self.add_parameter('limitv',
                           get_cmd=':SOUR:CURR:VLIMIT?',
                           get_parser=float,
                           set_cmd=':SOUR:CURR:VLIMIT {:.12f}',
                           label='Voltage Compliance')

        self.add_parameter('limiti',
                           get_cmd=':SOUR:VOLT:ILIMIT?',
                           get_parser=float,
                           set_cmd=':SOUR:VOLT:ILIMIT {:.12f}',
                           label='Current Compliance')
        
        self.add_parameter('output',
                           get_parser=int,
                           set_cmd=':OUTP:STAT {:d}',
                           get_cmd=':OUTP:STAT?')
                           
        self.connect_message()

    def _curr_parser(self, curr_read):
        return float(curr_read.split(',')[0])
        
    def set_volt(self, v_start, v_stop):
        v_vals = np.linspace(v_start, v_stop, abs(int(round((v_stop-v_start)/self._STEP)))+1)
        for v in v_vals[1:]:
            if self._STOP:
                self._STOP = False
                break
            self.volt(v)
            sleep(self._INTER_DELAY)
        
        #return self.curr()

    def reset(self):
        """
        Reset the instrument. When the instrument is reset, it performs the
        following actions.

            Returns the SourceMeter to the GPIB default conditions.

            Cancels all pending commands.

            Cancels all previously send `*OPC` and `*OPC?`
        """
        self.write(':*RST')