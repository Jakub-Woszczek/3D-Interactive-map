from venv import create

from direct.gui.DirectButton import DirectButton
from direct.gui.DirectFrame import DirectFrame
from direct.gui.DirectLabel import DirectLabel
from direct.gui.DirectRadioButton import DirectRadioButton
from panda3d.core import TransparencyAttrib, TextNode


class SettingsUI:
    def __init__(self,app):
        self.app = app
        self.optsFrame = None
        self.optsButton = None
        self.color_scheme = 0 # 0 - height / 1 - slope
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
        print("sett window opened")
        
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
        
        # Podtytuł: Color scheme
        DirectLabel(
            parent=self.optsFrame,
            text="<- Color scheme",
            scale=0.06,
            pos=(0.04, 0, 0.15),
            pad=(0.2, 0.1),
            text_align=TextNode.ALeft,
            text_fg=(0, 0, 0, 1)
        )
        
        btn1 = DirectRadioButton(
            text="Height oriented",
            variable=self.color_scheme_var,
            value=[0],
            scale=0.05,
            pos=(-0.18, 0, 0.20),
            pad=(0.2, 0.1),
            parent=self.optsFrame,
            command=lambda: self.select_scheme(0)
        )
        
        btn2 = DirectRadioButton(
            text="Slope oriented",
            variable=self.color_scheme_var,
            value=[1],
            scale=0.05,
            pos=(-0.18, 0, 0.10),
            pad=(0.2, 0.1),
            parent=self.optsFrame,
            command=lambda: self.select_scheme(1)
        )
        
        # Połącz je w grupę
        btn1.setOthers([btn2])
        btn2.setOthers([btn1])
        
        if self.color_scheme == 0:
            btn1.setIndicatorValue()
            btn2["indicatorValue"] = False
            print("jestem1")
        else:
            btn2.setIndicatorValue()
            btn1["indicatorValue"] = False
            print("jestem2")

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
        from sys import exit
        exit()
    
    def select_scheme(self,scheme):
        self.color_scheme = scheme
        print("Wybrano:", scheme)
    
    def saveSettings(self):
        print("saving settings")
        return
    
    # def backToMenu(self):
    #     print("back to menu")
    #     return