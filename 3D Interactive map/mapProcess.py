from direct.showbase.ShowBase import ShowBase
from direct.task.TaskManagerGlobal import taskMgr
from core.controls.controls import Controls
from terrainGenerator import gridGenerator


class MyGame(ShowBase):
    def __init__(self, config):
        ShowBase.__init__(self)
        self.config = config
        self.game_controls = Controls(self)
        self.game_controls.setupControls(self)
        self.game_controls.setupCamera(self)
        gridGenerator.generateMeshFromCSV(self)
        
        taskMgr.add(self.game_controls.update, 'update')
        
def run_map(config_queue):
    # config = config_queue.get()
    game = MyGame(config_queue)
    game.run()