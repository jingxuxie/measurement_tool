# -*- coding: utf-8 -*-
"""
Created on Wed Jan 26 09:08:29 2022

@author: terahertz
"""
# -*- coding: utf-8 -*-
"""
Created on Wed Jan 19 18:56:02 2022

@author: terahertz
"""
# -*- coding: utf-8 -*-
"""
Created on Mon Jan 10 18:48:40 2022

@author: terahertz
"""
# -*- coding: utf-8 -*-
"""
Created on Sun Jan  9 14:03:03 2022

@author: terahertz
"""
#%% Import
from time import sleep
import numpy as np
import qcodes as qc
from os import path, makedirs
from datetime import datetime

import matplotlib.pyplot as plt
from matplotlib.patches import BoxStyle
from custom_bbox import AngledBox

# Drivers

from instrument_drivers.tektronix.Keithley_2450 import Keithley2450
from instrument_drivers.tektronix.Keithley_2400 import Keithley_2400
from instrument_drivers.tektronix.Keithley_2502 import Keithley2502
#from instrument_drivers.stanford_research.SR830 import SR830
from instrument_drivers.tektronix.Keithley_6221 import Keithley6221
#from instrument_drivers.american_magnetics.AMI430 import AMI430
#from instrument_drivers.Bluefors.Probe import Probe


# Initialisation
smu_g1 = Keithley2502('SMU1','GPIB0::24::INSTR') # Vb 

smu_g2 = Keithley2450('SMU2','GPIB0::18::INSTR') # Bias

smu_g3 = Keithley_2400('SMU3','GPIB0::25::INSTR') # Vt 

#lockin1 = SR830('SR830_1','GPIB0::08::INSTR', autorange=False)
#lockin2 = SR830('SR830_2','GPIB0::09::INSTR', autorange=False)

K6221DeltaV = Keithley6221('K6221','GPIB0::12::INSTR')

#%% Input

to_plot = True;

# Input parameters

# Fix (Vt - Bias) and Sweep Bias and Vb
# Three loops

# first loop
Bias_start = -0.8; ## Bias
Bias_stop = -0.8;
Bias_step = 0.1;

# second loop
Vt_start = 3.31;  ## Vt
Vt_stop = 2.5;  
Vt_step = 0.01;

# third loop
Vb_start = -6 ## Vb  K2502 negative output
Vb_stop = 4;
Vb_step = 0.001;



# time control
delay = 1;
i_sd = 1e-9;
#amp = 1

# writing data
file_dir = "C:\\Data\\Zuocheng\\20220215\\I 11-6 Rxx 12-5 Bias = -0.8 V Vt 3.31 to 2.5 V_1nA.dat"

#field_ramp_down = False

# Range settings
smu_g1.rangei(10e-9)   ##Vb
smu_g1.measurerange_i(10e-9) ## Vb

#smu_g2.rangei(10e-9)   ##Bias
smu_g2.measurerange_i(10e-9) ## Bias

#smu_g3.measurerange_i(10e-9)  ## Vt

# Ramp control
smu_g2.volt.step = 0.1
smu_g2.volt.inter_delay = 1

smu_g3.volt.step = 0.1
smu_g3.volt.inter_delay = 0.1

V1 = 0 ## Vb



