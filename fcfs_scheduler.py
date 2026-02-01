"""
Concept: Process Scheduling - FCFS
Topic: First Come First Serve Simulation
Description: 
A simulation showing how the OS schedules processes in the order 
they arrive. Essential for understanding batch data pipelines.
"""

def calculate_fcfs(processes, burst_time):
    n = len(processes)
    waiting_time = [0] * n
    turnaround_time = [0] * n

    # 1. Waiting Time: Pehle process ka intezar 0 hota hai
    for i in range(1, n):
        waiting_time[i] = burst_time[i-1] + waiting_time[i-1]

    # 2. Turnaround Time: Burst Time + Waiting Time
    for i in range(n):
        turnaround_time[i] = burst_time[i] + waiting_time[i]

    # Display Results
    print(f"{'Process':<10} | {'Burst Time':<12} | {'Waiting Time':<13} | {'Turnaround Time'}")
    print("-" * 60)
    
    total_wt = 0
    total_tat = 0
    for i in range(n):
        total_wt += waiting_time[i]
        total_tat += turnaround_time[i]
        print(f"P{processes[i]:<9} | {burst_time[i]:<12} | {waiting_time[i]:<13} | {turnaround_time[i]}")

    print("-" * 60)
    print(f"Average Waiting Time: {total_wt/n:.2f}")
    print(f"Average Turnaround Time: {total_tat/n:.2f}")

# Example Processes (e.g., 3 Data Cleaning Tasks)
process_ids = [1, 2, 3]
burst_times = [10, 5, 8] # Time taken by each task

calculate_fcfs(process_ids, burst_times)