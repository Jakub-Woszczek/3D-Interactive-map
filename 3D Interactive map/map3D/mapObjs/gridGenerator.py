import math

import numpy as np
from panda3d.core import GeomVertexFormat, GeomVertexData, GeomVertexWriter, LineSegs, TextNode, Vec3
from panda3d.core import GeomTriangles, Geom, GeomNode
from assets.peaks import peaksData


def generateMeshFromCSV(app,meshType, distroFile="assets/gridSpacing.csv", zFile="assets/mapaTerenu"):
    try:
        distro = np.loadtxt(distroFile, delimiter=",")
        heights = np.loadtxt(zFile, delimiter=",")
    except Exception as e:
        print(f"Błąd przy wczytywaniu plików CSV: {e}")
        return

    rows, cols = heights.shape

    increaseHeight = 4
    Zmin = heights.min()*increaseHeight
    Zmax = heights.max()*increaseHeight

    
    format = GeomVertexFormat.getV3cp()
    vdata = GeomVertexData("combined_terrain", format, Geom.UHStatic)
    vertex = GeomVertexWriter(vdata, "vertex")
    color = GeomVertexWriter(vdata, "color")

    triangles = GeomTriangles(Geom.UHStatic)
    vertexIdx = 0

    step = 1
    for row in range(0, rows - step, step):
        for col in range(0, cols - step, step):
            z0 = heights[row, col] * increaseHeight
            z1 = heights[row, col + step] * increaseHeight
            z2 = heights[row + step, col] * increaseHeight
            z3 = heights[row + step, col + step] * increaseHeight

            p0 = (distro[col], distro[row], z0)
            p1 = (distro[col + step], distro[row], z1)
            p2 = (distro[col], distro[row + step], z2)
            p3 = (distro[col + step], distro[row + step], z3)
            
            avgZ1 = (z0 + z1 + z2) / 3
            if meshType == "height":
                flatColor1 = heightToColor(avgZ1, Zmin, Zmax)
            else:
                flatColor1 = slopeToColor(p1,p2,p0)
            
            for pos in [p0, p1, p2]:
                vertex.addData3f(*pos)
                color.addData4f(*flatColor1)
            triangles.addVertices(vertexIdx, vertexIdx + 1, vertexIdx + 2)
            vertexIdx += 3

            avgZ2 = (z2 + z1 + z3) / 3
            if meshType == "height":
                flatColor2 = heightToColor(avgZ2, Zmin, Zmax)
            else:
                flatColor2 = slopeToColor(p2, p1, p3)
            
            for pos in [p2, p1, p3]:
                vertex.addData3f(*pos)
                color.addData4f(*flatColor2)
            triangles.addVertices(vertexIdx, vertexIdx + 1, vertexIdx + 2)
            vertexIdx += 3
        
        app.queue.put(int(row / rows * 1000))

    geom = Geom(vdata)
    geom.addPrimitive(triangles)

    node = GeomNode("terrain")
    node.addGeom(geom)

    nodePath = app.render.attachNewNode(node)
    app.terrainMeshNode.append(nodePath)
    nodePath.setTwoSided(True)
    nodePath.setTransparency(True)
    
    # Generate tops Names
    bilboardDiff = 1*increaseHeight
    for topName, (row, col) in peaksData:
        x = distro[col]
        y = distro[row]
        z = heights[row, col]*increaseHeight
        
        # Sphere
        sphere = app.loader.loadModel("models/misc/sphere")
        sphere.setScale(0.3)
        sphere.setPos(x, y, z)
        sphere.setColor(1, 1, 1, 1)
        sphere.reparentTo(app.render)
        
        # Vertical line
        lineSegs = LineSegs()
        lineSegs.setThickness(4.0)
        lineSegs.setColor(1, 1, 1, 1)
        lineSegs.moveTo(x, y, z)
        lineSegs.drawTo(x, y, z + bilboardDiff)
        app.render.attachNewNode(lineSegs.create())
        
        # Billboard
        text = TextNode(topName)
        text.setText(topName)
        text.setTextColor(1, 1, 1, 1)
        text.setShadow(0.05, 0.05)
        text.setShadowColor(0, 0, 0, 1)
        text.setCardColor(0, 0, 0, 0.2)
        text.setAlign(TextNode.ACenter)
        
        textNodePath = app.render.attachNewNode(text)
        textNodePath.setScale(2)
        textNodePath.setPos(x, y, z + bilboardDiff)
        textNodePath.setBillboardPointEye()

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

def slopeToColor(p1,p2,p3):
    """
    Computes a color based on the slope of a triangle defined by three 3D points.

    The slope is calculated as the angle between the triangle’s normal vector and the vertical axis (Z).

    Color mapping (with smooth transitions between them):
        - 0°: Green
        - 20°: Yellow
        - 40°: Orange
        - 60°: Red
        - 90°: Black
    
    :p1: 3D point
    :p2: 3D point
    :p3: 3D point
    :return: A tuple representing the RGBA color corresponding to the slope.
    """
    
    v1 = Vec3(p2[0] - p1[0], p2[1] - p1[1], p2[2] - p1[2])
    v2 = Vec3(p3[0] - p1[0], p3[1] - p1[1], p3[2] - p1[2])
    
    normal = v1.cross(v2)
    normal.normalize()
    
    vertical = Vec3(0, 0, 1)
    dot = normal.dot(vertical)
    angleRad = math.acos(max(min(dot, 1.0), -1.0))  # Clamp dot product
    angleDeg = math.degrees(angleRad)
    
    def lerp(c1, c2, t):
        return tuple(c1[i] + (c2[i] - c1[i]) * t for i in range(4))
    
    breakpoints = [
        (0, (0, 1, 0, 1)),
        (20, (1, 1, 0, 1)),
        (40, (1, 0.5, 0, 1)),
        (60, (1, 0, 0, 1)),
        (90, (0, 0, 0, 1)),
    ]
    
    for i in range(len(breakpoints) - 1):
        a0, c0 = breakpoints[i]
        a1, c1 = breakpoints[i + 1]
        if a0 <= angleDeg < a1:
            t = (angleDeg - a0) / (a1 - a0)
            return lerp(c0, c1, t)
    
    return breakpoints[-1][1]