from multiprocessing import Process, Queue
from menu.menu import runMenu
from map3D.mapProcess import runMap
import argparse

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--menu",action="store_true", help="Activate only menu")
    parser.add_argument("--map",action="store_true", help="Activate only map")
    args = parser.parse_args()
    
    configQueue = Queue()
    
    if args.menu:
        runMenu(configQueue)
    elif args.map:
        runMap(configQueue)
    else:
    
        menuProc = Process(target=runMenu, args=(configQueue,))
        mapProc = Process(target=runMap, args=(configQueue,))
    
        menuProc.start()
        mapProc.start()
    
        menuProc.join()
        mapProc.join()