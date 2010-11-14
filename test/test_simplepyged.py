import unittest
import os
from gedcom import *


class McIntyreTest(unittest.TestCase):
    """Unit tests for simplepyged using mcintyre.ged."""

    def setUp(self):
        self.g = Gedcom(os.path.abspath('test/mcintyre.ged'))

    def test_parser(self):
        """Check if parser collected all records"""
        self.assertEqual(len(self.g.record_dict()), 57)

        self.assertEqual(len(self.g.individual_list()), 41)
        self.assertEqual(len(self.g.family_list()), 16)
              

    def test_missing_xref(self):
        """I don't really know what this does... (original author didn't bother to comment) """
        for e in self.g.line_list():
            if e.value().startswith('@'):
                f = self.g.record_dict().get(e.value(),None)
                if f == None:
                    print e.value()

        for e in self.g.line_list():
            if e.xref() == "@I99@":
                print e.name()


if __name__ == '__main__':
    unittest.main()
