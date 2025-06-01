import numpy as np
from panda3d.core import GeomVertexFormat, GeomVertexData, GeomVertexWriter
from panda3d.core import GeomTriangles, Geom, GeomNode


def generateMeshFromCSV(app, x_file="assets/x.csv", y_file="assets/y.csv", z_file="assets/mapa_terenu"):
    try:
        distro = np.loadtxt(y_file, delimiter=",")
        heights = np.loadtxt(z_file, delimiter=",")
    except Exception as e:
        print(f"Błąd przy wczytywaniu plików CSV: {e}")
        return

    rows, cols = heights.shape

    Zmin = heights.min()
    Zmax = heights.max()

    
    format = GeomVertexFormat.getV3cp()
    vdata = GeomVertexData("combined_terrain", format, Geom.UHStatic)
    vertex = GeomVertexWriter(vdata, "vertex")
    color = GeomVertexWriter(vdata, "color")

    triangles = GeomTriangles(Geom.UHStatic)
    vertexIdx = 0

    for row in range(0, rows - 1):
        for col in range(0, cols - 1):
            z0 = heights[row, col]
            z1 = heights[row, col + 1]
            z2 = heights[row + 1, col]
            z3 = heights[row + 1, col + 1]

            p0 = (distro[col], distro[row], z0)
            p1 = (distro[col + 1], distro[row], z1)
            p2 = (distro[col], distro[row + 1], z2)
            p3 = (distro[col + 1], distro[row + 1], z3)
            
            avgZ1 = (z0 + z1 + z2) / 3
            flatColor1 = heightToColor(avgZ1, Zmin, Zmax)
            for pos in [p0, p1, p2]:
                vertex.addData3f(*pos)
                color.addData4f(*flatColor1)
            triangles.addVertices(vertexIdx, vertexIdx + 1, vertexIdx + 2)
            vertexIdx += 3

            avg_z2 = (z2 + z1 + z3) / 3
            flat_color2 = heightToColor(avg_z2, Zmin, Zmax)
            for pos in [p2, p1, p3]:
                vertex.addData3f(*pos)
                color.addData4f(*flat_color2)
            triangles.addVertices(vertexIdx, vertexIdx + 1, vertexIdx + 2)
            vertexIdx += 3
        app.queue.put(int(row/rows*1000))

    geom = Geom(vdata)
    geom.addPrimitive(triangles)

    node = GeomNode("terrain")
    node.addGeom(geom)

    nodePath = app.render.attachNewNode(node)
    nodePath.setTwoSided(True)
    nodePath.setTransparency(True)

def heightToColor(z, Zmin, Zmax):
    normZ = (z - Zmin) / (Zmax - Zmin) if Zmax > Zmin else 0
    """
    zielony: (0, 1, 0)
    żółty: (1, 1, 0)
    pomarańczowy: (1, 0.5, 0)
    czerwony: (1, 0, 0)
    """

    if normZ < 0.33:
        t = normZ / 0.33
        r = t
        g = 1
    elif normZ < 0.66:
        t = (normZ - 0.33) / 0.33
        r = 1
        g = 1 - 0.5 * t
    else:
        t = (normZ - 0.66) / 0.34
        r = 1
        g = 0.5 * (1 - t)

    return (r, g, 0, 1)