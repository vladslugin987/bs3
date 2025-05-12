# -*- coding: utf-8 -*-

import multiprocessing as mp
from multiprocessing.sharedctypes import RawArray, RawValue
from ctypes import c_int
import time
import random

# Uebung 2, Aufgabe 2
# Shared memory objects
shared_array = None
next_position = None

def process_1():
    """Process that writes '1' to the array 10 times."""
    global shared_array, next_position
    
    for _ in xrange(10):
        # Get the current free position
        pos = next_position.value
        
        # Write value to array if position is valid
        if 0 <= pos < len(shared_array):
            shared_array[pos] = 1
            
        # Increment the position counter
        next_position.value += 1
        
        # Small random sleep to increase chance of race conditions
        time.sleep(random.uniform(0, 0.001))

def process_2(delay_iterations=1000000):
    """Process that writes '2' to the array 10 times with delay."""
    global shared_array, next_position
    
    for _ in xrange(10):
        # Get the current free position
        pos = next_position.value
        
        # Delay loop (just burning CPU cycles)
        for _ in xrange(delay_iterations):
            pass
        
        # Write value to array if position is valid
        if 0 <= pos < len(shared_array):
            shared_array[pos] = 2
            
        # Increment the position counter
        next_position.value += 1
        
        # Small random sleep to increase chance of race conditions
        time.sleep(random.uniform(0, 0.001))

def run_experiment(start_order, delay_iterations):
    """Run the experiment with specified parameters."""
    global shared_array, next_position
    
    # Initialize shared memory
    shared_array = RawArray(c_int, 20)
    next_position = RawValue(c_int, 0)
    
    # Initialize array with zeros
    for i in xrange(len(shared_array)):
        shared_array[i] = 0
    
    # Create processes
    p1 = mp.Process(target=process_1)
    p2 = mp.Process(target=process_2, args=(delay_iterations,))
    
    # Start processes in the specified order
    if start_order == "p1_first":
        p1.start()
        time.sleep(0.01)  # Small delay between process starts
        p2.start()
    else:  # p2_first
        p2.start()
        time.sleep(0.01)  # Small delay between process starts
        p1.start()
    
    # Wait for both processes to complete
    p1.join()
    p2.join()
    
    # Return the final state of the array
    return list(shared_array)

if __name__ == "__main__":
    # Test different configurations
    test_configs = [
        ("p1_first", 100),       # Process 1 first, short delay
        ("p2_first", 100),       # Process 2 first, short delay
        ("p1_first", 10000),     # Process 1 first, medium delay
        ("p2_first", 10000),     # Process 2 first, medium delay
        ("p1_first", 1000000),   # Process 1 first, long delay
        ("p2_first", 1000000),   # Process 2 first, long delay
    ]
    
    # Run each configuration multiple times
    for start_order, delay in test_configs:
        print "\nConfiguration: Start order = %s, Delay iterations = %d" % (start_order, delay)
        
        # Run 3 times with the same configuration
        for run in xrange(3):
            result = run_experiment(start_order, delay)
            
            # Count occurrences of each value
            ones = result.count(1)
            twos = result.count(2)
            zeros = result.count(0)
            
            print "Run %d: %s" % (run+1, result)
            print "Counts: 1s=%d, 2s=%d, 0s=%d" % (ones, twos, zeros)
