from a import *

def worker_my():
    while True:
        worker()

def main_my():
    ts = []
    for _ in range(500):
        t = threading.Thread(target=worker_my)
        t.start()
        ts.append(t)
    for t in ts:
        t.join()

if __name__ == '__main__':
    main_my()
