import unittest
import sys
sys.path.append(sys.path[0]+'/../')
from sgmltools import AMMtools

class TestSGMLtools(unittest.TestCase):

    def test_zones(self):
        testdata = AMMtools('test_data/', sourcefile='pretopic.txt')
        self.assertEqual(testdata.zone_panHandler(testdata.manual.find("pretopic"), "zone"), {'197'})



if __name__ == '__main__':
    unittest.main()


##    
##testdata = AMMtools('test_data/', sourcefile='pretopic.txt')
##print(testdata.zone_panHandler(testdata.manual.find("pretopic"), "panel"))
