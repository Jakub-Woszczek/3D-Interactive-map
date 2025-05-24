import tkinter as tk
from tkinter import ttk
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from menu.utils import *
from menu.utils import Menu
from PIL import Image, ImageTk


def runMenu(configQ):
    
    def sendConfig():
        config = {
            "scale": 1,
            "pos": 1
        }
        configQ.put(config)
        root.destroy()
    
    # Tinkter initialization
    root = tk.Tk()
    root.attributes("-fullscreen", True)
    menu = Menu(root)

    
    # Canvas map
    canvaSize = 600
    imgPath = 'assets/test_napis5.png'
    X = 1920/40
    Y = 1080/20*2
    
    canvas = tk.Canvas(root, width=canvaSize, height=canvaSize, bg='white')
    canvas.place(x=X, y=Y)
    menu.mapCanvas = canvas
    
    orgImg = Image.open(imgPath)
    x, y = orgImg.size
    
    scale = min(canvaSize / x, canvaSize / y, 1)
    newSize = (int(x * scale), int(y * scale))
    resizedImg = orgImg.resize(newSize, Image.LANCZOS)
    
    root.tk_image = ImageTk.PhotoImage(resizedImg)
    
    canvas.create_image(0,0, anchor='nw', image=root.tk_image)
    
    # Text "Mapa"
    labelMap = tk.Label(root, text="Mapa")
    gridPlace(labelMap, 7, 1)
    
    # Text "Trasa"
    labelRoute = tk.Label(root, text="Trasa")
    gridPlace(labelRoute, 26, 1)
    
    # Route graph boxes
    boxFrames = []
    for i in range(0, 9, 2):
        frame = tk.Frame(root, bg="lightblue")
        gridPlace(frame, 20 + i * 2, 2, colspan=2)
        boxFrames.append(frame)
    
    # Autocomplete Entry
    labelStart = tk.Label(root, text="Początek")
    gridPlace(labelStart, 20, 4)
    
    labelEnd = tk.Label(root, text="Koniec")
    gridPlace(labelEnd, 26, 4)
    
    labelStop = tk.Label(root, text="Dodaj przystanek")
    gridPlace(labelStop, 32, 4)
    
    for idx,i in enumerate([20,26,32]):
        entry = tk.Entry(root)
        gridPlace(entry, i, 5, colspan=3)
        menu.routeHandling.append(entry)
        
        listbox = tk.Listbox(root, height=6, width=15)
        listbox.place_forget()
        
        menu.makeListboxBind(entry, listbox)
        
        startBtt = tk.Button(root, text="Add", command=lambda i=idx: menu.addTop(i,i))
        gridPlace(startBtt, i + 3, 5, colspan=2)
    
    # Chart
    labelChart = tk.Label(root, text="Profil wysokościowy")
    gridPlace(labelChart, 20, 7, colspan=8)
    
    fig = Figure(figsize=(5, 4), dpi=100)
    plot = fig.add_subplot(111)
    plot.plot([1, 2, 3], [1, 4, 9])
    
    canvas = FigureCanvasTkAgg(fig, master=root)
    canvas.get_tk_widget().place_forget()
    gridPlace(canvas.get_tk_widget(), 20, 8, colspan=18, rowspan=6)
    
    # Route time length
    timeLabel = tk.Label(root, text="Przewidywany czas podróży")
    gridPlace(timeLabel, 20, 15, colspan=8)
    
    frame = tk.Frame(root, bg="lightgreen")
    gridPlace(frame, 28, 15, colspan=2)
    boxFrames.append(frame)
    
    # Progressbar
    progress = ttk.Progressbar(root, orient="horizontal", mode="determinate")
    gridPlace(progress, 22, 17, colspan=8)
    
    # Button
    startBtt = tk.Button(root, text="Start", command=sendConfig)
    gridPlace(startBtt, 34, 17)
    
    root.mainloop()
