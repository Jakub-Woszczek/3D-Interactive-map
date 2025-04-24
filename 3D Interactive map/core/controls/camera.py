from direct.gui.OnscreenImage import OnscreenImage
from panda3d.core import TransparencyAttrib, WindowProperties


def setupCamera(self):
    self.disableMouse()
    self.camera.setPos(0, 0, 3)
    self.camLens.setFov(80)
    

def captureMouse(self):
    # self.cameraSwingActivated = True
    #
    # md = self.win.getPointer(0)
    # self.lastMouseX = md.getX()
    # self.lastMouseY = md.getY()

    properties = WindowProperties()
    properties.setCursorHidden(True)
    properties.setMouseMode(WindowProperties.M_relative)
    self.win.requestProperties(properties)

def releaseMouse(self):
    # self.cameraSwingActivated = False

    properties = WindowProperties()
    properties.setCursorHidden(False)
    properties.setMouseMode(WindowProperties.M_absolute)
    self.win.requestProperties(properties)