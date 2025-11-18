import numpy as np
capacitance = 1.25e-9
frequency = 32000
impedance = 1/(2*np.pi*frequency*capacitance)/1000
print(f"Resistor should be {impedance:.2f}kOhm")

resistor = 3.865
frequency = 1/(2*np.pi*resistor*capacitance)/1000
print(f"Frequency should be {frequency:.2f}kHz")

#GAIN used = 
