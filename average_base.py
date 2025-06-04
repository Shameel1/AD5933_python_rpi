# average_base.py

import pandas as pd
import numpy as np

# Load all 5 sweeps
dfs = [pd.read_csv(f"data/sweep_{i}.csv") for i in range(1, 6)]

# Concatenate into one DataFrame
combined = pd.concat(dfs, axis=1)

# Drop extra headers
combined.columns = [f"sweep_{i}" for i in range(1, 6)]

# Compute row-wise average
combined['average'] = combined.mean(axis=1)

# Save base
combined[['average']].to_csv("data/base.csv", index=False)
print("✅ Saved base.csv (averaged impedance)")
