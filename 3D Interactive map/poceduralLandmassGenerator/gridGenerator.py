def generateGrid(app):
    for x in range(10):
        for y in range(10):
            createPoint(app, x-5, y-5)

def createPoint(app, x, y):
    pointModel = app.loader.loadModel("smiley")
    pointModel.reparentTo(app.render)
    pointModel.setPos(x, y, 0)
    pointModel.setScale(0.1)
    pointModel.setColor(1, 0, 0, 1)
    # newPointNode = app.render.attach/NewNode('PointNode')
    