from core.controls import camera

def setupControls(self):
    self.accept('escape', self.releaseMouse)
    self.accept('mouse1',self.captureMouse)