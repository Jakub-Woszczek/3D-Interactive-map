from direct.showbase.ShowBase import ShowBase
from direct.task.TaskManagerGlobal import taskMgr
from core.controls.controls import Controls
from mapObjs import gridGenerator
from mapObjs.routesGenerator import generateRoutes


class MyGame(ShowBase):
    def __init__(self, queue):
        ShowBase.__init__(self)
        self.queue = queue
        self.game_controls = Controls(self)
        self.game_controls.setupControls(self)
        self.game_controls.setupCamera(self)
        gridGenerator.generateMeshFromCSV(self)
        queue.put("completed")
        generateRoutes(self,self.queue.get())
        
        taskMgr.ad3d(self.game_controls.update, 'update')
        
def runMap(q):
    game = MyGame(q)
    game.run()