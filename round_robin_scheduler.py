"""
Concept: Process Scheduling - Round Robin
Topic: Time-Slicing and Fair Scheduling
Description: 
Simulates how modern OS handles multitasking by giving each 
process a 'Time Quantum'. Prevents the 'Convoy Effect'.
"""

def calculate_round_robin(processes, burst_time, quantum):
    n = len(processes)
    rem_bt = list(burst_time) # Remaining burst time
    wt = [0] * n # Waiting time
    t = 0 # Current time

    while True:
        done = True
        for i in range(n):
            if rem_bt[i] > 0:
                done = False # Process abhi baqi hai
                
                if rem_bt[i] > quantum:
                    t += quantum
                    rem_bt[i] -= quantum
                else:
                    t = t + rem_bt[i]
                    wt[i] = t - burst_time[i]
                    rem_bt[i] = 0
        
        if done:
            break

    # Results Display
    print(f"Time Quantum: {quantum}")
    print(f"{'Process':<10} | {'Burst Time':<12} | {'Waiting Time':<13} | {'Turnaround Time'}")
    print("-" * 65)
    
    total_wt, total_tat = 0, 0
    for i in range(n):
        tat = burst_time[i] + wt[i]
        total_wt += wt[i]
        total_tat += tat
        print(f"P{processes[i]:<9} | {burst_time[i]:<12} | {wt[i]:<13} | {tat}")

    print("-" * 65)
    print(f"Average Waiting Time: {total_wt/n:.2f}")
    print(f"Average Turnaround Time: {total_tat/n:.2f}")

# Example Data
p_ids = [1, 2, 3]
b_times = [10, 5, 8]
time_slice = 2

calculate_round_robin(p_ids, b_times, time_slice)