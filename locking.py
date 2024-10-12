import threading

counter = 0

lock = threading.Lock()

""" lock.acquire()
lock.release() """

def increment():
    global counter
    for i in range(10**6):
        lock.acquire()
        counter += 1
        lock.release()

        """ lo mismo que...
         
        with lock:
            counter += 1
        """

threads = []

for i in range(4):
    x = threading.Thread(target=increment)
    threads.append(x)

for t in threads:
    t.start()

for t in threads:
    t.join()

print('Counter value:', counter)