from multiprocessing import Process, Queue
from menu.menu import runMenu
from map3D.mapProcess import runMap
import argparse

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--menu",action="store_true", help="Activate only menu")
    parser.add_argument("--map",action="store_true", help="Activate only map")
    args = parser.parse_args()
    
    config_queue = Queue()
    
    if args.menu:
        runMenu(config_queue)
    if args.map:
        runMap(config_queue)
    else:
    
        menu_proc = Process(target=runMenu, args=(config_queue,))
        map_proc = Process(target=runMap, args=(config_queue,))
    
        menu_proc.start()
        map_proc.start()
    
        menu_proc.join()
        map_proc.join()