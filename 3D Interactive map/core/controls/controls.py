from math import pi, sin, cos
from direct.showbase.ShowBaseGlobal import globalClock
from panda3d.core import WindowProperties

from core.controls import camera,directions,keyMap
# from core.controls.camera import captureMouse
from core.controls.directions import Direction
from core.controls.keyMap import Keys


def degToRad(degrees):
    return degrees * (pi / 180.0)
class Controls:
    def __init__(self, app):
        self.cameraSwingActivated = True
        self.lastMouseX = 0
        self.lastMouseY = 0
        self.app = app
        self.keyMap = keyMap
        self.activeKeys = {
            "forward": False,
            "backward": False,
            "left": False,
            "right": False,
            "up": False,
            "down": False,
        }
        

    def setupControls(self,app):
        print("ustawiam klawisze")
        app.keyMap = {
            "forward": False,
            "backward": False,
            "left": False,
            "right": False,
            "up": False,
            "down": False,
        }
        self.captureMouse()
        app.accept('escape', self.releaseMouse)
        # app.accept('mouse1', app.handleLeftClick)
        # app.accept('mouse3', app.placeBlock)
        
        app.accept(Keys.W.value, self.updateKeyMap, ['forward', True])
        app.accept(Keys.W_UP.value, self.updateKeyMap, ['forward', False])
        app.accept(Keys.A.value, self.updateKeyMap, ['left', True])
        app.accept(Keys.A_UP.value, self.updateKeyMap, ['left', False])
        app.accept(Keys.S.value, self.updateKeyMap, ['backward', True])
        app.accept(Keys.S_UP.value, self.updateKeyMap, ['backward', False])
        app.accept(Keys.D.value, self.updateKeyMap, ['right', True])
        app.accept(Keys.D_UP.value, self.updateKeyMap, ['right', False])
        app.accept(Keys.SPACE.value, self.updateKeyMap, ['up', True])
        app.accept(Keys.SPACE_UP.value, self.updateKeyMap, ['up', False])
        app.accept(Keys.LSHIFT.value, self.updateKeyMap, ['down', True])
        app.accept(Keys.LSHIFT_UP.value, self.updateKeyMap, ['down', False])
        
    def captureMouse(self):
        self.cameraSwingActivated = True

        md = self.app.win.getPointer(0)
        self.lastMouseX = md.getX()
        self.lastMouseY = md.getY()
        
        properties = WindowProperties()
        # properties.setCursorHidden(True)
        properties.setMouseMode(WindowProperties.M_confined)
        self.app.win.requestProperties(properties)
        
    
    def releaseMouse(self):
        self.cameraSwingActivated = False

        properties = WindowProperties()
        properties.setCursorHidden(False)
        properties.setMouseMode(WindowProperties.M_absolute)
        self.app.win.requestProperties(properties)
    
    def updateKeyMap(self, key, value):
        self.activeKeys[key] = value
    
    def update(self, task):
        dt = globalClock.getDt()
        
        playerMoveSpeed = 10
        
        x_movement = 0
        y_movement = 0
        z_movement = 0
        
        if self.activeKeys['forward']:
            x_movement -= dt * playerMoveSpeed * sin(degToRad(self.app.camera.getH()))
            y_movement += dt * playerMoveSpeed * cos(degToRad(self.app.camera.getH()))
        if self.activeKeys['backward']:
            x_movement += dt * playerMoveSpeed * sin(degToRad(self.app.camera.getH()))
            y_movement -= dt * playerMoveSpeed * cos(degToRad(self.app.camera.getH()))
        if self.activeKeys['left']:
            x_movement -= dt * playerMoveSpeed * cos(degToRad(self.app.camera.getH()))
            y_movement -= dt * playerMoveSpeed * sin(degToRad(self.app.camera.getH()))
        if self.activeKeys['right']:
            x_movement += dt * playerMoveSpeed * cos(degToRad(self.app.camera.getH()))
            y_movement += dt * playerMoveSpeed * sin(degToRad(self.app.camera.getH()))
        if self.activeKeys['up']:
            z_movement += dt * playerMoveSpeed
        if self.activeKeys['down']:
            z_movement -= dt * playerMoveSpeed

        self.app.camera.setPos(
            self.app.camera.getX() + x_movement,
            self.app.camera.getY() + y_movement,
            self.app.camera.getZ() + z_movement,
        )
        
        if self.cameraSwingActivated:
            md = self.app.win.getPointer(0)
            mouseX = md.getX()
            mouseY = md.getY()
            
            mouseChangeX = mouseX - self.lastMouseX
            mouseChangeY = mouseY - self.lastMouseY
            
            self.cameraSwingFactor = 30
            
            currentH = self.app.camera.getH()
            currentP = self.app.camera.getP()
            if mouseChangeX != 0 and mouseChangeY != 0:
                self.app.camera.setHpr(
                    (currentH - mouseChangeX * dt * self.cameraSwingFactor,
                    min(90, max(-90, currentP - mouseChangeY * dt * self.cameraSwingFactor)),
                    0
                ))
                self.lastMouseX = mouseX
                self.lastMouseY = mouseY
            
            # self.app.win.movePointer(0, self.app.win.getXSize() // 2, self.app.win.getYSize() // 2)
                x = self.app.win.getXSize() // 2  # Środek okna w poziomie
                y = self.app.win.getYSize() // 2  # Środek okna w pionie
                
                # self.app.win.movePointer(0, x, y)  # Przenosi kursor na (x, y)
                if self.app.win.movePointer(0, x, y):
                    self.lastMouseX = x
                    self.lastMouseY = y
        
        return task.cont
