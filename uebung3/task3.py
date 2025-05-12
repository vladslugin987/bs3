# -*- coding: utf-8 -*-

import multiprocessing as mp
from multiprocessing.sharedctypes import RawArray
from ctypes import c_long
import random
import time

NUM_ACCOUNTS = 100
INITIAL_BALANCE = 1000
NUM_TRANSACTIONS = 150  # Increased number of transactions
DELAY_ITERATIONS = 1500000  # Significantly increased delay

## Aufgabe 3
# Version 1: Slow transaction function that may lead to race conditions
def fuehreTransaktionDurch_langsam(accounts, account1, account2, amount):
    """
    Performs a transaction between two accounts with a delay (slow version).
    """
    # Read current balances
    balance1 = accounts[account1]
    balance2 = accounts[account2]
    
    # Simulate processing time (increases chance of race conditions)
    for _ in xrange(DELAY_ITERATIONS):
        pass
    
    # Update balances
    accounts[account1] = balance1 - amount
    accounts[account2] = balance2 + amount

# Version 2: Fast transaction function
def fuehreTransaktionDurch_schnell(accounts, account1, account2, amount):
    """
    Performs a transaction between two accounts immediately (fast version).
    """
    accounts[account1] -= amount
    accounts[account2] += amount

# Version 3: Transaction function with a global lock
def fuehreTransaktionDurch_mit_lock(accounts, account1, account2, amount, lock):
    """
    Performs a transaction between two accounts using a global lock.
    """
    lock.acquire()
    try:
        # Read current balances
        balance1 = accounts[account1]
        balance2 = accounts[account2]
        
        # Simulate processing time
        for _ in xrange(10000):
            pass
        
        # Update balances
        accounts[account1] = balance1 - amount
        accounts[account2] = balance2 + amount
    finally:
        lock.release()

# Version 4: Transaction function with individual account locks
def fuehreTransaktionDurch_mit_account_locks(accounts, account1, account2, amount, locks):
    """
    Performs a transaction between two accounts using individual account locks.
    """
    # Acquire locks in order of account numbers to prevent deadlocks
    first_lock = min(account1, account2)
    second_lock = max(account1, account2)
    
    locks[first_lock].acquire()
    locks[second_lock].acquire()
    
    try:
        # Read current balances
        balance1 = accounts[account1]
        balance2 = accounts[account2]
        
        # Simulate processing time
        for _ in xrange(10000):
            pass
        
        # Update balances
        accounts[account1] = balance1 - amount
        accounts[account2] = balance2 + amount
    finally:
        # Release locks in reverse order
        locks[second_lock].release()
        locks[first_lock].release()

# Process function for executing multiple transactions
def process_function(process_id, transaction_func, accounts, iterations=NUM_TRANSACTIONS, lock=None, account_locks=None):
    """
    Process that performs multiple transactions.
    """
    random.seed(process_id)  # Different seed for each process
    
    for i in xrange(iterations):
        # Choose two different random accounts
        account1 = random.randint(0, NUM_ACCOUNTS - 1)
        account2 = random.randint(0, NUM_ACCOUNTS - 1)
        while account2 == account1:
            account2 = random.randint(0, NUM_ACCOUNTS - 1)
        
        # Random amount between 1 and 100
        amount = random.randint(1, 100)
        
        # Execute transaction using the selected function
        if lock is not None and account_locks is None:
            transaction_func(accounts, account1, account2, amount, lock)
        elif account_locks is not None:
            transaction_func(accounts, account1, account2, amount, account_locks)
        else:
            transaction_func(accounts, account1, account2, amount)

def verify_total_balance(accounts, expected_total):
    """
    Verifies that the total balance across all accounts is correct.
    """
    actual_total = sum(accounts)
    return actual_total == expected_total

