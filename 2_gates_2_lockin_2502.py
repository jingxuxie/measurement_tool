#%% Import
from time import sleep
import numpy as np
import matplotlib.pyplot as plt
import qcodes as qc
from matplotlib.patches import BoxStyle
from custom_bbox import AngledBox
from os import path, makedirs
from datetime import datetime

# Drivers
from instrument_drivers.tektronix.Keithley_2450 import Keithley2450
from instrument_drivers.tektronix.Keithley_2502 import Keithley2502
from instrument_drivers.stanford_research.SR830 import SR830
from instrument_drivers.tektronix.Keithley_6221 import Keithley6221
#from instrument_drivers.american_magnetics.AMI430 import AMI430
#ami = AMI430('AMI430', address='192.168.0.40', port=7180)

# Initialisation
smu_g1 = Keithley2502('SMU1','GPIB0::24::INSTR') # outer loop
smu_g2 = Keithley2450('SMU2','GPIB0::18::INSTR')
lockin1 = SR830('SR830_1','GPIB0::08::INSTR', autorange=False)
lockin2 = SR830('SR830_2','GPIB0::09::INSTR', autorange=False)

K6221DeltaV = Keithley6221('K6221','GPIB0::12::INSTR')

#%% Input

to_plot = True;
# Input parameters
VG1_start = 16;
VG1_stop = -16;
VG1_step = 1;

VG2_start = -4;
VG2_stop = 1.5;
VG2_step = 0.001;


delay = 1;
i_sd = 1e-9;
file_dir1 = "C:\\Data\\Zuocheng\\20211229\\forward.dat"
file_dir2 = "C:\\Data\\Zuocheng\\20211229\\backward.dat"

# Range settings
smu_g1.rangei(10e-9)
smu_g1.measurerange_i(10e-9)
smu_g2.measurerange_i(10e-9)

# Ramp control
smu_g2.volt.step = 0.1
smu_g2.volt.inter_delay = .1

