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
        self.gameControls = Controls(self)
        self.terrainMeshNode = []
        self.terrainMeshConfig = DEFAULT_MESH_CONFIG
        self.settingsUI = SettingsUI(self)
        
        self.gameControls.setupControls(self)
        self.gameControls.setupCamera(self)
        self.loadMapObjs()
        
        taskMgr.add(self.gameControls.update, 'update')
    
    def loadMapObjs(self):
        """
        Creates objs on in game, terrain, background and routes from config
        :return:
        """
        gridGenerator.generateMeshFromCSV(self,DEFAULT_MESH_CONFIG)
        bgGenerator.generateBg(self)
        self.queue.put("completed")
        if not self.queue.empty():
            item = self.queue.get()
            if isinstance(item, list):
                generateRoutes(self, item)
    
    def clearMesh(self):
        """
        Removes all terrain nodes (used during change of map colours)
        """
        for node in self.terrainMeshNode:
            node.removeNode()
        self.terrainMeshNode.clear()
    
    def updateMeshColor(self,config):
        """
        If the current map type differs from the one selected in the config,
        the function removes the existing map and creates a new one.
        """
        if self.terrainMeshConfig == config:
            return
        self.clearMesh()
        gridGenerator.generateMeshFromCSV(self,config)
        self.terrainMeshConfig = config
        
def runMap(q):
    game = MyGame(q)
    game.run()