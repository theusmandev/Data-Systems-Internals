


import pandas as pd
import time
import os

# Script ki maujooda location hasil karna
base_dir = os.path.dirname(os.path.abspath(__file__))

# Path join karna (ye folder structure ke mutabiq automatic adjust ho jaye ga)
row_csv_path = os.path.join(base_dir, "Data", "audible_row_major.csv")
col_csv_path = os.path.join(base_dir, "Data", "audible_col_major.csv")


def benchmark_csv(file_path, mode="Row"):
    print(f"\n--- Testing {mode}-Oriented CSV ---")
    
    # 1. Loading Speed
    start = time.time()
    df = pd.read_csv(file_path)
    load_time = time.time() - start
    print(f"Load Time: {load_time:.4f} seconds")

    # 2. Memory Usage
    memory = df.memory_usage(deep=True).sum() / (1024**2) # MBs mein
    print(f"Memory Footprint: {memory:.2f} MB")

    # 3. Analytical Operation (Sum of Price)
    # Agar column file hai to humein transpose karke ya specific row uthani hogi
    start = time.time()
    if mode == "Row":
        avg = df['price'].mean()
    else:
        # File B mein 'price' index ban chuka hoga agar transpose hui hai
        # Hum assume kar rahe hain ke 'price' wali puri row ka mean lena hai
        avg = df.iloc[7, 1:].astype(float).mean() # Adjust index based on your file
    
    calc_time = time.time() - start
    print(f"Calculation Time (Mean): {calc_time:.6f} seconds")

# Benchmark run karein
benchmark_csv(row_csv_path, mode="Row")
benchmark_csv(col_csv_path, mode="Column")