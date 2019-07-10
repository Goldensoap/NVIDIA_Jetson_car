import multiprocessing as mp
import numpy as np
import time

def option():
    a1 = np.asmatrix(np.random.rand(1000,1000))
    a2 = np.asmatrix(np.random.rand(1000,1000))
    for i in range(10000):
        a3 = a1*a2

if __name__ == "__main__":
    start = time.time()
    option()
    option()
    stop = time.time()
    print('单进程耗时'+str(stop-start))
    start = time.time()
    p1 = mp.Process(target = option)
    p2 = mp.Process(target = option)
    p1.start()
    p2.start()
    p1.join()
    p2.join()
    stop = time.time()
    print('双进程耗时'+str(stop-start))