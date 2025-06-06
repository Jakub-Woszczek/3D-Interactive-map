from copy import deepcopy
import numpy as np

from assets.peaks import peaksData
from assets.topsEdgesGraph import edges
from assets.routesTimeing import routeTime

class Graph:
    def __init__(self):
        # Pixel coordinates of tops: topsCoords[topID] = (pixelRow, pixelCol)
        self.topsCoords = []

        # Adjacency graph: adjGraph[topIdx] = [(neighbourTopIdx, edgeIdx), ...]
        self.adjGraph = self.createAdjacencyGraph()

        # Pixel coordinates of routes: routes[routeIdx] = [(pixelRow, pixelCol), ...]
        self.routes = []

        # Height values: heightMap[rowIdx, colIdx] = height
        self.heightMap = None

        # Travel time for each edge: edgeWeights[edgeIdx] = time
        self.edgeWeights = routeTime

        # Init functions
        self.importTopsCoords()
        self.importRoutes()
        self.importMapHeights()
        
    def importTopsCoords(self):
        self.topsCoords = [(row, col) for _, (row, col) in peaksData]
    
    def createAdjacencyGraph(self):
        """
        Creates graph where
        G[topIdx] = [(neighbourTopIdx,edgeIdx),...]
        and counts tops
        :return:
        """
        self.topsAmnt = max(max(edge) for edge in edges) + 1
        adj = [[] for _ in range(self.topsAmnt)]
        for idx, (a, b) in enumerate(edges):
            adj[a].append((b, idx))
            adj[b].append((a, idx))
        return adj
    
    def importRoutes(self):
        for i in range(33):
            with open(f"assets/Trasy/t{i}.txt",'r') as f:
                route = []
                for line in f:
                    line = line.strip()
                    if line.startswith('(') and line.endswith(')'):
                        xStr, yStr = line[1:-1].split(',')
                        x = int(xStr.strip())
                        y = int(yStr.strip())
                        route.append((x, y))
                self.routes.append(route)
    
    def importMapHeights(self):
        zFile = "assets/mapaTerenu"
        self.heightMap = np.loadtxt(zFile, delimiter=",")
    
    def findShortestPath(self, top1Idx, top2Idx):
        """
        Returns list of edge indices for shortest path from top1Idx to top2Idx
        using Dijkstra's algorithm.
        """
        import heapq
        dist = [float("inf")] * len(self.adjGraph)
        prev = [None] * len(self.adjGraph)
        prevEdge = [None] * len(self.adjGraph)
        
        dist[top1Idx] = 0
        heap = [(0, top1Idx)]
        
        while heap:
            currDist, u = heapq.heappop(heap)
            if currDist > dist[u]:
                continue
            if u == top2Idx:
                break
            
            for v, edgeIdx in self.adjGraph[u]:
                weight = self.edgeWeights[edgeIdx]
                if dist[v] > dist[u] + weight:
                    dist[v] = dist[u] + weight
                    prev[v] = u
                    prevEdge[v] = edgeIdx
                    heapq.heappush(heap, (dist[v], v))
        
        path = []
        curr = top2Idx
        while prev[curr] is not None:
            path.append(prevEdge[curr])
            curr = prev[curr]
        
        if curr != top1Idx:
            return []
        
        path.reverse()
        return path
    
    def getElevationProfile(self, topsIdx):
        """
        :param topsIdx: Array of indexes of tops from start to end
        :return: Array of elevation profile shortest path crosses
        """
        if len(topsIdx) < 2:
            return [],[]
        def cumsumList(arr):
            result = []
            total = 0
            for num in arr:
                total += num
                result.append(total)
            return result
            
        elevationProfile = []
        distances = [0 for _ in range(len(topsIdx) - 1)]
        
        allPaths = [
            self.findShortestPath(a, b)
            for a, b in zip(topsIdx, topsIdx[1:])
        ]
        
        allPathsLengths = [len(el) for el in allPaths]
        
        allPathsLengthsCopy = deepcopy(allPathsLengths)
        edgesPath = sum(allPaths, [])  # Flatten edges array
        
        i = 0
        lastSpot = self.topsCoords[topsIdx[0]]
        
        for edgeIdx in edgesPath:
            route = self.routes[edgeIdx]
            n = len(route)
            partialElevation = [self.heightMap[row][col] for row, col in route]
            
            if route[0] != lastSpot:
                partialElevation.reverse()
                lastSpot = route[0]
            else:
                lastSpot = route[n-1]
            
            if i >= len(allPathsLengths) or allPathsLengths[i] == 0:
                i += 1
                if i >= len(allPathsLengths):  # prevent index error
                    break
            
            distances[i] += len(partialElevation)
            elevationProfile.append(partialElevation)
            allPathsLengths[i] -= 1
        
        elevationProfile = sum(elevationProfile, [])
        
        # Cumulative dist between tops
        visited = []
        i = 0
        for amnt in allPathsLengthsCopy:
            visited.append(sum(distances[i:i + amnt]))
            i += 1

        
        return elevationProfile, cumsumList([0] + distances)
    
    def getTravelTime(self, topsIdx):
        """
        Computes the total travel time along the shortest path that passes through the given top indices.
        :return: Total travel time
        """
        allPaths = [
            self.findShortestPath(a, b)
            for a, b in zip(topsIdx, topsIdx[1:])
        ]
        edgesPath = sum(allPaths, [])  # Flatten edges array
        return sum(self.edgeWeights[idx] for idx in edgesPath)
        
            
        
        
        