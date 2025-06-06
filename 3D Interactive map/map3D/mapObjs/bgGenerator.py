def generateBg(app):
    # Ground - ! Not visible tops names !
    # cm = CardMaker("ground")
    # cm.setFrame(-300, 300, -300, 300)
    #
    # app.ground = app.render.attachNewNode(cm.generate())
    # app.ground.setHpr(0, -90, 0)
    # app.ground.setPos(0, 0, 0)
    # app.ground.setTexScale(TextureStage.getDefault(), 1, 1)
    #
    # groundTexture = app.loader.loadTexture("assets/forestTopView.jpg")
    # app.ground.setTexture(groundTexture)
    
    # Skies
    app.sky = app.loader.loadModel("assets/skybox/skybox.egg")
    app.sky.reparentTo(app.render)
    app.sky.setScale(1000)
    app.sky.setBin('background', 0)
    app.sky.setDepthWrite(0)
    app.sky.setLightOff()
    