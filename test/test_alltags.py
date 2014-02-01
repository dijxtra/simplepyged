import unittest
import os
from gedcom import *


class AllTagsTest(unittest.TestCase):
    """Unit tests for simplepyged using the torture GED file."""

    def setUp(self):
        self.g = Gedcom(os.path.abspath('test/TGC55CLF.utf-8.ged'))

    def test_parser(self):
        """Check if parser collected all records"""
        self.assertEqual(len(self.g.individual_list()), 15)
        self.assertEqual(len(self.g.family_list()), 7)

    def test_indi(self):
        """Check that all 21 individual event types are handled (excluding
        BIRT and DEAT)"""
        torture = self.g.get_individual('@PERSON1@')
        uniq_events = set([e.tag for e in torture.other_events])
        self.assertEqual(len(uniq_events), 21)

    def test_fam(self):
        """Check that all 10 family event types are handled (excluding MARR)"""
        torture = self.g.get_family('@FAMILY1@')
        uniq_events = set([e.tag for e in torture.other_events])
        self.assertEqual(len(uniq_events), 10)

if __name__ == '__main__':
    unittest.main()
