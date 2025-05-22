from assets.peaks import peaks
from tkinter import END
import os

DEFAULT_COLSPAN = 4
DEFAULT_ROWSPAN = 1

class Menu:
    def __init__(self,root):
        self.tops = peaks
        self.start = None # Stores ID of top
        self.end = None # Stores ID of top
        self.hikingStops = [] # Stores IDs of tops
        self.topsNames = []
        self.tkRoot = root
        self.routeHandling = [] # Array with entries [startEntry,endEntry,stopEntry]
        self.routeHandlingFunctions = [self.addStart,
                                       self.addEnd,
                                       self.addHikingStop]
        self.mapCanvas = None
        self.routes = []
        self.currListbox = []
        self.routesCanvaIDs = []
        self.importTopsNames()
        self.importRoutes()
    
    def importTopsNames(self):
        for i ,(name,(x,y)) in enumerate(self.tops):
            self.topsNames.append(name)
    
    def importRoutes(self):
        for i in range(33):
            with open(f"assets/Trasy/t{i}.txt",'r') as f:
                route = []
                for line in f:
                    line = line.strip()
                    if line.startswith('(') and line.endswith(')'):
                        x_str, y_str = line[1:-1].split(',')
                        x = int(x_str.strip())
                        y = int(y_str.strip())
                        route.append((x, y))
                self.routes.append(route)
        
    
    # Start-End ADD handling functions
    def addStart(self):
        routeIDs = drawRoute(self.mapCanvas, self.routes[0], "startRoute")
        self.routesCanvaIDs.append(routeIDs)
        name = self.routeHandling[0].get()
        if name in self.topsNames:
            print(name)
            self.start = self.topsNames.index(name)
        return 1
    
    def addEnd(self):
        name = self.routeHandling[1].get()
        if name in self.topsNames:
            print(name)
            self.end = self.topsNames.index(name)
        return 1
    
    def addHikingStop(self):
        name = self.routeHandling[2].get()
        self.deleteAllRoutes()
        if name in self.topsNames:
            # Not start/meta (idiot proof)
            self.hikingStops.append(self.topsNames.index(name))
        return 1
    
    def deleteAllRoutes(self):
        for ids in self.routesCanvaIDs:
            for lineID in ids:
                self.mapCanvas.delete(lineID)
    
    def makeListboxBind(self,entry, listbox):
        listbox.bind("<<ListboxSelect>>", lambda e: selectFromListbox(listbox, entry))
        entry.bind("<KeyRelease>", lambda e: updateListbox(entry, listbox, self.topsNames))


def gridPlace(widget, col, row, colspan=DEFAULT_COLSPAN, rowspan=DEFAULT_ROWSPAN):
    relx = col / 40
    rely = row / 20
    relwidth = colspan / 40
    relheight = rowspan / 20
    widget.place(relx=relx, rely=rely, relwidth=relwidth, relheight=relheight)


def updateListbox(entry,listbox,suggestions):
    typed = entry.get()
    listbox.delete(0, 'end')

    matchCount = 0
    if typed:
        for item in suggestions:
            words = item.lower().split()
            if any(word.startswith(typed.lower()) for word in words):
                listbox.insert(END, item)
                matchCount += 1
                
    if matchCount > 0:
        listbox.place(x=entry.winfo_x(), y=entry.winfo_y() + entry.winfo_height())
        listbox.config(height=min(matchCount, 10))
        listbox.lift()
    else:
        listbox.place_forget()

def selectFromListbox(listbox,entry):
    selection = listbox.curselection()
    if selection:
        selected = listbox.get(selection[0])
        entry.delete(0, END)
        entry.insert(0, selected)
        listbox.place_forget()


def drawRoute(canvas,points,tag='route_line', orgImgSize=(2048,2048), newImgSize=(600,600)):
    ox, oy = orgImgSize
    nx, ny = newImgSize

    scaledPoints = [(px * nx / ox, py * ny / oy) for (px, py) in points]

    ids = []
    for i in range(len(scaledPoints) - 1):
        lineID = canvas.create_line(
            *scaledPoints[i],
            *scaledPoints[i + 1],
            fill='red',
            width=2,
            tags=tag
        )
        ids.append(lineID)
    
    return ids

