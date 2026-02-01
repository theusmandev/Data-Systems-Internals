"""
Concept: Spatial Locality & Memory Layout
Topic: Row-Major vs Column-Major Access Speed
Description: 
This script demonstrates how accessing data in the same order it is 
stored in memory (Row-Major for NumPy) is significantly faster than 
jumping across memory addresses (Column-Major).
"""

import numpy as np
import time

# 10k x 10k ka matrix (Row-Major by default in NumPy)
size = 10000
matrix = np.ones((size, size))

# --- 1. Row-wise Access (Efficient) ---
# Memory mein data row-by-row para hai, aur hum bhi row-by-row utha rahe hain.
start_time = time.time()
row_sum = 0
for i in range(size):
    for j in range(size):
        row_sum += matrix[i, j]  # i (row) pehle, j (col) baad mein
print(f"Row-wise time: {time.time() - start_time:.4f} seconds")

# --- 2. Column-wise Access (Inefficient) ---
# Data row-wise para hai, lekin hum jump kar ke column-by-column utha rahe hain.
start_time = time.time()
col_sum = 0
for j in range(size):
    for i in range(size):
        col_sum += matrix[i, j]  # j (col) pehle scan ho raha hai
print(f"Column-wise time: {time.time() - start_time:.4f} seconds")