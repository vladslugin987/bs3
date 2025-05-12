import multiprocessing
import ctypes
import time

STACK_SIZE = 10
stack = multiprocessing.Array(ctypes.c_long, STACK_SIZE)
stack_pointer = multiprocessing.Value(ctypes.c_int, 0)
lock = multiprocessing.Lock()


def push(item):
    with lock:
        if stack_pointer.value >= STACK_SIZE:
            print(f"[{multiprocessing.current_process().name}] Stack Overflow")
            return
        stack[stack_pointer.value] = item
        print(f"[{multiprocessing.current_process().name}] push: {item}")
        stack_pointer.value += 1


def pop():
    with lock:
        if stack_pointer.value == 0:
            print(f"[{multiprocessing.current_process().name}] Stack Underflow")
            return None
        stack_pointer.value -= 1
        item = stack[stack_pointer.value]
        print(f"[{multiprocessing.current_process().name}] pop: {item}")
        return item


def stack_worker_push():
    for i in range(3):
        push(i)
        time.sleep(0.1)


def stack_worker_pop():
    for _ in range(3):
        pop()
        time.sleep(0.15)


if __name__ == "__main__":
    p1 = multiprocessing.Process(target=stack_worker_push, name="P1")
    p2 = multiprocessing.Process(target=stack_worker_push, name="P2")
    p3 = multiprocessing.Process(target=stack_worker_pop, name="P3")

    p1.start()
    p2.start()
    time.sleep(0.2)
    p3.start()

    p1.join()
    p2.join()
    p3.join()