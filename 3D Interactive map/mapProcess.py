from direct.showbase.ShowBase import ShowBase
from direct.task.TaskManagerGlobal import taskMgr
from core.controls.controls import Controls
from terrainGenerator import gridGenerator


class MyGame(ShowBase):
    def __init__(self, queue):
        ShowBase.__init__(self)
        self.queue = queue
        self.game_controls = Controls(self)
        self.game_controls.setupControls(self)
        self.game_controls.setupCamera(self)
        gridGenerator.generateMeshFromCSV(self)
        queue.put("completed")
        taskMgr.add(self.game_controls.update, 'update')
        
def runMap(q):
    # config = config_queue.get()
    game = MyGame(q)
    game.run()