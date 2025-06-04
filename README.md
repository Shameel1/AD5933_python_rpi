
# AD5933 Raspberry Pi Impedance Measurement & Fault Detection

This project provides a complete Python-based workflow for measuring and analyzing impedance using the **Analog Devices AD5933 Evaluation Board (EVAL-AD5933EBZ)** and a **Raspberry Pi** over I²C. The system is designed for applications such as **monitoring piezoelectric materials**, performing **fault detection**, and capturing sweep-based impedance data.

---

## 🧩 System Overview

- **Board**: Analog Devices EVAL-AD5933EBZ
- **Controller**: Raspberry Pi (with I²C enabled)
- **Communication**: I²C (SDA/SCL)
- **Calibration Resistor**: 200 kΩ standard resistor
- **Target System**: Piezoelectric material or other impedance-based system (Device Under Test)
- **Secondary MCU**: Arduino (connected via USB `/dev/ttyACM0` @ 9600 baud)
- **Software**: Python 3 with `smbus`, `pandas`, `matplotlib`, and `scikit-learn`

---

## 🔌 Wiring

| EVAL-AD5933EBZ Pin | Raspberry Pi Connection |
|--------------------|-------------------------|
| **T7 (VIN)**       | One terminal of calibration resistor or DUT |
| **T8 (VOUT)**      | Other terminal of calibration resistor or DUT |
| **SCL**            | Pi GPIO SCL (e.g., GPIO3 / Pin 5) |
| **SDA**            | Pi GPIO SDA (e.g., GPIO2 / Pin 3) |
| **+5V**            | Pi 5V (Pin 2 or 4) |
| **GND**            | Pi GND (Pin 6) |

| Arduino Connection | Function |
|--------------------|----------|
| `/dev/ttyACM0`     | NeoPixel control (status indication) |

| Raspberry Pi GPIO | Function       |
|-------------------|----------------|
| GPIO5             | Button Input (active low) |

---

## 🧪 Measurement Workflow

### 🔹 1. Collect Baseline Data
Start with collecting 5 clean, fault-free trials:

```bash
python3 save_base_data.py
````

### 🔹 2. Visualize and Verify

Check for inconsistencies or noise:

```bash
python3 plot_them.py
```

If discrepancies exist, troubleshoot and repeat the data collection.

### 🔹 3. Average Baseline

Once verified, compute the average baseline for fault detection:

```bash
python3 average_base.py
```

This generates `base.csv`, which is used for MSE comparison in fault detection.

### 🔹 4. Run Measurement and Detection

Now run the main program:

```bash
python3 impedance_measure.py
```

* The system will initialize and wait.
* Press the **button on GPIO5** to begin each measurement.

---

## 🧠 LED Feedback (via Arduino)

The Arduino controls a 7-LED NeoPixel strip and indicates system status:

| LED Color | Meaning                      |
| --------- | ---------------------------- |
| 🔵 Blue   | Measurement in progress      |
| 🟢 Green  | No fault detected            |
| 🔴 Red    | Fault detected or error      |
| ⚫ Off     | Idle state / ready for input |

The blue LEDs animate incrementally (1–7) during the sweep, giving a visual "loading" effect.

---

## 📦 Dependencies

Install required Python libraries:

```bash
sudo apt install python3-pip i2c-tools
pip3 install pandas matplotlib scikit-learn
```

Enable I²C on your Pi via `raspi-config` if not already:

```bash
sudo raspi-config
# Interfacing Options > I2C > Enable
```

---

## ⚙️ Fault Detection Logic

The system compares the current impedance sweep with the averaged baseline using **Mean Squared Error (MSE)**:

```python
from sklearn.metrics import mean_squared_error
mse = mean_squared_error(base_values, new_sweep)
```

| MSE Value | Interpretation    |
| --------- | ----------------- |
| ≤ 300     | ✅ Healthy system  |
| > 300     | ⚠️ Fault detected |

---

## 🛠 Troubleshooting

* Run `i2cdetect -y 1` to check if AD5933 is visible (`0x0D`)
* Make sure `base.csv` exists and matches the expected point count
* Ensure the Arduino is on `/dev/ttyACM0` and the NeoPixel code is flashed
* Button must be wired with pull-up (NO type); default state should be high

---

## 👤 Author

Shameel Abdulla
2025 – Qatar



