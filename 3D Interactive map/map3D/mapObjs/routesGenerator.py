import numpy as np
from panda3d.core import LineSegs

def drawPathLine(app, points, color=(1, 0, 0, 1), thickness=3.0):
    """
    Draws a line segmented on the map
    :param app: Application instance
    :param points: Two points (x,y,z) between which the line segment is drawn
    """
    
    if not points or len(points) < 2:
        return

    lineSegs = LineSegs()
    lineSegs.setThickness(thickness)
    lineSegs.setColor(*color)

    lineSegs.moveTo(*points[0])
    for pt in points[1:]:
        lineSegs.drawTo(*pt)

    lineNode = lineSegs.create()
    app.render.attachNewNode(lineNode)


def generateRoutes(app,config,distro="assets/gridSpacing.csv", zFile="assets/mapaTerenu"):
    """
    Generates routes on map 3D and highlights the chosen ones.
    :param app: Application instance.
    :param config: IDs array of chosen edges
    """
    try:
        distro = np.loadtxt(distro, delimiter=",")
        heights = np.loadtxt(zFile, delimiter=",")
    except Exception as e:
        print(f"Błąd przy wczytywaniu plików CSV: {e}")
        return
    
    increaseHeight = 4
    floatingFactor = 0.05
    for i in range(33):
        with open(f"assets/Trasy/t{i}.txt", 'r') as f:
            route = []
            for line in f:
                line = line.strip()
                if line.startswith('(') and line.endswith(')'):
                    xStr, yStr = line[1:-1].split(',')
                    x = int(xStr.strip())
                    y = int(yStr.strip())
                    route.append((distro[y], distro[x], heights[x,y]*increaseHeight + floatingFactor))
        
        if i in config:
            color = (0, 1, 1, 1)
        else:
            color = (0, 0, 0, 1)
        
        for j in range(len(route)-1):
            drawPathLine(app,[route[j],route[j+1]],color=color)