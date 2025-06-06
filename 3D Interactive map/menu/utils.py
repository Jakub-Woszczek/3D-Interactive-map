from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
from assets.peaks import peaksData
from assets.routesTimeing import routeTime
from tkinter import END
from tkinter import messagebox
import numpy as np
import matplotlib.colors as mcolors
from matplotlib.patches import Polygon
from menu.graph import Graph
import tkinter as tk
from random import randint

DEFAULT_COLSPAN = 4
DEFAULT_ROWSPAN = 1

class Menu:
    def __init__(self,root):
        self.tops = peaksData       # Array of tuples with tops names and tuple of coords on map
        self.start = None           # Stores ID of top
        self.end = None             # Stores ID of top
        self.hikingStops = []       # Stores IDs of tops
        self.topsNames = []         # Stores names of tops as strings (topsNames[topIdx] = name)
        self.tkRoot = root          # Instance of tinkter window
        self.routeHandling = []     # Array with entries [startEntry,endEntry,stopEntry]
        self.mapCanvas = None       # Instance of canvas
        self.routes = []            # Array of routes, where each is list of pixel coords (one after another)
        self.routesCanvaIDs = []    # IDs of drawn line on canvas
        self.edgeWeights = routeTime # Weight of each edge idx
        self.topsAmnt = 0
        # Menu grid unit size
        self.colPixelUnit = 1920 / 40
        self.rowPixelUnit = 1080 / 20
        
        self.chartCanvas = None # Elevation chart canvas
        self.graph = Graph()
        self.travelTimeLabel = None
        self.routeGraphLabel = None
        self.progressBar = None
        self.startButton = None
        self.activeEdgedIds = None # Stores edges ids to send them in config to 3D map
        self.showManualButton = None
        
        self.importTopsNames()
        self.importRoutes()
    
    def importTopsNames(self):
        for name,(x,y) in self.tops:
            self.topsNames.append(name)
    
    def importRoutes(self):
        for i in range(33):
            with open(f"assets/Trasy/t{i}.txt",'r') as f:
                route = []
                for line in f:
                    line = line.strip()
                    if line.startswith('(') and line.endswith(')'):
                        xStr, yStr = line[1:-1].split(',')
                        x = int(xStr.strip())
                        y = int(yStr.strip())
                        route.append((x, y))
                self.routes.append(route)
    
    def addTop(self, entryIdx):
        """
        Add top to route if input in entry box is valid
        :param entryIdx: Index of entry box
        """
        entry = self.routeHandling[entryIdx]
        name = entry.get().strip()
        
        entry.config(bg="white")
        
        if name not in self.topsNames:
            entry.config(bg="lightcoral")
            return
        
        topID = self.topsNames.index(name)
        try:
            fullRoute = self.isValidNewTop(topID,entryIdx)
            if entryIdx == 0:
                self.start = topID
            elif entryIdx == 1:
                self.end = topID
            elif entryIdx == 2:
                self.hikingStops.append(topID)
            
            if len(fullRoute) > 1 : self.updateMenu()
            self.updateRouteGraphLabel()
            entry.config(bg="lightgreen")
        
        except ValueError as e:
            entry.config(bg="lightcoral")
            messagebox.showerror("Input error: ", str(e))
    
    
    def isValidNewTop(self,newTopID,topType):
        """
        Checks if the new top is valid, with condition that no 2 neighbouring tops can be the same.
        Prevents from adding more that 3 hiking stops.
        :param topType: Start/end/hiking stop
        :return: Idx of consecutive tops on the route
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
            return fullRouteCleaned
        
        for i in range(len(fullRouteCleaned)-1):
            if fullRouteCleaned[i] == fullRouteCleaned[i+1]:
                raise ValueError("Sąsiednie punkty na trasie nie mogą być takie same.")
        return fullRouteCleaned
    
    def eraseRoutesFromCanvas(self):
        """
        Erases previously drawn routed on canvas
        """
        for lineID in self.routesCanvaIDs:
            self.mapCanvas.delete(lineID)
        self.routesCanvaIDs = []
    
    def makeListboxBind(self,entry, listbox):
        listbox.bind("<<ListboxSelect>>", lambda e: selectFromListbox(listbox, entry))
        entry.bind("<KeyRelease>", lambda e: updateListbox(entry, listbox, self.topsNames))
    
    def updateMapPahtVis(self):
        """
        Creates list of paths (path - list of edgesID) between chosen points and draws it on canvas.
        Handles all inputs combinations whether user wrote only (with condition that tops amount>2)
            - start + stop
            - stop + end
            - start + stops + end
            ... ect.
        :return flattened list of edge indexes
        """
        
        self.eraseRoutesFromCanvas()
        
        routePoints = [self.start] + self.hikingStops + [self.end]
        routePoints = [p for p in routePoints if p is not None]
        if len(routePoints) < 2:
            return []
        
        allPaths = [
            self.graph.findShortestPath(a, b)
            for a, b in zip(routePoints, routePoints[1:])
        ]
        self.activeEdgedIds = [edgeId for sublist in allPaths for edgeId in sublist]
        
        for path in allPaths:
            for edgeIdx in path:
                ids = drawRoute(self.mapCanvas, self.routes[edgeIdx])
                self.routesCanvaIDs += ids
                
        return routePoints
    
    def updateChart(self,x, y, marks):
        """
        Crates and plots elevation chart
        :param x: List of x-values representing distances.
        :param y: List of y-values representing elevations.
        :param marks: List of x-values indicating the positions of mountain tops along the route.
        """
        dpi = 100
        width = self.colPixelUnit * 17 / dpi
        height = self.rowPixelUnit * 3 / dpi
        fig = Figure(figsize=(width, height), dpi=dpi)
        plot = fig.add_subplot(111)
        
        drawElevationChart(x, y, pionoweLinie=marks, ax=plot)
        
        # Del prev route from canvas
        if self.chartCanvas is not None:
            self.chartCanvas.get_tk_widget().destroy()
            
        self.chartCanvas = FigureCanvasTkAgg(fig, master=self.tkRoot)
        widget = self.chartCanvas.get_tk_widget()
        
        gridPlace(widget, 20, 8, colspan=18, rowspan=6)
        
        self.chartCanvas.draw()
    
    def updateMenu(self):
        """
        Updates GUI elements when a valid top is added.
        """
        topsIds = self.updateMapPahtVis()

        yVals,checkpoints = self.graph.getElevationProfile(topsIds)
        xVals = np.arange(len(yVals))
        
        marks = {checkPoint: self.topsNames[topsIds[i]] for i, checkPoint in enumerate(checkpoints)}
        
        self.updateChart(xVals, yVals, marks)
        self.updateTime()
    
    def updateTime(self):
        """
        Updates estimated time for travel, and actualizes it on label
        """
        fullRoute = [self.start] + self.hikingStops + [self.end]
        fullRouteCleaned = [top for top in fullRoute if top is not None]
        
        timeText = "0 h" if len(fullRouteCleaned) < 2 else f"{self.graph.getTravelTime(fullRouteCleaned)} h"
        self.travelTimeLabel.config(text=timeText)
    
    def generateRandomTopName(self):
        nameID = randint(0, len(peaksData) - 1)
        return peaksData[nameID][0]
    
    def updateRouteGraphLabel(self):
        """
        Updates the travel graph displayed as:
        top1 → top2 → ...
        """
        fullRoute = [self.start] + self.hikingStops + [self.end]
        fullRouteCleaned = [top for top in fullRoute if top is not None]
        
        if not fullRouteCleaned:
            self.routeGraphLabel.config(text="(No route)")
            return
        
        text = self.topsNames[fullRouteCleaned[0]]
        for i in range(1,len(fullRouteCleaned)):
            text += "  -->  " + self.topsNames[fullRouteCleaned[i]]
        
        self.routeGraphLabel.config(text=text)
    
    def deleteHikingStop(self):
        """
        Creates popup window to choose which hiking stop to delete
        """
        if len(self.hikingStops) < 1:
            messagebox.showerror("Logic error:", "Nie masz dodanych żadnych przystanków")
            return
        
        # Sizes setup
        hikingStopsAmount = len(self.hikingStops)
        marginWidth = 30
        buttonWidth = 100
        baseWidth = marginWidth + hikingStopsAmount * (marginWidth + buttonWidth)
        
        marginHeight = 30
        buttonHeight = 50
        baseHeight = 2*marginHeight + buttonHeight
        
        popup = tk.Toplevel(self.tkRoot)
        popup.title("Choose hiking stop to delete")
        popup.transient(self.tkRoot)  # keep at surface
        popup.grab_set()  # block menu interaction
        
        popup.update_idletasks()
        x = self.tkRoot.winfo_screenwidth() // 2 - baseWidth // 2
        y = self.tkRoot.winfo_screenheight() // 2 - baseHeight // 2
        popup.geometry(f"{baseWidth}x{baseHeight}+{x}+{y}")
        
        def deleteSelectedStop(index):
            self.hikingStops.pop(index)
            popup.destroy()
            self.updateMenu()
            self.updateRouteGraphLabel()
        
        # Create one button per stop
        for idx, topID in enumerate(self.hikingStops):
            name = self.topsNames[topID]
            btn = tk.Button(popup, text=name, width=12, height=2,
                            command=lambda i=idx: deleteSelectedStop(i))
            btn.place(x=marginWidth + idx * (buttonWidth + marginWidth), y=marginHeight)
        
    def listenToMapProgress(self,q):
        """
        Listens to the progress of loading the 3D map and updates the progress bar with percentage values.
        :param q: queue
        """
        while True:
            try:
                percentLoaded = q.get(timeout=1)
                if percentLoaded == "completed":
                    self.progressBar['value'] = 100
                    self.startButton.config(state="normal",text="Mapa 3D")
                    return
                
                self.progressBar['value'] = percentLoaded/10
            except:
                pass
    
    def showManual(self):
        """
        Shows popup with manual instruction.
        :return:
        """
        manualWindow = tk.Toplevel(self.tkRoot)
        manualWindow.title("Instrukcja obsługi")
        manualWindow.geometry("400x300")
        
        manualText = (
            "Witaj podróżniku!\n\n"
            "1. Aby utworzyć trasę, wpisz początek i koniec w odpowiednie pola, a następnie kliknij „Add”.\n\n"
            "2. Aby dodać przystanek pośredni, skorzystaj z pola „Dodaj przystanek” i kliknij „Add”. "
            "Możesz dodać maksymalnie 3 przystanki.\n\n"
            "3. Przystanki są dodawane w kolejności:\n"
            "   początek → przystanek 1 → przystanek 2 → przystanek 3 → koniec\n\n"
            "4. Aby usunąć przystanek, kliknij „Usuń przystanek” i wybierz odpowiedni.\n\n"
            "5. Gdy mapa 3D się załaduje, kliknij „Mapa 3D”, aby zobaczyć swoją trasę z lotu ptaka.\n\n"
            "Udanej podróży!"
        )
        
        label = tk.Label(
            manualWindow,
            text=manualText,
            justify="left",
            padx=20,
            pady=20,
            wraplength=650,
            anchor="w"
        )
        label.pack(expand=True, fill="both")
        label.config(font=("Helvetica", 12))
        
        closeButton = tk.Button(manualWindow, text="Zamknij", command=manualWindow.destroy)
        closeButton.pack(pady=10)
        
        windowWidth = 700
        windowHeight = 300
        screenWidth = self.tkRoot.winfo_screenwidth()
        screenHeight = self.tkRoot.winfo_screenheight()
        
        positionTop = int(screenHeight / 2 - windowHeight / 2)
        positionRight = int(screenWidth / 2 - windowWidth / 2)
        
        manualWindow.geometry(f'{windowWidth}x{windowHeight}+{positionRight}+{positionTop}')
        
        manualWindow.transient(self.tkRoot)
        manualWindow.grab_set()
        self.tkRoot.wait_window(manualWindow)


def gridPlace(widget, col, row, colspan=DEFAULT_COLSPAN, rowspan=DEFAULT_ROWSPAN):
    """
    Places the widget at specific coordinates with a defined size to achieve basic layout ordering.
    """
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


def drawRoute(canvas,points,tag='routeLine', orgImgSize=(2048,2048), newImgSize=(600,600)):
    """
    Draws lines between each pair of consecutive points in the 'points' array.

    :param canvas: The Tkinter Canvas instance where lines will be drawn.
    :param points: List of points (e.g., [(x1, y1), (x2, y2), ...]).
    :param tag: Tag assigned to each line (used for future deletion).
    :param orgImgSize: Original image size as a (width, height) tuple.
    :param newImgSize: Resized image size as a (width, height) tuple.
    """
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


def gradientFill(x, y, yMin, yMax, ax=None):
    """
    Rysuje wykres z linią oraz gradientowym wypełnieniem pod nią.
    Parametry linii i gradientu są ustawiane osobno.
    """
    if ax is None:
        raise ValueError("Musisz przekazać ax (AxesSubplot)")
    
    # Line settings
    line, = ax.plot(x, y, color='grey', alpha=0.4, linewidth=1)
    
    zorder = line.get_zorder()
    
    z = np.empty((100, 1, 4), dtype=float)
    rgb = mcolors.colorConverter.to_rgb('grey')
    z[:, :, :3] = rgb
    # Set gradient (starting from topAlpha to bottomAlpha)
    topAlpha = 0.8
    bottomAlpha = 0.1
    z[:, :, -1] = np.linspace(bottomAlpha, topAlpha, 100)[:, None]
    
    xmin, xmax = x.min(), x.max()
    ymin, ymax = yMin, yMax
    im = ax.imshow(z, aspect='auto', extent=[xmin, xmax, ymin, ymax],
                   origin='lower', zorder=zorder)
    
    xy = np.column_stack([x, y])
    xy = np.vstack([[xmin, ymin], xy, [xmax, ymin], [xmin, ymin]])
    clipPath = Polygon(xy, facecolor='none', edgecolor='none', closed=True)
    ax.add_patch(clipPath)
    im.set_clip_path(clipPath)
    
    ax.autoscale(True)
    return line, im

def drawElevationChart(Xvals, Yvals, pionoweLinie=None, ax=None):
    """
    Plots elevation profile with marked route points
    """
    if ax is None:
        raise ValueError("Musisz przekazać ax (AxesSubplot)")
        
    yMin, yMax = 4.1741213941640275e-05, 4.634259615214229
    gradientFill(Xvals, Yvals, yMin, yMax, ax=ax)
    
    if pionoweLinie:
        for xv, label in pionoweLinie.items():
            yTop = np.interp(xv, Xvals, Yvals)
            
            ax.vlines(x=xv, ymin=yMin, ymax=yTop, color='gray', linewidth=0.7, alpha=0.6)
            
            ax.plot(xv, yTop, marker='o', markersize=7,
                    markerfacecolor='white', markeredgecolor='gray', markeredgewidth=1)
            
            ax.text(xv, yTop + 0.1, label, color='black', fontsize=9,
                    ha='center', va='bottom')
    
    ax.grid(axis='y', alpha=0.3)
    ax.grid(axis='x', visible=False)
    
    ax.set_ylim(yMin, yMax + 1)
    
    for spine in ax.spines.values():
        spine.set_visible(False)
    ax.spines['bottom'].set_visible(True)
    ax.spines['bottom'].set_color('grey')
    ax.spines['bottom'].set_linewidth(2)
    ax.spines['bottom'].set_alpha(0.2)
    ax.tick_params(axis='both', which='both', length=0)


class PlaceholderEntry(tk.Entry):
    def __init__(self, master=None, placeholder="placeholder", color='grey', *args, **kwargs):
        super().__init__(master, *args, **kwargs)
        self.placeholder = placeholder
        self.placeholderColor = color
        self.defaultFgColor = self['fg']

        self.bind("<FocusIn>", self._onFocusIn)
        self.bind("<FocusOut>", self._onFocusOut)

        self._putPlaceholder()

    def _putPlaceholder(self):
        self.insert(0, self.placeholder)
        self.config(fg=self.placeholderColor)

    def _onFocusIn(self, _):
        if self.get() == self.placeholder:
            self.delete(0, tk.END)
            self.config(fg=self.defaultFgColor)

    def _onFocusOut(self, _):
        if not self.get():
            self._putPlaceholder()
