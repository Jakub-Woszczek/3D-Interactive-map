from direct.gui.DirectButton import DirectButton
from direct.gui.DirectFrame import DirectFrame
from direct.gui.DirectLabel import DirectLabel
from direct.gui.DirectRadioButton import DirectRadioButton
from panda3d.core import TransparencyAttrib, TextNode
from map3D.mapConfig import DEFAULT_MESH_CONFIG,MESH_BY_HEIGHT,MESH_BY_SLOPE

class SettingsUI:
    def __init__(self,app):
        self.app = app
        self.optsFrame = None
        self.optsButton = None
        self.color_scheme = self.app.terrainMeshConfig
        self.color_scheme_var = [self.color_scheme]
        
        self.createSettingsIcon()
    
    def createSettingsIcon(self):
        iconTexture = self.app.loader.loadTexture('assets\settingsIcon.png')
        self.optsButton = DirectButton(
            image=iconTexture,
            scale=0.1,
            pos=(-0.1, 0, -0.1),
            command=self.openSettingsWindow,
            frameColor=(0, 0, 0, 0),
            parent=self.app.a2dTopRight
        )
        self.optsButton.setTransparency(TransparencyAttrib.MAlpha)

    
    def openSettingsWindow(self):
        
        if self.optsFrame:
            self.closeSettings()
            return
        
        self.optsFrame = DirectFrame(
            frameColor=(0, 0, 0, 0.8),
            frameSize=(-0.5, 0.5, -0.4, 0.4),
            pos=(0, 0, 0)
        )
        
        DirectLabel(
            parent=self.optsFrame,
            text="USTAWIENIA",
            scale=0.08,
            pos=(0, 0, 0.32),
            pad=(0.2, 0.1),
            text_fg=(0, 0, 0, 1),
        )
        
        DirectLabel(
            parent=self.optsFrame,
            text="<- Color scheme",
            scale=0.06,
            pos=(0.04, 0, 0.15),
            pad=(0.2, 0.1),
            text_align=TextNode.ALeft,
            text_fg=(0, 0, 0, 1)
        )
        
        self.color_scheme_var[0] = 0 if self.color_scheme == MESH_BY_HEIGHT else 1
        btn1 = DirectRadioButton(
            text="Height oriented",
            variable=self.color_scheme_var,
            value=[0],
            scale=0.05,
            pos=(-0.18, 0, 0.20),
            pad=(0.2, 0.1),
            parent=self.optsFrame,
            command=lambda: self.select_scheme(MESH_BY_HEIGHT)
        )
        
        btn2 = DirectRadioButton(
            text="Slope oriented",
            variable=self.color_scheme_var,
            value=[1],
            scale=0.05,
            pos=(-0.18, 0, 0.10),
            pad=(0.2, 0.1),
            parent=self.optsFrame,
            command=lambda: self.select_scheme(MESH_BY_SLOPE)
        )
        
        # Entwine buttons
        btn1.setOthers([btn2])
        btn2.setOthers([btn1])

        DirectButton(
            parent=self.optsFrame,
            text="Save",
            scale=0.06,
            pos=(0, 0, 0),
            pad=(0.2, 0.1),
            command=self.saveSettings
        )
        
        DirectButton(
            parent=self.optsFrame,
            text="Exit Game",
            scale=0.06,
            pos=(0, 0, -0.16),
            pad=(0.2, 0.1),
            command=self.exitGame
        )
        
        DirectButton(
            parent=self.optsFrame,
            text="Back to Game",
            scale=0.06,
            pos=(0, 0, -0.24),
            pad=(0.2, 0.1),
            command=self.closeSettings
        )
        
        # DirectButton(
        #     parent=self.optsFrame,
        #     text="Back to Menu",
        #     scale=0.06,
        #     pos=(0, 0, -0.32),
        #     pad=(0.2, 0.1),
        #     command=self.backToMenu
        # )
        return
    
    def closeSettings(self):
        self.optsFrame.destroy()
        self.optsFrame = None
    
    def exitGame(self):
        self.app.userExit()
    
    def select_scheme(self,scheme):
        self.color_scheme = scheme
    
    def saveSettings(self):
        self.app.updateMeshColor(self.color_scheme)
        return
    
    # def backToMenu(self):
    #     print("back to menu")
    #     return