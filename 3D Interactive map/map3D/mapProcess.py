from direct.showbase.ShowBase import ShowBase
from direct.task.TaskManagerGlobal import taskMgr
from core.controls.controls import Controls
from map3D.settingsUI import SettingsUI
from map3D.mapObjs import bgGenerator, gridGenerator
from map3D.mapObjs.routesGenerator import generateRoutes
from map3D.mapConfig import DEFAULT_MESH_CONFIG

class MyGame(ShowBase):
    def __init__(self, queue):
        ShowBase.__init__(self)
        self.queue = queue
        self.game_controls = Controls(self)
        self.terrainMeshNode = []
        self.terrainMeshConfig = DEFAULT_MESH_CONFIG
        self.game_controls.setupControls(self)
        self.game_controls.setupCamera(self)
        self.settingsUI = SettingsUI(self)
        self.loadMapObjs()
        
        taskMgr.add(self.game_controls.update, 'update')
    
    def loadMapObjs(self):
        gridGenerator.generateMeshFromCSV(self,DEFAULT_MESH_CONFIG)
        bgGenerator.generateBg(self)
        self.queue.put("completed")
        if not self.queue.empty():
            item = self.queue.get()
            if isinstance(item, list):
                generateRoutes(self, item)
            else:
                pass
                # generateRoutes(self, [])
    
    def clearMesh(self):
        for node in self.terrainMeshNode:
            node.removeNode()
        self.terrainMeshNode.clear()
    
    def updateMeshColor(self,config):
        if self.terrainMeshConfig == config:
            return
        self.clearMesh()
        gridGenerator.generateMeshFromCSV(self,config)
        self.terrainMeshConfig = config
        
def runMap(q):
    game = MyGame(q)
    game.run()