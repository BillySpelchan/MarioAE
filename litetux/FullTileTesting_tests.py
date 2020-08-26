import unittest
from litetux import LTMap
from litetux import FullTileTesting

SMALL_TEST_MAP = "{\"width\":4, \"height\":4, \"_mapData\":[[0,1,2,3],[4,5,6,7],[8,9,10,11],[12,13,14,15]]}"
SMALL_TEST_MAP_INVERSED = "{\"width\":4, \"height\":4, \"_mapData\":[[15,14,13,12],[11,10,9,8],[7,6,5,4],[3,2,1,0]]}"
SMALL_TEST_MAP_MID_MIXED = "{\"width\":4, \"height\":4, \"_mapData\":[[0,1,2,3],[4,4,5,7],[8,14,5,11],[12,13,14,15]]}"


class MyTestCase(unittest.TestCase):

    def test_same_map_comparison(self):
        lvl1 = LTMap.LiteTuxMap(4, 4)
        lvl1.from_json_string(SMALL_TEST_MAP)
        mt = FullTileTesting.MapTest(lvl1, lvl1)
        self.assertEqual(mt.get_total_tile_errors(), 0)
        self.assertEqual(mt.get_total_hamming_error(), 0)
        self.assertEqual(mt.get_average_tile_hamming_error(), 0)
        self.assertEqual(mt.hamming_errors_to_string(), "0000\n0000\n0000\n0000\n")
        self.assertEqual(mt.get_total_distance_error(), 0)
        self.assertEqual(mt.get_average_distance_error(), 0)
        self.assertEqual(mt.distance_errors_to_string(), "0 0 0 0 \n0 0 0 0 \n0 0 0 0 \n0 0 0 0 \n")

    def test_inverted_map_comparison(self):
        lvl1 = LTMap.LiteTuxMap(4, 4)
        lvl1.from_json_string(SMALL_TEST_MAP)
        lvl2 = LTMap.LiteTuxMap(4, 4)
        lvl2.from_json_string(SMALL_TEST_MAP_INVERSED)
        mt = FullTileTesting.MapTest(lvl1, lvl2)
        self.assertEqual(mt.get_total_tile_errors(), 16)
        self.assertEqual(mt.get_total_hamming_error(), 64)
        self.assertEqual(mt.get_average_tile_hamming_error(), 4.0)
        self.assertEqual(mt.hamming_errors_to_string(), "4444\n4444\n4444\n4444\n")
        self.assertEqual(mt.get_total_distance_error(), 128)
        self.assertEqual(mt.get_average_distance_error(), 8.0)
        self.assertEqual(mt.distance_errors_to_string(), "15 7 1 9 \n13 5 3 11 \n11 3 5 13 \n9 1 7 15 \n")

    def test_bad_middle_map_comparison(self):
        lvl1 = LTMap.LiteTuxMap(4, 4)
        lvl1.from_json_string(SMALL_TEST_MAP)
        lvl2 = LTMap.LiteTuxMap(4, 4)
        lvl2.from_json_string(SMALL_TEST_MAP_MID_MIXED)
        mt = FullTileTesting.MapTest(lvl1, lvl2)
        self.assertEqual(mt.get_total_tile_errors(), 4)
        self.assertEqual(mt.get_total_hamming_error(), 10)
        self.assertEqual(mt.get_average_tile_hamming_error(), 0.625)
        self.assertEqual(mt.hamming_errors_to_string(), "0000\n0130\n0240\n0000\n")
        self.assertEqual(mt.get_total_distance_error(), 12)
        self.assertEqual(mt.get_average_distance_error(), 0.75)
        self.assertEqual(mt.distance_errors_to_string(), "0 0 0 0 \n0 1 5 0 \n0 1 5 0 \n0 0 0 0 \n")

if __name__ == '__main__':
    unittest.main()
