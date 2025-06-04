import time
import math
import numpy as np
import smbus
import matplotlib.pyplot as plt
import csv
from sklearn.metrics import mean_squared_error
import pandas as pd

# I2C and Register Constants
AD5933_ADDR = 0x0D
INTERNAL_CLK_HZ = 16000000

# Control Register Bits
AD5933_CONTROL_RESET = 0x10
AD5933_CONTROL_INT_SYSCLK = 0x00
AD5933_STAT_DATA_VALID = 0x02

# Functional Modes
FUNC_NOP = 0x00
FUNC_INIT_START_FREQ = 0x01
FUNC_START_SWEEP = 0x02
FUNC_INC_FREQ = 0x03
FUNC_REPEAT_FREQ = 0x04
FUNC_MEASURE_TEMP = 0x09
FUNC_POWER_DOWN = 0x0A
FUNC_STANDBY = 0x0B

# Ranges
V_OUT_2000mVpp = 0
V_OUT_200mVpp = 1
V_OUT_400mVpp = 2
V_OUT_1000mVpp = 3

# Gain
GAIN_1X = 1
GAIN_5X = 0

def to_signed(val, bits=16):
    if val & (1 << (bits - 1)):
        val -= 1 << bits
    return val

class AD5933:
    def __init__(self, bus=1, clk=INTERNAL_CLK_HZ):
        self.bus = smbus.SMBus(bus)
        self.clk = clk
        self.ctrl_range = V_OUT_2000mVpp
        self.ctrl_gain = GAIN_1X
        self.gain_factor = 1.089500e-08

    def write_reg(self, reg, val):
        self.bus.write_byte_data(AD5933_ADDR, reg, val)

    def read_reg(self, reg):
        return self.bus.read_byte_data(AD5933_ADDR, reg)

    def set_reg_value(self, reg, val, nbytes):
        for byte in range(nbytes):
            self.write_reg(reg + nbytes - byte - 1, (val >> (byte * 8)) & 0xFF)

    def get_reg_value(self, reg, nbytes):
        val = 0
        for i in range(nbytes):
            val = (val << 8) | self.read_reg(reg + i)
        return val

    def control_byte(self, func):
        return (func << 4) | (self.ctrl_range << 1) | self.ctrl_gain

    def reset(self):
        self.write_reg(0x81, AD5933_CONTROL_RESET | AD5933_CONTROL_INT_SYSCLK)
        time.sleep(0.01)

    def set_range_and_gain(self, out_range, gain):
        self.ctrl_range = out_range
        self.ctrl_gain = gain
        ctrl_hb = self.control_byte(FUNC_STANDBY)
        ctrl_lb = AD5933_CONTROL_INT_SYSCLK | gain
        self.write_reg(0x80, ctrl_hb)
        self.write_reg(0x81, ctrl_lb)
        time.sleep(0.01)

    def set_freq_range(self, start_freq, freq_inc, points):
        self.start_freq = start_freq
        self.freq_inc = freq_inc
        self.points = points

        freq_start_reg = int((start_freq * 4 / self.clk) * (2**27))
        freq_inc_reg = int((freq_inc * 4 / self.clk) * (2**27))

        self.set_reg_value(0x82, freq_start_reg, 3)
        self.set_reg_value(0x85, freq_inc_reg, 3)
        self.set_reg_value(0x88, points, 2)
        self.set_reg_value(0x8A, 15, 2)  # settling cycles

    def start_sweep(self):
        self.write_reg(0x80, self.control_byte(FUNC_STANDBY))
        self.reset()
        self.write_reg(0x80, self.control_byte(FUNC_INIT_START_FREQ))
        time.sleep(0.05)
        self.write_reg(0x80, self.control_byte(FUNC_START_SWEEP))
        time.sleep(0.1)

    def wait_data_ready(self, timeout=1.0):
        start = time.time()
        while time.time() - start < timeout:
            status = self.get_reg_value(0x8F, 1)
            if status & AD5933_STAT_DATA_VALID:
                return True
            time.sleep(0.01)
        return False

    def read_complex(self):
        real = self.get_reg_value(0x94, 2)
        imag = self.get_reg_value(0x96, 2)
        return to_signed(real), to_signed(imag)

    def measure_magnitude(self):
        if not self.wait_data_ready():
            raise TimeoutError("Data not ready")
        real, imag = self.read_complex()
        return math.sqrt(real**2 + imag**2), real, imag

    def calibrate(self, known_resistor_ohm):
        self.write_reg(0x80, self.control_byte(FUNC_REPEAT_FREQ))
        mag, real, imag = self.measure_magnitude()
        if mag == 0:
            raise ValueError("Invalid magnitude for calibration")
        self.gain_factor = 1 / (mag * known_resistor_ohm)
        print(f"[CAL] |Z| = {mag:.2f}, Real = {real}, Imag = {imag}, Gain = {self.gain_factor:.6e}")

    def measure_impedance(self):
        self.write_reg(0x80, self.control_byte(FUNC_REPEAT_FREQ))
        mag, real, imag = self.measure_magnitude()
        if self.gain_factor == 0:
            raise ValueError("Gain factor not set")
        impedance = 1 / (mag * self.gain_factor) if mag > 0 else float('inf')
        return impedance, real, imag

    def sweep_impedance(self):
        zmod = []
        for i in range(self.points):
            imp, real, imag = self.measure_impedance()
            freq = self.start_freq + i * self.freq_inc
            print(f"Point {i+1}: Z = {imp:.2f} Ω @ {freq} Hz")
            zmod.append(imp)
            self.write_reg(0x80, self.control_byte(FUNC_INC_FREQ))
            time.sleep(0.05)
        return zmod


# --- Execution Block ---
if __name__ == '__main__':
    sensor = AD5933()
    sensor.set_range_and_gain(out_range=V_OUT_2000mVpp, gain=GAIN_1X)
    sensor.set_freq_range(start_freq=30000, freq_inc=20, points=200)

    #print("Starting sweep and calibration...")
    #sensor.start_sweep()
    #sensor.calibrate(known_resistor_ohm=200000)

    #input("Calibration done. Replace resistor with DUT and press Enter...")
    # Loop parameters
    iterations = 5

    for i in range(iterations):
        print(f"\n--- Measurement {i+1}/{iterations} ---")
        sensor.start_sweep()
        results = sensor.sweep_impedance()
        df = pd.DataFrame(results, columns=["Impedance (Ohms)"])
        filename = f"sweep_{i+1}.csv"
        df.to_csv(filename, index=False)
        print(f"✅ Sweep {i+1} saved to '{filename}'")


#     print("Reading impedance sweep...")
#     results = sensor.sweep_impedance()
# 
#     plt.plot(results)
#     plt.xlabel("Sweep Point")
#     plt.ylabel("Impedance (Ohms)")
#     plt.title("Impedance Sweep")
#     plt.grid(True)
#     plt.show()

