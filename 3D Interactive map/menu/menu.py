import threading
from tkinter import ttk
from menu.utils import *
from menu.utils import Menu
from PIL import Image, ImageTk


def runMenu(configQ):
    
    def sendConfig():
        config = menu.activeEdgedIds
        configQ.put(config)
        root.destroy()
    
    # Tinkter initialization
    root = tk.Tk()
    root.attributes("-fullscreen", True)
    menu = Menu(root)
    colPixelUnit = 1920/40
    rowPixelUnit = 1080/20
    
    mapLoaderListener = threading.Thread(target=menu.listenToMapProgress, args=(configQ,),daemon=True)
    mapLoaderListener.start()
    
    # Canvas map
    canvaSize = 600
    imgPath = 'assets/mapaMenu.png'
    X = colPixelUnit
    Y = rowPixelUnit*2
    
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
    gridPlace(labelRoute, 27, 1,colspan=3)
    
    # Delete hiking stop button
    deleteHikingStopButton = tk.Button(root, text="Delete Hiking Stop", command=menu.deleteHikingStop)
    gridPlace(deleteHikingStopButton, 33, 1,colspan=3,rowspan=1)
    
    # Route graph boxes
    menu.routeGraphLabel = tk.Label(root, text="")
    gridPlace(menu.routeGraphLabel, 20, 2,colspan=17)
    
    # Autocomplete Entry
    labelStart = tk.Label(root, text="Początek")
    gridPlace(labelStart, 20, 4)
    
    labelEnd = tk.Label(root, text="Koniec")
    gridPlace(labelEnd, 26, 4)
    
    labelStop = tk.Label(root, text="Dodaj przystanek")
    gridPlace(labelStop, 32, 4)
    
    for idx,i in enumerate([20,26,32]):
        entry = PlaceholderEntry(root,placeholder="np: " + menu.generateRandomTopName())
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
    
    # Route time length
    timeLabel = tk.Label(root, text="Przewidywany czas podróży")
    gridPlace(timeLabel, 20, 15, colspan=8)
    
    frame = tk.Frame(root, bg="lightgreen")
    gridPlace(frame, 28, 15, colspan=2)
    
    menu.travelTimeLabel = tk.Label(frame, text="0",background="lightgreen")
    menu.travelTimeLabel.pack(pady=10)
    
    # Progressbar
    menu.progressBar = ttk.Progressbar(root, orient="horizontal", mode="determinate")
    gridPlace(menu.progressBar, 22, 17, colspan=8)
    
    labelRoute = tk.Label(root, text="Ładowanie mapy 3D")
    gridPlace(labelRoute, 30, 17,colspan=3)
    
    # Button
    menu.startButton = tk.Button(root, text="Mapa 3D\n(trwa ładowanie)", command=sendConfig,state="disabled")
    gridPlace(menu.startButton, 34, 17)
    
    root.mainloop()
