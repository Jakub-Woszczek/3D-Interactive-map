import unittest

from matplotlib import pyplot as plt

from menu.graph import Graph

class TestGraph(unittest.TestCase):
    def test_elevationProfile(self):
        graph = Graph()
        tops = [1,26,20,1,14,8]
        
        result,verticals = graph.getElevationProfile(tops)
        x = list(range(len(result)))
        
        plt.figure(figsize=(8, 4))
        plt.plot(x, result, label='Elevation')
        for v in verticals:
            plt.axvline(x=v, color='red', linestyle='--', linewidth=1,
                        label='Segment Break' if v == verticals[0] else None)
        plt.title('Elevation Profile')
        plt.xlabel('Distance (units)')
        plt.ylabel('Elevation (m)')
        plt.grid(True)
        plt.legend()
        plt.tight_layout()
        plt.show()

        self.assertTrue(len(result) > 0)

if __name__ == '__main__':
    unittest.main()