from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
from assets.peaks import peaks
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
        self.edgeWeights = routeTime
        self.topsAmnt = 0
        self.colPixelUnit = 1920 / 40
        self.rowPixelUnit = 1080 / 20
        self.chartCanvas = None
        self.graph = Graph()
        self.travelTimeLabel = None
        self.routeGraphLabel = None
        
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
                        x_str, y_str = line[1:-1].split(',')
                        x = int(x_str.strip())
                        y = int(y_str.strip())
                        route.append((x, y))
                self.routes.append(route)
    
    # Start-End ADD handling functions
    def addTop(self, entryIdx,topType):
        entry = self.routeHandling[entryIdx]
        name = entry.get().strip()
        
        entry.config(bg="white")
        
        if name not in self.topsNames:
            entry.config(bg="lightcoral")
            return
        
        topID = self.topsNames.index(name)
        try:
            fullRoute = self.isValidNewTop(topID,topType)
            if topType == 0:
                self.start = topID
            elif topType == 1:
                self.end = topID
            elif topType == 2:
                self.hikingStops.append(topID)
            
            if len(fullRoute) > 1 : self.updateMenu()
            self.updateRouteGraphLabel()
            entry.config(bg="lightgreen")
        
        except ValueError as e:
            entry.config(bg="lightcoral")
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
            return fullRouteCleaned
        
        for i in range(len(fullRouteCleaned)-1):
            if fullRouteCleaned[i] == fullRouteCleaned[i+1]:
                raise ValueError("Sąsiednie punkty na trasie nie mogą być takie same.")
        return fullRouteCleaned
    
    def eraseRoutesFromCanvas(self):
        for line_id in self.routesCanvaIDs:
            self.mapCanvas.delete(line_id)
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
            return ([],[],[])
        
        allPaths = [
            self.graph.findShortestPath(a, b)
            for a, b in zip(routePoints, routePoints[1:])
        ]
        
        for path in allPaths:
            for edgeIdx in path:
                ids = drawRoute(self.mapCanvas,self.routes[edgeIdx])
                self.routesCanvaIDs += ids
                
        return routePoints
    
    def updateChart(self,x, y, znaczniki):
        dpi = 100
        width = self.colPixelUnit * 17 / dpi
        height = self.rowPixelUnit * 3 / dpi
        fig = Figure(figsize=(width, height), dpi=dpi)
        plot = fig.add_subplot(111)
        
        drawElevationChart(x, y, pionowe_linie=znaczniki, ax=plot)
        
        # Del prev route from canvas
        if self.chartCanvas is not None:
            self.chartCanvas.get_tk_widget().destroy()
            
        self.chartCanvas = FigureCanvasTkAgg(fig, master=self.tkRoot)
        widget = self.chartCanvas.get_tk_widget()
        
        gridPlace(widget, 20, 8, colspan=18, rowspan=6)
        
        self.chartCanvas.draw()
    
    def updateMenu(self):
        topsIds = self.updateMapPahtVis()

        yVals,checkpoints = self.graph.getElevationProfile(topsIds)
        xVals = np.arange(len(yVals))
        
        marks = {checkpt: self.topsNames[topsIds[i]] for i, checkpt in enumerate(checkpoints)}
        
        self.updateChart(xVals,yVals, marks)
        self.updateTime()
    
    def updateTime(self):
        fullRoute = [self.start] + self.hikingStops + [self.end]
        fullRouteCleaned = [top for top in fullRoute if top is not None]
        
        time_text = "0 h" if len(fullRouteCleaned) < 2 else f"{self.graph.getTravelTime(fullRouteCleaned)} h"
        self.travelTimeLabel.config(text=time_text)
    
    def generateRandomTopName(self):
        nameID = randint(0,len(peaks)-1)
        return peaks[nameID][0]
    
    def updateRouteGraphLabel(self):
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
        
        def delete_selected_stop(index):
            self.hikingStops.pop(index)
            popup.destroy()
            self.updateMenu()
            self.updateRouteGraphLabel()
        
        # Create one button per stop
        for idx, topID in enumerate(self.hikingStops):
            name = self.topsNames[topID]
            btn = tk.Button(popup, text=name, width=12, height=2,
                            command=lambda i=idx: delete_selected_stop(i))
            btn.place(x=marginWidth + idx * (buttonWidth + marginWidth), y=marginHeight)
        


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


def gradientFill(x, y, y_min, y_max, ax=None):
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
    ymin, ymax = y_min, y_max
    im = ax.imshow(z, aspect='auto', extent=[xmin, xmax, ymin, ymax],
                   origin='lower', zorder=zorder)
    
    xy = np.column_stack([x, y])
    xy = np.vstack([[xmin, ymin], xy, [xmax, ymin], [xmin, ymin]])
    clip_path = Polygon(xy, facecolor='none', edgecolor='none', closed=True)
    ax.add_patch(clip_path)
    im.set_clip_path(clip_path)
    
    ax.autoscale(True)
    return line, im

def drawElevationChart(x_vals, y_vals, pionowe_linie=None, ax=None):
    """
    Plots elevation profile with marked route points
    """
    if ax is None:
        raise ValueError("Musisz przekazać ax (AxesSubplot)")
        
    y_min, y_max = 4.1741213941640275e-05, 4.634259615214229
    gradientFill(x_vals, y_vals, y_min, y_max, ax=ax)
    
    if pionowe_linie:
        for xv, label in pionowe_linie.items():
            y_bottom = y_min
            y_top = np.interp(xv, x_vals, y_vals)
            
            ax.vlines(x=xv, ymin=y_bottom, ymax=y_top, color='gray', linewidth=0.7, alpha=0.6)
            
            ax.plot(xv, y_top, marker='o', markersize=7,
                    markerfacecolor='white', markeredgecolor='gray', markeredgewidth=1)
            
            ax.text(xv, y_top + 0.1, label, color='black', fontsize=9,
                    ha='center', va='bottom')
    
    ax.grid(axis='y', alpha=0.3)
    ax.grid(axis='x', visible=False)
    
    # ax.set_ylabel("Wysokość")
    ax.set_ylim(y_min, y_max + 1)
    
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
        self.placeholder_color = color
        self.default_fg_color = self['fg']  # Domyślny kolor tekstu

        self.bind("<FocusIn>", self._on_focus_in)
        self.bind("<FocusOut>", self._on_focus_out)

        self._put_placeholder()

    def _put_placeholder(self):
        self.insert(0, self.placeholder)
        self.config(fg=self.placeholder_color)

    def _on_focus_in(self, event):
        if self.get() == self.placeholder:
            self.delete(0, tk.END)
            self.config(fg=self.default_fg_color)

    def _on_focus_out(self, event):
        if not self.get():
            self._put_placeholder()