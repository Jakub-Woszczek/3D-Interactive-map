import csv
from panda3d.core import GeomVertexFormat, GeomVertexData, GeomVertexWriter, GeomLines
from panda3d.core import GeomTriangles, Geom, GeomNode
from panda3d.core import LColor

def generateMeshFromCSV(app, filename="mapa.csv", gestosc=10, scale=4, step=2):
    try:
        with open(filename, "r") as file:
            reader = csv.reader(file)
            heights = [[float(value) for value in row] for row in reader]
    except Exception as e:
        print(f"Błąd przy wczytywaniu pliku CSV: {e}")
        return

    rows = len(heights)
    cols = len(heights[0]) if rows > 0 else 0

    flat = [val for row in heights for val in row]
    z_min = min(flat)
    z_max = max(flat)

    format = GeomVertexFormat.getV3cp()
    vdata = GeomVertexData("combined_terrain", format, Geom.UHStatic)
    vertex = GeomVertexWriter(vdata, "vertex")
    color = GeomVertexWriter(vdata, "color")

    triangles = GeomTriangles(Geom.UHStatic)
    vertex_index = 0

    for y in range(0, rows - step, step):
        for x in range(0, cols - step, step):
            # Wysokości i pozycje
            z0 = heights[y][x]
            z1 = heights[y][x + step]
            z2 = heights[y + step][x]
            z3 = heights[y + step][x + step]

            p0 = ((x - cols // 2) / gestosc, (y - rows // 2) / gestosc, z0 * scale)
            p1 = ((x + step - cols // 2) / gestosc, (y - rows // 2) / gestosc, z1 * scale)
            p2 = ((x - cols // 2) / gestosc, (y + step - rows // 2) / gestosc, z2 * scale)
            p3 = ((x + step - cols // 2) / gestosc, (y + step - rows // 2) / gestosc, z3 * scale)

            # Kolory
            c0 = heightToColor(z0, z_min, z_max)
            c1 = heightToColor(z1, z_min, z_max)
            c2 = heightToColor(z2, z_min, z_max)
            c3 = heightToColor(z3, z_min, z_max)

            # Trójkąt 1: p0, p1, p2
            avg_z1 = (z0 + z1 + z2) / 3
            flat_color1 = heightToColor(avg_z1, z_min, z_max)
            for pos in [p0, p1, p2]:
                vertex.addData3f(*pos)
                color.addData4f(*flat_color1)
            
            triangles.addVertices(vertex_index, vertex_index + 1, vertex_index + 2)
            vertex_index += 3

            # Trójkąt 2: p2, p1, p3
            avg_z2 = (z2 + z1 + z3) / 3
            flat_color2 = heightToColor(avg_z2, z_min, z_max)
            for pos in [p2, p1, p3]:
                vertex.addData3f(*pos)
                color.addData4f(*flat_color2)
            
            triangles.addVertices(vertex_index, vertex_index + 1, vertex_index + 2)
            vertex_index += 3

    geom = Geom(vdata)
    geom.addPrimitive(triangles)

    node = GeomNode("terrain")
    node.addGeom(geom)

    nodePath = app.render.attachNewNode(node)
    # Druciany overlay (czarne krawędzie)
    # wireframe = nodePath.copyTo(app.render)
    # wireframe.setRenderModeWireframe()
    # wireframe.setColor(0, 0, 0, 1)
    # wireframe.setTransparency(True)
    # wireframe.setDepthOffset(1)  # delikatnie przesunięty do przodu, by był widoczny
    #
    nodePath.setTwoSided(True)  # widać od spodu też
    nodePath.setTransparency(True)
    
    add_route(app, rows, cols, gestosc, scale, heights)


def heightToColor(z, z_min, z_max):
    norm_z = (z - z_min) / (z_max - z_min) if z_max > z_min else 0
    r = norm_z
    g = 1 - norm_z
    return (r, g, 0, 1)


def add_route(app, rows, cols, gestosc, scale, heights):
    route_points = []
    step = 2

    for i in range(0, min(rows, cols), step):
        x = i
        y = i

        z = heights[y][x] + 0.01
        route_points.append((x, y, z))

    route_format = GeomVertexFormat.getV3cp()
    route_vdata = GeomVertexData("route", route_format, Geom.UHStatic)
    route_vertex = GeomVertexWriter(route_vdata, "vertex")
    route_color = GeomVertexWriter(route_vdata, "color")

    route_color_value = (1, 1, 0, 1)

    for (x, y, z) in route_points:
        route_vertex.addData3f((x - cols // 2) / gestosc, (y - rows // 2) / gestosc, z * scale)
        route_color.addData4f(*route_color_value)

    route_lines = GeomLines(Geom.UHStatic)
    for i in range(len(route_points) - 1):
        route_lines.addVertices(i, i + 1)

    route_lines.closePrimitive()

    route_geom = Geom(route_vdata)
    route_geom.addPrimitive(route_lines)

    route_node = GeomNode("route")
    route_node.addGeom(route_geom)

    route_np = app.render.attachNewNode(route_node)
    route_np.setRenderModeThickness(3)
