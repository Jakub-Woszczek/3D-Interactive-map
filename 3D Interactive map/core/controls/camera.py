# from direct.gui.OnscreenImage import OnscreenImage
# from panda3d.core import TransparencyAttrib, WindowProperties

from panda3d.core import WindowProperties


def setupCamera(self):
    properties = WindowProperties()
    properties.setMouseMode(WindowProperties.M_relative)
    self.app.win.requestProperties(properties)
    
    self.disableMouse()
    self.camera.setPos(0, 0, 3)
    self.camLens.setFov(80)
    
    
# def captureMouse(self):
#
#     properties = WindowProperties()
#     properties.setCursorHidden(True)
#     properties.setMouseMode(WindowProperties.M_relative)
#     self.win.requestProperties(properties)
#
# def releaseMouse(self):
#
#     properties = WindowProperties()
#     properties.setCursorHidden(False)
#     properties.setMouseMode(WindowProperties.M_absolute)
#     self.win.requestProperties(properties)