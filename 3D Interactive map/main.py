from direct.showbase.ShowBase import ShowBase
from direct.task.TaskManagerGlobal import taskMgr
from panda3d.core import WindowProperties
from core.controls.controls import Controls
from poceduralLandmassGenerator import gridGenerator
import argparse

class MyGame(ShowBase):
    def __init__(self,args):
        ShowBase.__init__(self)
        self.args = args
        self.game_controls = Controls(self)
        self.game_controls.setupControls(self)
        self.game_controls.setupCamera(self)
        gridGenerator.generateMeshFromCSV(self)
        
        taskMgr.add(self.game_controls.update, 'update')

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--scale",type=int,default=1, help="Sampling step for height values.")
    parser.add_argument("-pos", help="Current position display.",action="store_true")
    args = parser.parse_args()

    game = MyGame(args)
    game.run()