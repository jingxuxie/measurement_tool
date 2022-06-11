from qcodes import VisaInstrument
import qcodes.utils.validators as vals


class Keithley_2635(VisaInstrument):
    """
    QCoDeS driver for the Keithley 2635 voltage source.
    """

    def __init__(self, name, address, **kwargs):
        super().__init__(name, address, terminator='\n', **kwargs)
        
        self.add_parameter('volt',
                           get_cmd='smua.measure.v()',
                           get_parser=float,
                           set_cmd='smua.source.levelv={:.12f}',
                           label='Voltage',
                           unit='V')

        self.add_parameter('curr',
                           get_cmd='smua.measure.i()',
                           get_parser=float,
                           set_cmd='smua.source.leveli={:.12f}',
                           label='Current',
                           unit='A')

        self.add_parameter('res',
                           get_cmd='smua.measure.r()',
                           get_parser=float,
                           set_cmd=False,
                           label='Resistance',
                           unit='Ohm')

        self.add_parameter('mode',
                           get_cmd='smua.source.func',
                           get_parser=float,
                           set_cmd='smua.measure.func={:d}',
                           val_mapping={'current': 0, 'voltage': 1},
                           docstring='Selects the output source.')

        self.add_parameter('nplc',
                           label='Number of power line cycles',
                           set_cmd='smua.measure.nplc={:.4f}',
                           get_cmd='smua.measure.nplc',
                           get_parser=float,
                           vals=vals.Numbers(0.001, 25))
        # volt range
        self.add_parameter('sourcerange_v',
                           label='voltage source range',
                           get_cmd='smua.source.rangev',
                           get_parser=float,
                           set_cmd='smua.source.rangev={:.12f}',
                           unit='V')
        
        self.add_parameter('measurerange_v',
                           label='voltage measure range',
                           get_cmd='smua.measure.rangev',
                           get_parser=float,
                           set_cmd='smua.measure.rangev={:.12f}',
                           unit='V')
        # current range
        self.add_parameter('sourcerange_i',
                           label='current source range',
                           get_cmd='smua.source.rangei',
                           get_parser=float,
                           set_cmd='smua.source.rangei={:.12f}',
                           unit='A')

        self.add_parameter('measurerange_i',
                           label='current measure range',
                           get_cmd='smua.measure.rangei',
                           get_parser=float,
                           set_cmd='smua.measure.rangei={:.12f}',
                           unit='A')
        # Compliance limit
        self.add_parameter('limitv',
                           get_cmd='smua.source.limitv',
                           get_parser=float,
                           set_cmd='smua.source.limitv={:.12f}',
                           unit='V')
        # Compliance limit
        self.add_parameter('limiti',
                           get_cmd='smua.source.limiti',
                           get_parser=float,
                           set_cmd='smua.source.limiti={:.12f}',
                           unit='A')
        
        self.add_parameter('output',
                           get_cmd='smua.source.output',
                           get_parser=float,
                           set_cmd='smua.source.output={:d}')

    def _display_settext(self, text):
        self.visa_handle.write('display.settext("{}")'.format(text))

    def get_idn(self):
        IDN = self.ask_raw('*IDN?')
        vendor, model, serial, firmware = map(str.strip, IDN.split(','))
        model = model[6:]

        IDN = {'vendor': vendor, 'model': model,
               'serial': serial, 'firmware': firmware}
        return IDN

    def display_clear(self):
        """
        This function clears the display, but also leaves it in user mode
        """
        self.visa_handle.write('display.clear()')

    def display_normal(self):
        """
        Set the display to the default mode
        """
        self.visa_handle.write('display.screen = display.SMUA_SMUB')

    def exit_key(self):
        """
        Get back the normal screen after an error:
        send an EXIT key press event
        """
        self.visa_handle.write('display.sendkey(75)')

    def reset(self):
        """
        Reset instrument to factory defaults.
        This resets both channels.
        """
        self.write('reset()')

    def ask(self, cmd: str) -> str:
        """
        Override of normal ask. This is important, since queries to the
        instrument must be wrapped in 'print()'
        """
        return super().ask('print({:s})'.format(cmd))