def main():
    # Initialize shared account array
    accounts = RawArray(c_long, NUM_ACCOUNTS)
    
    # Set initial balance for each account
    for i in xrange(NUM_ACCOUNTS):
        accounts[i] = INITIAL_BALANCE
    
    expected_total = INITIAL_BALANCE * NUM_ACCOUNTS
    
    print "\n=== a) Demonstration von Race Conditions ==="
    
    # Create two processes both using the slow transaction function
    p1 = mp.Process(target=process_function, args=(1, fuehreTransaktionDurch_langsam, accounts))
    p2 = mp.Process(target=process_function, args=(2, fuehreTransaktionDurch_langsam, accounts))
    
    # Start processes
    start_time = time.time()
    p1.start()
    p2.start()
    
    # Wait for processes to complete
    p1.join()
    p2.join()
    elapsed_time = time.time() - start_time
    
    # Verify results
    actual_total = sum(accounts)
    balance_ok = actual_total == expected_total
    
    print "Gesamtsaldo korrekt: %s" % balance_ok
    print "Tatsächlicher Gesamtsaldo: %d, Erwarteter Gesamtsaldo: %d, Differenz: %d" % (actual_total, expected_total, actual_total - expected_total)
    
    # Print sample account balances
    print "Beispiel Kontostände:"
    for i in range(5):
        print "Konto %d: %d" % (i, accounts[i])
    
    print "Ausführungszeit ohne Locks: %.4f Sekunden" % elapsed_time
    
    print "\n=== b) Verwendung eines globalen Locks ==="
    
    # Reset account balances
    for i in xrange(NUM_ACCOUNTS):
        accounts[i] = INITIAL_BALANCE
    
    # Create global lock
    global_lock = mp.Lock()
    
    # Create processes with lock
    p1 = mp.Process(target=process_function, args=(1, fuehreTransaktionDurch_mit_lock, accounts, NUM_TRANSACTIONS, global_lock))
    p2 = mp.Process(target=process_function, args=(2, fuehreTransaktionDurch_mit_lock, accounts, NUM_TRANSACTIONS, global_lock))
    
    # Start and wait for processes
    start_time = time.time()
    p1.start()
    p2.start()
    p1.join()
    p2.join()
    elapsed_time = time.time() - start_time
    
    # Verify results
    balance_ok = verify_total_balance(accounts, expected_total)
    print "Gesamtsaldo korrekt: %s" % balance_ok
    print "Gesamtsaldo: %d (Erwartet: %d)" % (sum(accounts), expected_total)
    print "Ausführungszeit mit globalem Lock: %.4f Sekunden" % elapsed_time
    
    print "\n=== c) Verwendung von individuellen Konto-Locks ==="
    
    # Reset account balances
    for i in xrange(NUM_ACCOUNTS):
        accounts[i] = INITIAL_BALANCE
    
    # Create individual locks for each account
    account_locks = [mp.Lock() for _ in xrange(NUM_ACCOUNTS)]
    
    # Create processes with account locks
    p1 = mp.Process(target=process_function, args=(1, fuehreTransaktionDurch_mit_account_locks, accounts, NUM_TRANSACTIONS, None, account_locks))
    p2 = mp.Process(target=process_function, args=(2, fuehreTransaktionDurch_mit_account_locks, accounts, NUM_TRANSACTIONS, None, account_locks))
    
    # Start and wait for processes
    start_time = time.time()
    p1.start()
    p2.start()
    p1.join()
    p2.join()
    elapsed_time = time.time() - start_time
    
    # Verify results
    balance_ok = verify_total_balance(accounts, expected_total)
    print "Gesamtsaldo korrekt: %s" % balance_ok
    print "Gesamtsaldo: %d (Erwartet: %d)" % (sum(accounts), expected_total)
    print "Ausführungszeit mit Konto-Locks: %.4f Sekunden" % elapsed_time
    
    print "\n=== d) Vorteile und Nachteile ==="
    print """
Vorteile von individuellen Konto-Locks:
1. Erhöhte Parallelität: Transaktionen zwischen verschiedenen Konten können gleichzeitig stattfinden
2. Bessere Leistung: Weniger Konflikte im Vergleich zu einem globalen Lock
3. Feinere Granularität: Nur die tatsächlich an der Transaktion beteiligten Konten werden gesperrt

Nachteile und Herausforderungen:
1. Deadlock-Risiko: Wenn Locks nicht in konsistenter Reihenfolge erworben werden
2. Erhöhte Komplexität: Verwaltung mehrerer Locks erforderlich
3. Höherer Overhead: Erstellung und Verwaltung vieler Locks erfordert mehr Ressourcen
4. Möglichkeit von Kaskadenverzögerungen, wenn häufig verwendete Konten oft gesperrt sind
"""

if __name__ == "__main__":
    main()
