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

    line_node = lineSegs.create()
    app.render.attachNewNode(line_node)


def generateRoutes(app,config,distro="assets/y.csv", z_file="assets/mapa_terenu"):
    """
    Generates routes on map 3D and highlights the chosen ones.
    :param app: Application instance.
    :param config: IDs array of chosen edges
    """
    print(f"Config: {config}")
    try:
        distro = np.loadtxt(distro, delimiter=",")
        heights = np.loadtxt(z_file, delimiter=",")
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
                    x_str, y_str = line[1:-1].split(',')
                    x = int(x_str.strip())
                    y = int(y_str.strip())
                    route.append((distro[y], distro[x], heights[x,y]*increaseHeight + floatingFactor))
        
        if i in config:
            color = (0, 1, 1, 1)
        else:
            color = (0, 0, 0, 1)
        
        for j in range(len(route)-1):
            drawPathLine(app,[route[j],route[j+1]],color=color)