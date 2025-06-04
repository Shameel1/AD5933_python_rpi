# AD5933 Raspberry Pi Impedance Measurement & Fault Detection

This project provides a complete Python-based workflow for measuring and analyzing impedance using the **Analog Devices AD5933 Evaluation Board (EVAL-AD5933EBZ)** and a **Raspberry Pi** over I²C. The system is designed for applications such as **monitoring piezoelectric materials**, performing **fault detection**, and capturing sweep-based impedance data.

---

## 🧩 System Overview

- **Board**: Analog Devices EVAL-AD5933EBZ
- **Controller**: Raspberry Pi (with I²C enabled)
- **Communication**: I²C (SDA/SCL)
- **Calibration Resistor**: 200 kΩ standard resistor
- **Target System**: Piezoelectric material or other impedance-based system (Device Under Test)
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

---

## 🧪 Measurement Workflow

### 🔧 1. **Calibration**
- Connect a **200 kΩ resistor** across the T7 (VIN) and T8 (VOUT) terminals.
- Run the script to **perform calibration** and compute the **gain factor**.

### 🔄 2. **Measurement**
- Replace the resistor with **the piezoelectric material** or DUT.
- Configure:
  - **Start Frequency**
  - **Frequency Increment**
  - **Number of Points**
- Perform an impedance **sweep**.
- Save data to CSV or proceed to fault detection.

### ⚠️ 3. **Fault Detection**
- Compare a new sweep against a previously computed **baseline average** (`base.csv`).
- Compute **Mean Squared Error (MSE)**.
- If MSE > 3000, the system flags a **fault**.

---

## 🧠 Features

- 📈 Impedance measurement via frequency sweep
- 🧪 Calibration using known resistor
- 💾 CSV data export using `pandas`
- 🧮 Fault detection using `scikit-learn` MSE
- 🖥️ Terminal-based user interface
- 🐍 Fully implemented in Python using `smbus` and standard packages

---

## 📦 Dependencies

Install required Python libraries:

```bash
sudo apt install python3-pip i2c-tools
pip3 install pandas matplotlib scikit-learn
````

Enable I2C on your Pi via `raspi-config` if not already:

```bash
sudo raspi-config
# Interfacing Options > I2C > Enable
```

---

## 🚀 Running the Program

Run the main Python script:

```bash
python3 impedance_measure.py
```

You will be prompted to:

* Calibrate using the 200kΩ resistor
* Replace with DUT and begin sweep
* Save or analyze data for faults

---

## 📊 Generating the Baseline

After saving 5 good sweeps:

```bash
python3 average_base.py
```

This creates `base.csv` from `sweep_1.csv` to `sweep_5.csv`.

---

## ⚙️ Fault Detection Logic

The system computes:

```python
from sklearn.metrics import mean_squared_error
mse = mean_squared_error(base_values, new_sweep)
```

* ✅ If MSE ≤ 3000 → system is healthy
* ⚠️ If MSE > 3000 → **Fault detected**

---

## 🛠 Troubleshooting

* Use `i2cdetect -y 1` to check if AD5933 is detected (default I²C address: `0x0D`)
* If `base.csv` not found, generate it using saved sweeps first
* Ensure proper settling time and frequency configuration for accurate data

---

## 👤 Author

Shameel Abdulla
2025 – Qatar
