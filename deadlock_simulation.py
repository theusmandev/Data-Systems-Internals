"""
Concept: Process Management - Deadlock
Topic: Resource Contention and Circular Wait
Description: 
A simulation where two threads (processes) try to acquire two locks 
in reverse order, leading to a permanent system hang (Deadlock).
"""

import threading
import time

# Do resources (Locks) banayen
resource_A = threading.Lock()
resource_B = threading.Lock()

def process_one():
    print("Process 1: Trying to acquire Resource A...")
    with resource_A:
        print("Process 1: Acquired Resource A. Now trying for Resource B...")
        time.sleep(1) # Simulation delay
        with resource_B:
            print("Process 1: Acquired both resources!")

def process_two():
    print("Process 2: Trying to acquire Resource B...")
    with resource_B:
        print("Process 2: Acquired Resource B. Now trying for Resource A...")
        time.sleep(1) # Simulation delay
        with resource_A:
            print("Process 2: Acquired both resources!")

# Threads start karein
t1 = threading.Thread(target=process_one)
t2 = threading.Thread(target=process_two)

print("--- Starting Deadlock Simulation ---")
t1.start()
t2.start()

t1.join()
t2.join()
print("Simulation Finished (If you see this, there was NO deadlock)")