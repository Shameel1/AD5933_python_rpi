import pandas as pd
import matplotlib.pyplot as plt

# Folder and file info
folder = 'data'
num_files = 3
column_name = 'Impedance (Ohms)'

dfs = []

# Load and plot each sweep
for i in range(1, num_files + 1):
    filepath = f'data/sweep_{i}.csv'
    df = pd.read_csv(filepath)
    dfs.append(df[column_name])
    plt.plot(df.index, df[column_name], color='gray', alpha=0.4)

# Combine into a DataFrame and compute mean
all_data = pd.concat(dfs, axis=1)
avg = all_data.mean(axis=1)

# Plot average in red
plt.plot(avg.index, avg.values, color='red', label='Average')

# Formatting
plt.xlabel('Index (Data Point)')
plt.ylabel('Impedance (Ohms)')
plt.title('Sweep Data with Average')
plt.legend()
plt.grid(True)
plt.tight_layout()
plt.savefig('baseline.png')
plt.show()
