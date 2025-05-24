from assets.peaks import peaks
from assets.topsEdgesGraph import edges
from assets.routesTimeing import routeTime
from tkinter import END
from tkinter import messagebox

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
        self.mapCanvas = None
        self.routes = []
        self.currListbox = []
        self.routesCanvaIDs = []
        self.importTopsNames()
        self.importRoutes()
        self.adjGraph = self.createAadjacencyGraph()
        self.edgeWeights = routeTime
        self.topsAmnt = 0
    
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
    
    def createAadjacencyGraph(self):
        """
        Creates graph where
        G[topIdx] = [(neighbourTopIdx,edgeIdx),...]
        and counts tops
        :return:
        """
        self.topsAmnt = 0
        for top1,top2 in edges:
            self.topsAmnt = max(self.topsAmnt,top1,top2)
        
        adjGraph = [[] for _ in range(self.topsAmnt+1)]
        for edgeIdx,(top1, top2) in enumerate(edges):
            adjGraph[top1].append((top2, edgeIdx))
            adjGraph[top2].append((top1, edgeIdx))
        
        self.topsAmnt += 1
        return adjGraph
        
    
    # Start-End ADD handling functions
    def addTop(self, entryIdx,topType):
        name = self.routeHandling[entryIdx].get()
        if name not in self.topsNames:
            return
        
        topID = self.topsNames.index(name)
        try:
            self.isValidNewTop(topID,topType)
            if topType == 0:
                self.start = topID
            elif topType == 1:
                self.end = topID
            elif topType == 2:
                self.hikingStops.append(topID)
            self.updateMapPahtVis()
        except ValueError as e:
            messagebox.showerror("Input error: ", str(e))
    
    
    def isValidNewTop(self,newTopID,topType):
        """
        Checks if the new top is valid, with condition that no 2 neighbournig tops can be the same.
        Prevents from adding more that 3 hiking stops.
        :param newTopID:
        :param topType:
        :return:
        """
        match topType:
            case 0:
                fullRoute = [newTopID] + self.hikingStops + [self.end]
            case 1:
                fullRoute = [self.start] + self.hikingStops + [newTopID]
            case 2:
                if len(self.hikingStops) >= 3:
                    raise ValueError("Nie można dodać więcej niż 3 przystanki.")
                fullRoute = [self.start] + self.hikingStops + [newTopID] + [self.end]
            case _:
                fullRoute = []
        
        fullRouteCleaned = [top for top in fullRoute if top is not None]
        
        if len(fullRouteCleaned) < 2:
            return True
        
        for i in range(len(fullRouteCleaned)-1):
            if fullRouteCleaned[i] == fullRouteCleaned[i+1]:
                raise ValueError("Sąsiednie punkty na trasie nie mogą być takie same.")
        return True
    
    def eraseRoutesFromCanvas(self):
        for line_id in self.routesCanvaIDs:
            self.mapCanvas.delete(line_id)
        self.routesCanvaIDs = []
    
    def makeListboxBind(self,entry, listbox):
        listbox.bind("<<ListboxSelect>>", lambda e: selectFromListbox(listbox, entry))
        entry.bind("<KeyRelease>", lambda e: updateListbox(entry, listbox, self.topsNames))
    
    def findShortestPath(self, top1Idx, top2Idx):
        """
        Returns list of edge indices for shortest path from top1Idx to top2Idx
        using Dijkstra's algorithm.
        """
        import heapq
        dist = [float("inf")] * len(self.adjGraph)
        prev = [None] * len(self.adjGraph)
        prevEdge = [None] * len(self.adjGraph)
        
        dist[top1Idx] = 0
        heap = [(0, top1Idx)]
        
        while heap:
            currDist, u = heapq.heappop(heap)
            if currDist > dist[u]:
                continue
            if u == top2Idx:
                break
            
            for v, edgeIdx in self.adjGraph[u]:
                weight = self.edgeWeights[edgeIdx]
                if dist[v] > dist[u] + weight:
                    dist[v] = dist[u] + weight
                    prev[v] = u
                    prevEdge[v] = edgeIdx
                    heapq.heappush(heap, (dist[v], v))
        
        path = []
        curr = top2Idx
        while prev[curr] is not None:
            path.append(prevEdge[curr])
            curr = prev[curr]
        
        if curr != top1Idx:
            return []
        
        path.reverse()
        return path
    
    def updateMapPahtVis(self):
        """
        Creates list of paths (path - list of edgesID) between chosen points and draws it on canvas.
        Handles all inputs combinations whether user wrote only (with condition that tops amount>2)
            - start + stop
            - stop + end
            - start + stops + end
            ... ect.
        """
        
        self.eraseRoutesFromCanvas()
        
        routePoints = [self.start] + self.hikingStops + [self.end]
        routePoints = [p for p in routePoints if p is not None]
        print(routePoints)
        if len(routePoints) < 2:
            return
        
        allPaths = [
            self.findShortestPath(a, b)
            for a, b in zip(routePoints, routePoints[1:])
        ]
        
        for path in allPaths:
            for edgeIdx in path:
                ids = drawRoute(self.mapCanvas,self.routes[edgeIdx])
                self.routesCanvaIDs += ids
                
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
            fill='purple',
            width=3,
            tags=tag
        )
        ids.append(lineID)
    
    return ids

