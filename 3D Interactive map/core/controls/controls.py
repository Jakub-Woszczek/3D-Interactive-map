from math import pi, sin, cos
from direct.gui.OnscreenText import OnscreenText
from direct.showbase.ShowBaseGlobal import globalClock
from panda3d.core import WindowProperties, TextNode

from core.controls import directions,keyMap
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
        self.posText = OnscreenText(
            text="",
            pos=(-1.3, 0.9),
            scale=0.05,
            fg=(1, 1, 1, 1),
            align=TextNode.ALeft,
            mayChange=True
        )
        

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
    
    # Initial camera setup
    def setupCamera(self,app):
        # Use here captureMouse(self)
        properties = WindowProperties()
        properties.setCursorHidden(True)
        properties.setMouseMode(WindowProperties.M_confined)
        properties.setSize(960, 540)
        app.win.requestProperties(properties)

        app.disableMouse()
        app.camera.setPosHpr(130, 0, 50,90, -25, 0)
        app.camLens.setFov(80)
    
    
    def captureMouse(self):
        self.cameraSwingActivated = True
        
        centerX = self.app.win.getXSize() // 2
        centerY = self.app.win.getYSize() // 2

        md = self.app.win.getPointer(0)
        self.lastMouseX = md.getX()
        self.lastMouseY = md.getY()
        
        properties = WindowProperties()
        properties.setCursorHidden(True)
        properties.setMouseMode(WindowProperties.M_confined)
        self.app.win.movePointer(0,centerX,centerY)
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
        # Heads-up display
        if self.app.args.pos:
            pos = self.app.camera.getPos()
            hpr = self.app.camera.getHpr()
            self.posText.setText(f"X: {pos.x:.1f} Y: {pos.y:.1f} Z: {pos.z:.1f} | H: {hpr.x:.1f} P: {hpr.y:.1f}")
        
        dt = globalClock.getDt()
        
        playerMoveSpeed = 10
        
        xMovement = 0
        yMovement = 0
        zMovement = 0

        if self.activeKeys['forward']:
            xMovement -= dt * playerMoveSpeed * sin(degToRad(self.app.camera.getH()))
            yMovement += dt * playerMoveSpeed * cos(degToRad(self.app.camera.getH()))
        if self.activeKeys['backward']:
            xMovement += dt * playerMoveSpeed * sin(degToRad(self.app.camera.getH()))
            yMovement -= dt * playerMoveSpeed * cos(degToRad(self.app.camera.getH()))
        if self.activeKeys['left']:
            xMovement -= dt * playerMoveSpeed * cos(degToRad(self.app.camera.getH()))
            yMovement -= dt * playerMoveSpeed * sin(degToRad(self.app.camera.getH()))
        if self.activeKeys['right']:
            xMovement += dt * playerMoveSpeed * cos(degToRad(self.app.camera.getH()))
            yMovement += dt * playerMoveSpeed * sin(degToRad(self.app.camera.getH()))
        if self.activeKeys['up']:
            zMovement += dt * playerMoveSpeed
        if self.activeKeys['down']:
            zMovement -= dt * playerMoveSpeed


        self.app.camera.setPos(
            self.app.camera.getX() + xMovement,
            self.app.camera.getY() + yMovement,
            self.app.camera.getZ() + zMovement,
        )
        
        if self.cameraSwingActivated:
            md = self.app.win.getPointer(0)
            mouseX = md.getX()
            mouseY = md.getY()
            
            mouseChangeX = mouseX - self.lastMouseX
            mouseChangeY = mouseY - self.lastMouseY
            
            self.cameraSwingFactor = 10
            
            currH = self.app.camera.getH()
            currP = self.app.camera.getP()
            if mouseChangeX != 0 and mouseChangeY != 0:
                self.app.camera.setHpr(
                    (currH - mouseChangeX * dt * self.cameraSwingFactor,
                     min(90, max(-90, currP - mouseChangeY * dt * self.cameraSwingFactor)),
                     0
                     ))
                self.lastMouseX = mouseX
                self.lastMouseY = mouseY
            
                x = self.app.win.getXSize() // 2
                y = self.app.win.getYSize() // 2
                
                if self.app.win.movePointer(0, x, y):
                    self.lastMouseX = x
                    self.lastMouseY = y
        
        return task.cont
