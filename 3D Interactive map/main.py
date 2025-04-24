from math import pi, sin, cos
from direct.showbase.ShowBase import ShowBase
from direct.showbase.ShowBaseGlobal import globalClock
from direct.task.TaskManagerGlobal import taskMgr
from panda3d.core import WindowProperties

from core.controls import controls, camera
# from core.controls.camera import setupCamera, captureMouse
from core.controls.controls import Controls
from core.controls.keyboardControl import setupControls
from poceduralLandmassGenerator import gridGenerator

class MyGame(ShowBase):
    def __init__(self):
        ShowBase.__init__(self)
        self.game_controls = Controls(self)
        self.game_controls.setupControls(self)
        self.setupCamera()
        # captureMouse(self)
        # setupControls(self)
        gridGenerator.generateGrid(self)
        
        taskMgr.add(self.game_controls.update, 'update')
    
    def setupCamera(self):
        properties = WindowProperties()
        properties.setCursorHidden(True)
        properties.setMouseMode(WindowProperties.M_relative)
        properties.setSize(960, 540)
        self.win.requestProperties(properties)

        self.disableMouse()
        self.camera.setPos(0, 0, 3)
        self.camLens.setFov(80)

        
game = MyGame()
game.run()