#%% Measurement
try:
    # File check
    d_path = path.dirname(file_dir)
    if not path.exists(d_path):
        makedirs(d_path)
    if path.isfile(file_dir):
        file_dir = file_dir[:-4] + datetime.now().strftime('_%Y%m%d_%H%M%S') + '.dat'
    file = open(file_dir,"a")
    file.write("Bias\tVt\tVb\tRxx1\tTheta1\tRxx2\tTheta2\tLeak1\tLeak2\tLeak3\n")
    file.write("V\tV\tV\tOhm\t\tOhm\t\tA\tA\tA\n") #header
    file.close()
    
    # Loop parameters
    
   
    
    
    Bias_vals = np.linspace(Bias_start, Bias_stop, int(abs(round((Bias_stop-Bias_start)/Bias_step)))+1)
    
    Vt_vals = np.linspace(Vt_start, Vt_stop, int(abs(round((Vt_stop-Vt_start)/Vt_step)))+1)
    
    Vb_vals = np.linspace(Vb_start, Vb_stop, int(abs(round((Vb_stop-Vb_start)/Vb_step)))+1)
    
    data_list = []
    
    result1 = np.zeros([len(Vt_vals),len(Vb_vals)])
    
    if to_plot:
        f = plt.figure('Dual gate resistance mapping', figsize=(20,7))
        grid = plt.GridSpec(5, 8, wspace=2, hspace=2)
        
        ax1 = f.add_subplot(grid[:2,0:2])
        ax1.set(title ="Rxx", xlabel ="Vb", ylabel="Rxx (Ohm)")
        ax1.grid(True)
        ax1.ticklabel_format(axis='y',style='sci',scilimits=(0,0))
        line1, = ax1.plot([],[],'.-')
        
        
        BoxStyle._style_list["angled"] = AngledBox
        ratio = abs((Vt_stop-Vt_start)*100/(Vb_stop-Vb_start))
        
        ax5 = f.add_subplot(grid[2:,:4])
        ax5.set(title ="Resistance colormap - 1", xlabel ="Vb (V)", ylabel="Vt (V)")
        map5 = ax5.imshow(result1, origin='lower',interpolation='none',aspect=ratio, 
                           extent=[Vb_start-Vb_step/2,Vb_stop+Vb_step/2, 
                                   Vt_start-Vt_step/2,Vt_stop+Vt_step/2])
        
        # ann5 = ax5.annotate(DD_vals[0], xy=(1, 0.5/len(DD_vals)), 
        #                      xycoords='axes fraction', fontsize=10, color = 'w', 
        #                      xytext=(10, 0), textcoords='offset points',
        #                      ha='left', va='center', fontweight='bold',
        #                      bbox=dict(boxstyle='angled', fc='red', ec='none'))
    
    
    
    #Measurement start
    # print(ami.coil_constant())
    # sleep(3600)
    first_gate_ramp = True
    first_gate_ramp_Bias = True
    first_gate_ramp_Vb = True
    
    print(datetime.now().strftime('%H:%M:%S'))
   
    for Bias in Bias_vals:
        
        if first_gate_ramp_Bias:
            #first sweep Vb to -18 V
            
            
            VBG = 6 # K2502 negative output
                
            smu_g1.set_volt(V1, VBG) # Sweep Vb from V1 to Vb
                
            V1 = VBG   # V1 is the current voltage of K2502
                  
            
            V_step = abs(Bias) / smu_g2.volt.step
            smu_g2.volt(Bias)
            sleep(smu_g2.volt.inter_delay * V_step * 5)
            first_gate_ramp_Bias = False
        else:
            smu_g2.volt(Bias)
                
        sleep(delay*5)                    




        
        
   
        for Vt in Vt_vals:          
            file = open(file_dir,"a")
            data_list = []
            
            if first_gate_ramp:
                V_step = abs(Vt) / smu_g3.volt.step
                smu_g3.volt(Vt)
                sleep(smu_g3.volt.inter_delay * V_step * 5)
                first_gate_ramp = False
            else:
                smu_g3.volt(Vt)            
            

            
            # Data reading leak current
            i_g1 = smu_g1.curr()  # Vb
            if abs(i_g1) > 10e-9:
                raise ValueError
            
            i_g2 = smu_g2.curr() # Vt
            if abs(i_g2) > 10e-9:
                raise ValueError
                
            i_g3 = smu_g3.curr() # Bias
            if abs(i_g3) > 10e-9:
                raise ValueError
                
            sleep(delay*5)  
            
            
                
                
            first_gate_ramp_Vb = True    
               
            for Vb in Vb_vals:
                
                if first_gate_ramp_Vb:
                    VBG = -Vb # K2502 negative output
                    
                    smu_g1.set_volt(V1, VBG) # Sweep Vb from V1 to Vb
                    
                    V1 = VBG   # V1 is the current voltage of K2502
                    
                    sleep (delay*5)
                    
                    first_gate_ramp_Vb = False
                
                else:

                    VBG = -Vb # K2502 negative output
                    
                    smu_g1.set_volt(V1, VBG) # Sweep Vb from V1 to Vb
                    
                    V1 = VBG   # V1 is the current voltage of K2502

                            
                                
                #VX1 = lockin1.VX()
                #P1 = lockin1.P()
                #VX2 = lockin2.VX()
                #P2 = lockin2.P()
                #VX3 = lockin3.VX()
                #P3 = lockin3.P()
                DeltaV = K6221DeltaV.delta_read()
                
                R1 = DeltaV/i_sd
                #R2 = VX2/i_sd/10
                #R2 = VX2/i_sd/amp
                #R3 = VX3/i_sd
                
                dataset = [Bias, Vt, Vb, R1, 0, 0, 0, i_g1, i_g2, i_g3]
                file.write("\t".join(map(str,dataset))+"\n")
                
                # Prepare data for plotting
                if to_plot:
                    i = -int(round((Vt-Vt_start)/Vt_step))
                    j = int(round((Vb-Vb_start)/Vb_step))
                    result1[i,j] = R1
                    #result2[i,j] = R2
                    
                    data_list.append(dataset)
                    data = np.array(data_list)
                    
                    line1.set_data(data[:,2],data[:,3])
                    ax1.relim()
                    ax1.autoscale_view(True,True,True)
                    
    
                    
                    
                    map5.set_data(result1)
                    map5.autoscale()
                    # ann5.remove()
                    # ann5 = ax5.annotate(DD, xy=(1, (i+0.5)/len(DD_vals)), 
                    #              xycoords='axes fraction', fontsize=10, color = 'w', 
                    #              xytext=(10, 0), textcoords='offset points',
                    #              ha='left', va='center', fontweight='bold',
                    #              bbox=dict(boxstyle='angled', fc='red', ec='none'))
                    
                    f.canvas.draw()
                    plt.pause(0.01)
                     
            
            file.close()
            #nn_vals = np.flip(nn_vals)
            
except KeyboardInterrupt:
    print('Measurement is interrupted.')
    file.close()


    smu_g2.volt(0)
    smu_g1.set_volt(V1, 0)
    V1 = 0
    smu_g3.volt(0)
    
    exit()
except ValueError:
    print('Gate is leaking')
    file.close()
    smu_g2.volt(0)
    smu_g1.set_volt(V1, 0)
    V1 = 0
    smu_g3.volt(0)
    
    exit()
finally:
    
    file.close()
    
    smu_g2.volt(0)
    smu_g1.set_volt(V1, 0)
    V1 = 0
    smu_g3.volt(0)
    print('Measurement is done. ')
    print(datetime.now().strftime('%H:%M:%S'))
    # if field_ramp_down:
    #     while not ami.exit_persistent_mode():
    #         pass
    #     ami.switch_heater.on()
    #     ami.field(0)
    #     ami.wait_while_ramping()
    #     print("Cooling Switch")
    #     print(datetime.now().strftime('%H:%M:%S'))
    #     while not ami.enter_persistent_mode():
    #         pass
    
    # print('Field at {0}T.'.format(ami.field()))
    qc.Instrument.close_all()
    