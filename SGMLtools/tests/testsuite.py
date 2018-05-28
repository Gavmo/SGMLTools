import unittest
import sys
sys.path.append(sys.path[0]+'/../')
from sgmltools import AMMtools

class TestSGMLtools(unittest.TestCase):

    def test_zones(self):
        testdata = AMMtools('test_data/', sourcefile='pretopic.txt')
        self.assertEqual(testdata.zone_panHandler(testdata.manual.find("pretopic"), "zone"), {'197'})

    def test_panels(self):
        testdata = AMMtools('test_data/', sourcefile='pretopic.txt')
        self.assertEqual(testdata.zone_panHandler(testdata.manual.find("pretopic"), "pan"), {'197MB'})

    def test_tools(self):
        testdata = AMMtools('test_data/', sourcefile='task.txt')
        self.assertEqual(testdata.toolHandler(testdata.manual.find("task")), [['98D57004013000', '2', 'HOOK-COVER (RIB 2 SURGE DOORS)'], ['98D57004014000', '2', 'HOOK-COVER (RIB2-SURGE DOORS)']])

    def test_cblst(self):
        testdata = AMMtools('test_data/', sourcefile='cblst.txt')
        self.assertEqual(testdata.cblstHandler(testdata.manual.find("cblst")), [{'pan': '121VU', 'effect': None, 'cb': '5-SQ-2', 'cbname': 'COM NAV/RADAR/2', 'cbloc': 'K14'}, {'pan': '121VU', 'effect': None, 'cb': '5-SQ-2', 'cbname': 'COM NAV/RADAR/2', 'cbloc': 'K14'}, {'pan': '122VU', 'effect': None, 'cb': '1-DA-1', 'cbname': 'ANTI ICE/PROBES/1/TAT', 'cbloc': 'Z12'}, {'pan': '122VU', 'effect': None, 'cb': '1-DA-1', 'cbname': 'ANTI ICE/PROBES/1/TAT', 'cbloc': 'Z12'}, {'pan': '122VU', 'effect': None, 'cb': '1-DA-1', 'cbname': 'ANTI ICE/PROBES/1/TAT', 'cbloc': 'Z12'}, {'pan': '122VU', 'effect': None, 'cb': '1-DA-1', 'cbname': 'ANTI ICE/PROBES/1/TAT', 'cbloc': 'Z12'}, {'pan': '122VU', 'effect': None, 'cb': '5-DA-2', 'cbname': 'ANTI ICE/PROBES/2/STATIC', 'cbloc': 'Y11'}, {'pan': '122VU', 'effect': None, 'cb': '5-DA-2', 'cbname': 'ANTI ICE/PROBES/2/STATIC', 'cbloc': 'Y11'}, {'pan': '122VU', 'effect': None, 'cb': '5-DA-2', 'cbname': 'ANTI ICE/PROBES/2/STATIC', 'cbloc': 'Y11'}, {'pan': '122VU', 'effect': None, 'cb': '5-DA-2', 'cbname': 'ANTI ICE/PROBES/2/STATIC', 'cbloc': 'Y11'}, {'pan': '122VU', 'effect': None, 'cb': '5-DA-3', 'cbname': 'ANTI ICE/PROBES/3/STATIC', 'cbloc': 'Z14'}, {'pan': '122VU', 'effect': None, 'cb': '5-DA-3', 'cbname': 'ANTI ICE/PROBES/3/STATIC', 'cbloc': 'Z14'}, {'pan': '122VU', 'effect': None, 'cb': '5-DA-3', 'cbname': 'ANTI ICE/PROBES/3/STATIC', 'cbloc': 'Z14'}, {'pan': '121VU', 'effect': None, 'cb': '4-FP-3', 'cbname': 'ADIRS/ADIRU/3/115VAC', 'cbloc': 'N05'}, {'pan': '121VU', 'effect': None, 'cb': '4-FP-3', 'cbname': 'ADIRS/ADIRU/3/115VAC', 'cbloc': 'N05'}, {'pan': '121VU', 'effect': None, 'cb': '4-FP-2', 'cbname': 'ADIRS/ADIRU/2/115VAC', 'cbloc': 'N06'}, {'pan': '121VU', 'effect': None, 'cb': '9-FP', 'cbname': 'ADIRS/ADIRU/3PWR/SWTG', 'cbloc': 'N09'}, {'pan': '121VU', 'effect': None, 'cb': '9-FP', 'cbname': 'ADIRS/ADIRU/3PWR/SWTG', 'cbloc': 'N09'}, {'pan': '121VU', 'effect': None, 'cb': '10-FP', 'cbname': 'ADIRS/2PWR/SHED &/AOA2 MON', 'cbloc': 'N10'}, {'pan': '121VU', 'effect': None, 'cb': '10-FP', 'cbname': 'ADIRS/2PWR/SHED &/AOA2 MON', 'cbloc': 'N10'}, {'pan': '121VU', 'effect': None, 'cb': '10-FP', 'cbname': 'ADIRS/2PWR/SHED &/AOA2 MON', 'cbloc': 'N10'}, {'pan': '121VU', 'effect': None, 'cb': '5-FP-3', 'cbname': 'ADIRS/ADIRU/3/26VAC AND AOA', 'cbloc': 'N07'}])

    def test_table(self):
        testdata = AMMtools('test_data/', sourcefile='table_3.txt')
        self.assertEqual(testdata.tableHandler(testdata.manual.find("table")),[['HEADER', 'ITEM', 'INSP CODE', 'INSPECTION TASKS', 'PHASE 1', 'PHASE 2', 'PHASE 3', 'INSP SIGN', 'REF. FIG.'], ['', '1.', '', '', '', '', '', ''], ['', 'A.', '', 'NOTE: If it is not possible to correctly do the inspection of the vertical stabilizer with the binoculars, you can do the inspection of the vertical stabilizer without binoculars (refer to method 1 inspection).', 'X', '', '', ''], ['', 'B.', '', 'Examine all the static dischargers for burn marks, damaged tip or breakage.', 'X', '', '', ''], ['', 'C.', '', 'Examine the parts that follow for burn marks, change of color, puncturing, delamination or other damage: - The skin of the vertical stabilizer and the rudder (specially the leading and trailing edges, the rudder surface in the hinge area and the antenna fairings) - The vertical stabilizer tip - The lightning conductor of the vertical stabilizer and rudder tips.', 'X', '', '', ''], ['', '', '', 'If you find damage: - Do a GVI of the vertical stabilizer (method 1 inspection).', '', 'X', '', '']])

if __name__ == '__main__':
    unittest.main()


##    
##testdata = AMMtools('test_data/', sourcefile='table_3.txt')
##print(testdata.manual.prettify())
##print(testdata.tableHandler(testdata.manual.find("table")))
##
