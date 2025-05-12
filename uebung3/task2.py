# -*- coding: utf-8 -*-

import multiprocessing as mp
from multiprocessing.sharedctypes import RawValue
from ctypes import c_long
import time

# Uebung 3, Aufgabe 2
# Fast counter increment function
def erhoeheZaehler_schnell(counter):
    """Quickly increments the counter by 1."""
    counter.value += 1

# Slow counter increment function
def erhoeheZaehler_langsam(counter):
    """Increments the counter by 1 with a delay."""
    # Save the current counter value
    current_value = counter.value
    
    # Add a delay, simulating a long operation
    for _ in xrange(1000000):
        pass
    
    # Increment the counter by 1
    counter.value = current_value + 1

# Counter increment function with lock
def erhoeheZaehler_mit_lock(counter, lock):
    """Increments the counter by 1 using a lock."""
    lock.acquire()
    try:
        current_value = counter.value
        
        # Add a delay, simulating a long operation
        for _ in xrange(1000000):
            pass
        
        counter.value = current_value + 1
    finally:
        lock.release()

# Process function that calls the increment function multiple times
def process_function(increment_func, counter, iterations=50, lock=None):
    """Process that repeatedly calls the counter increment function."""
    for _ in xrange(iterations):
        if lock is not None:
            increment_func(counter, lock)
        else:
            increment_func(counter)

def main():
    # a) Two different c_long counters
    print "\na) Two different c_long counters"
    counter1 = RawValue(c_long, 0)
    counter2 = RawValue(c_long, 0)
    
    # Create and start processes
    p1 = mp.Process(target=process_function, args=(erhoeheZaehler_schnell, counter1))
    p2 = mp.Process(target=process_function, args=(erhoeheZaehler_langsam, counter2))
    
    p1.start()
    p2.start()
    p1.join()
    p2.join()
    
    print "Counter1 (schnell): %d" % counter1.value
    print "Counter2 (langsam): %d" % counter2.value
    
    # b) One shared c_long counter
    print "\nb) One shared c_long counter"
    shared_counter = RawValue(c_long, 0)
    
    # Create and start processes
    p1 = mp.Process(target=process_function, args=(erhoeheZaehler_schnell, shared_counter))
    p2 = mp.Process(target=process_function, args=(erhoeheZaehler_langsam, shared_counter))
    
    p1.start()
    p2.start()
    p1.join()
    p2.join()
    
    print "Shared counter: %d" % shared_counter.value
    
    # d) Lock for shared counter
    print "\nd) Lock for shared counter"
    shared_counter = RawValue(c_long, 0)
    lock = mp.Lock()
    
    # Create and start processes
    p1 = mp.Process(target=process_function, args=(erhoeheZaehler_mit_lock, shared_counter, 50, lock))
    p2 = mp.Process(target=process_function, args=(erhoeheZaehler_mit_lock, shared_counter, 50, lock))
    
    p1.start()
    p2.start()
    p1.join()
    p2.join()
    
    print "Shared counter with lock: %d" % shared_counter.value

if __name__ == "__main__":
    main()