#%% Measurement
try:
    # File check
    d_path1 = path.dirname(file_dir1)
    if not path.exists(d_path1):
        makedirs(d_path1)
    if path.isfile(file_dir1):
        file_dir1 = file_dir1[:-4] + datetime.now().strftime('_%Y%m%d_%H%M%S') + '.dat'
    file1 = open(file_dir1,"a")
    file1.write("VBG\tVTG\tIBG\tITG\tVX1\tVY1\tVX2\tVY2\tR1\tR2\nV\tV\tA\tA\tV\tV\tV\tV\tOhm\tOhm\n") #header
    file1.close()
    
    d_path2 = path.dirname(file_dir2)
    if not path.exists(d_path2):
        makedirs(d_path2)
    if path.isfile(file_dir2):
        file_dir2 = file_dir2[:-4] + datetime.now().strftime('_%Y%m%d_%H%M%S') + '.dat'
    file2 = open(file_dir2,"a")
    file2.write("VBG\tVTG\tIBG\tITG\tVX1\tVY1\tVX2\tVY2\tR1\tR2\nV\tV\tA\tA\tV\tV\tV\tV\tOhm\tOhm\n") #header
    file2.close()
    
    # Loop parameters
    VG1_vals = np.linspace(VG1_start, VG1_stop, int(abs(round((VG1_stop-VG1_start)/VG1_step)))+1)
    VG2_vals = np.linspace(VG2_start, VG2_stop, int(abs(round((VG2_stop-VG2_start)/VG2_step)))+1)
    data_list = []
    result1 = np.zeros([len(VG1_vals),len(VG2_vals)])
    result2 = np.zeros([len(VG1_vals),len(VG2_vals)])
    
    # Canvas settings
    if to_plot:
        f = plt.figure('Dual gate resistance mapping', figsize=(20,7))
        grid = plt.GridSpec(5, 8, wspace=2, hspace=2)
        
        ax1 = f.add_subplot(grid[:2,0:2])
        ax1.set(title ="G1 leakage", xlabel ="$V_{G2} (V)$", ylabel="I (A)")
        ax1.grid(True)
        ax1.ticklabel_format(axis='y',style='sci',scilimits=(0,0))
        line1, = ax1.plot([],[],'.-')
        
        ax2 = f.add_subplot(grid[:2,2:4])
        ax2.set(title ="G2 leakage", xlabel ="$V_{G2} (V)$", ylabel="I (A)")
        ax2.grid(True)
        ax2.ticklabel_format(axis='y',style='sci',scilimits=(0,0))
        line2, = ax2.plot([],[],'.-')
        
        ax3 = f.add_subplot(grid[:2,4:6])
        ax3.set(title ="R1", xlabel ="$V_{G2} (V)$", ylabel="R (Ohm)")
        ax3.grid(True)
        ax3.ticklabel_format(axis='y',style='sci',scilimits=(0,0))
        line3, = ax3.plot([],[],'.-')
        
        ax4 = f.add_subplot(grid[:2,6:])
        ax4.set(title ="R2", xlabel ="$V_{G2} (V)$", ylabel="R (Ohm)")
        ax4.grid(True)
        ax4.ticklabel_format(axis='y',style='sci',scilimits=(0,0))
        line4, = ax4.plot([],[],'.-')
        
        BoxStyle._style_list["angled"] = AngledBox
        ratio = abs((VG2_stop-VG2_start)/(VG1_stop-VG1_start))
        
        ax5 = f.add_subplot(grid[2:,:4])
        ax5.set(title ="Resistance colormap - 1", xlabel ="VBG (V)", ylabel="VTG (V)")
        map5 = ax5.imshow(result1, origin='lower',interpolation='none',aspect=ratio, 
                           extent=[VG2_start-VG2_step/2,VG2_stop+VG2_step/2, 
                                   VG1_start-VG1_step/2,VG1_stop+VG1_step/2])
        ann5 = ax5.annotate(VG1_vals[0], xy=(1, 0.5/len(VG1_vals)), 
                             xycoords='axes fraction', fontsize=10, color = 'w', 
                             xytext=(10, 0), textcoords='offset points',
                             ha='left', va='center', fontweight='bold',
                             bbox=dict(boxstyle='angled', fc='red', ec='none'))
        
        ax6 = f.add_subplot(grid[2:,4:])
        ax6.set(title ="Resistance colormap - 2", xlabel ="VBG (V)", ylabel="VTG (V)")
        map6 = ax6.imshow(result2, origin='lower',interpolation='none',aspect=ratio, 
                           extent=[VG2_start-VG2_step/2,VG2_stop+VG2_step/2, 
                                   VG1_start-VG1_step/2,VG1_stop+VG1_step/2])
        ann6 = ax6.annotate(VG1_vals[0], xy=(1, 0.5/len(VG1_vals)), 
                             xycoords='axes fraction', fontsize=10, color = 'w', 
                             xytext=(10, 0), textcoords='offset points',
                             ha='left', va='center', fontweight='bold',
                             bbox=dict(boxstyle='angled', fc='red', ec='none'))
    
    
    # Measurement start
    V1 = 0
    first_gate_ramp = True
    #smu_g2.output.set(1)
    
   
        
    for VG1 in VG1_vals:
        smu_g1.set_volt(V1, VG1)
        V1 = VG1
        #sleep(delay)
        file1 = open(file_dir1,"a")
        file2 = open(file_dir2,"a")
        data_list = []
        sleep(delay)
        
        for forward_backward_index in range(2):
            for VG2 in VG2_vals:
                
                if first_gate_ramp:
                    V_step = abs(VG2) / smu_g2.volt.step
                    smu_g2.volt(VG2)
                    sleep(smu_g2.volt.inter_delay * V_step * 5)
                    first_gate_ramp = False
                else:
                    smu_g2.volt(VG2)
                sleep(delay)
                
                # Data readings
                i_g1 = smu_g1.curr()
                if abs(i_g1) > 5e-9:
                    raise ValueError
                i_g2 = smu_g2.curr()
                if abs(i_g2) > 5e-9:
                    raise ValueError
                
                # Data readings
                VX1 = lockin1.VX()
                VY1 = lockin1.Y()
                #VR1 = lockin1.R()
                
                VX2 = lockin2.VX()
                VY2 = lockin2.Y()
                #VR2 = lockin2.R()
                
                DeltaV = K6221DeltaV.delta_read()
                
                R1 = DeltaV/i_sd
                R2 = VX2/i_sd
                
                dataset = [-VG1, VG2, i_g1, i_g2, VX1, VY1, VX2, VY2, R1, R2]
                #dataset = [-VG1, VG2, i_g1, i_g2, DeltaV, R1]
                
                if forward_backward_index == 0:
                    file1.write( "\t".join(map(str,dataset))+"\n")
                else:
                    file2.write( "\t".join(map(str,dataset))+"\n")    
                
                # Prepare data for plotting
                if to_plot:
                    i = int(round((VG1-VG1_start)/VG1_step))
                    j = int(round((VG2-VG2_start)/VG2_step))
                    result1[i,j] = R1
                    result2[i,j] = R2
                    data_list.append(dataset)
                    data = np.array(data_list)
                    
                    line1.set_data(data[:,1],data[:,2])
                    ax1.relim()
                    ax1.autoscale_view(True,True,True)
                    
                    line2.set_data(data[:,1],data[:,3])
                    ax2.relim()
                    ax2.autoscale_view(True,True,True)
                    
                    line3.set_data(data[:,1],data[:,8])
                    ax3.relim()
                    ax3.autoscale_view(True,True,True)
                    
                    line4.set_data(data[:,1],data[:,9])
                    ax4.relim()
                    ax4.autoscale_view(True,True,True)
                    
                    f.canvas.draw()
                    plt.pause(0.01)
            
            if to_plot:
                map5.set_data(result1)
                map5.autoscale()
                ann5.remove()
                ann5 = ax5.annotate(VG1, xy=(1, (i+0.5)/len(VG1_vals)), 
                             xycoords='axes fraction', fontsize=10, color = 'w', 
                             xytext=(10, 0), textcoords='offset points',
                             ha='left', va='center', fontweight='bold',
                             bbox=dict(boxstyle='angled', fc='red', ec='none'))
                
                
#                map6.set_data(result2)
#                map6.autoscale()
#                ann6.remove()
#                ann6 = ax6.annotate(VG1, xy=(1, (i+0.5)/len(VG1_vals)), 
#                             xycoords='axes fraction', fontsize=10, color = 'w', 
#                             xytext=(10, 0), textcoords='offset points',
#                             ha='left', va='center', fontweight='bold',
#                             bbox=dict(boxstyle='angled', fc='red', ec='none'))
                    
                f.canvas.draw()
                plt.pause(0.01)
            VG2_vals = np.flip(VG2_vals)
        file1.close()
        file2.close()
            
except KeyboardInterrupt:
    print('Measurement is interrupted.')

finally:
    file1.close()
    file2.close()
    if to_plot:
        plt.savefig(file_dir1[:-4] + datetime.now().strftime('_%Y%m%d_%H%M%S') + '.png')      
    
    smu_g2.volt(0)
    smu_g1.set_volt(V1, 0)
    
    
    
    print('Measurement is done.')
    qc.Instrument.close_all()