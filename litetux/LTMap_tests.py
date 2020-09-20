import unittest
from litetux import LTMap


class MyTestCase(unittest.TestCase):
    TEST_MAP = "{\"width\":12, \"height\":10, \"_mapData\":"+\
    "[[1 , 2, 2, 3, 3, 3, 4, 4, 4, 4, 5, 5]," +\
    " [5 , 5, 5, 6, 6, 6, 6, 6, 6, 7, 7, 7]," +\
    " [7 , 7, 7, 7, 8, 8, 8, 8, 8, 8, 8, 8]," +\
    " [9 , 9, 9, 9, 9, 9, 9, 9, 9,10,10,10]," +\
    " [10,10,10,10,10,10,10,11,11,11,11,11]," +\
    " [11,11,11,11,11,11,12,12,12,12,12,12]," +\
    " [12,12,12,12,12,12,13,13,13,13,13,13]," +\
    " [13,13,13,13,13,13,13,14,14,14,14,14]," +\
    " [14,14,14,14,14,14,14,14,14,15,15,15]," +\
    " [15,15,15,15,15,15,15,15,15,15,15,15] ] }"

    def test_map_frequency_count(self):
        test_map = LTMap.LiteTuxMap(1,1)
        test_map.from_json_string(self.TEST_MAP)
        
        tile_freq = LTMap.TileFrequencyMetric(test_map, 16)
        for t in range(16):
            self.assertEqual(tile_freq.get_tile_count(t), t)
        self.assertEqual(tile_freq.get_tile_percent(12), .1)

    def test_adding_map_to_TFM(self):
        test_map = LTMap.LiteTuxMap(1, 1)
        test_map.from_json_string(self.TEST_MAP)

        tile_freq = LTMap.TileFrequencyMetric(test_map, 16)
        tile_freq.add_map(test_map)
        for t in range(16):
            self.assertEqual(tile_freq.get_tile_count(t), t*2)
        self.assertEqual(tile_freq.get_tile_percent(12), .1)

    def test_group_frequency(self):
        test_map = LTMap.LiteTuxMap(1,1)
        test_map.from_json_string(self.TEST_MAP)
        tile_freq = LTMap.TileFrequencyMetric(test_map, 16)
        self.assertEqual(tile_freq.get_tile_group_count([1,7,10]), 18)
        self.assertEqual(tile_freq.get_tile_group_percentage([1,7,10]), .15)

    def test_frequency_report(self):
        test_map = LTMap.LiteTuxMap(1,1)
        test_map.from_json_string(self.TEST_MAP)
        tile_freq = LTMap.LiteTuxFrequencyMetrics(test_map)
        tile_freq.generate_report()

if __name__ == '__main__':
    unittest.main()
