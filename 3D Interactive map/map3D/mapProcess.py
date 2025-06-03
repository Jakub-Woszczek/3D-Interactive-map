from direct.showbase.ShowBase import ShowBase
from direct.task.TaskManagerGlobal import taskMgr
from core.controls.controls import Controls
from map3D.settingsUI import SettingsUI
from mapObjs import gridGenerator
from mapObjs.routesGenerator import generateRoutes


class MyGame(ShowBase):
    def __init__(self, queue):
        ShowBase.__init__(self)
        self.queue = queue
        self.game_controls = Controls(self)
        self.game_controls.setupControls(self)
        self.game_controls.setupCamera(self)
        self.settingsUI = SettingsUI(self)
        gridGenerator.generateMeshFromCSV(self)
        queue.put("completed")
        if not queue.empty():
            item = queue.get()
            if isinstance(item, list):
                generateRoutes(self, item)
            else:
                pass
                # generateRoutes(self, [])
        
        taskMgr.add(self.game_controls.update, 'update')
        
def runMap(q):
    game = MyGame(q)
    game.run()