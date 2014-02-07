import unittest
import os
from gedcom import *


class McIntyreTest(unittest.TestCase):
    """Unit tests for records.py using mcintyre.ged."""

    def setUp(self):
        self.g = Gedcom(os.path.abspath('test/mcintyre.ged'))

    def test_individual(self):
        """Testing class Individual"""
        mary = self.g.get_individual('@P405366386@')

        self.assertEqual(mary.type(), 'Individual')
       
        self.assertEqual(mary.birth().dateplace(), ('19 Nov 1923', 'Louisiana, USA'))
        self.assertEqual(mary.alive(), True)
        self.assertEqual(mary.father().alive(), False)
        self.assertEqual(mary.father().death().dateplace(), ('19 Aug 1975', 'Bastrop, Louisiana'))
        self.assertEqual(mary.sex(), 'F')
        self.assertEqual(mary.given_name(), 'Mary Christine')
        self.assertEqual(mary.surname(), 'Hern')
        self.assertEqual(mary.fathers_name(), 'Thomas Clyde')

        self.assertEqual(mary.deceased(), False)
        self.assertEqual(mary.death(), None)
           
        self.assertEqual(map(lambda x: x.xref(), mary.parent_families()), ['@F5@'])
        self.assertEqual(map(lambda x: x.husband().xref(), mary.parent_families()), ['@P405368888@'])
        self.assertEqual(mary.father().xref(), '@P405368888@')
        self.assertEqual(mary.mother().xref(), '@P405538002@')
        self.assertEqual(map(lambda x: x.xref(), mary.families()), ['@F4@'])
        self.assertEqual(mary.father().children(), [mary])

    def test_family(self):
        """Testing class Family"""
        fam = self.g.get_family('@F8@')

        self.assertEqual(fam.marriage().dateplace(), ('22 Oct 1821', 'Jefferson County, Mississippi, USA'))

    def test_relatives(self):
        """Testing Individual methods concerned with finding a relative"""
        mary = self.g.get_individual('@P405366386@')

        self.assertEqual(mary.common_ancestor(mary), mary)
        self.assertEqual(mary.common_ancestor(mary.father()), mary.father())
        self.assertEqual(mary.father().common_ancestor(mary), mary.father())

        chris = self.g.get_individual('@P405749335@')
        barbara = self.g.get_individual('@P407946950@')
        marys_husband = self.g.get_individual('@P405364205@')
        self.assertEqual(chris.common_ancestor(barbara) in [mary, marys_husband], True)
        self.assertEqual(barbara.common_ancestor(chris) in [mary, marys_husband], True)
        self.assertEqual(barbara.is_relative(chris), True)
        self.assertEqual(chris.is_relative(barbara), True)

        will = self.g.get_individual('@P407996928@')
        self.assertEqual(barbara.is_relative(will), False)
        self.assertEqual(chris.is_relative(will), True)

        self.assertEqual(barbara.distance_to_ancestor(mary), 1)
        self.assertEqual(chris.distance_to_ancestor(mary), 3)
        self.assertEqual(map(lambda x: x.xref(), chris.down_path(mary, barbara, 1)), ['@P405366386@'])
        self.assertEqual(map(lambda x: x.xref(), chris.down_path(mary, chris, 3)), ['@P405366386@', '@P405342543@', '@P405313470@'])

        kimberly = self.g.get_individual('@P405313470@')
        marsha = self.g.get_individual('@P405342543@')

        self.assertTrue(marsha.is_relative(kimberly))
        self.assertTrue(kimberly.is_relative(marsha))

        self.assertFalse(marsha.is_parent(kimberly))
        self.assertTrue(kimberly.is_parent(marsha))

        self.assertFalse(marsha.is_sibling(kimberly))
        self.assertFalse(kimberly.is_sibling(marsha))

        self.assertFalse(marsha.is_parent(barbara))
        self.assertFalse(barbara.is_parent(marsha))

        self.assertTrue(marsha.is_sibling(barbara))
        self.assertTrue(barbara.is_sibling(marsha))

        self.assertEqual(map(lambda (x, y): (x.xref(), y), chris.path_to_relative(barbara)), [('@P405749335@', 'start'), ('@P405313470@', 'parent'), ('@P405342543@', 'parent'), ('@P407946950@', 'sibling')])
        
        self.assertEqual(map(lambda (x, y): (x.xref(), y), barbara.path_to_relative(chris)), [('@P407946950@', 'start'), ('@P405342543@', 'sibling'), ('@P405313470@', 'child'), ('@P405749335@', 'child')])

    def test_spaces(self):
        """Testing indenting spaces"""
        ernest = self.g.get_individual('@P405362004@')

        self.assertEqual(ernest.type(), 'Individual')

        notes = ernest.children_tags('NOTE')
        self.assertEqual(len(notes), 1)
        self.assertEqual(notes[0].value(), '    Ma and Papa')
       
class WrightTest(unittest.TestCase):
    """Unit tests for records.py using wright.ged."""

    def setUp(self):
        self.g = Gedcom(os.path.abspath('test/wright.ged'))

    def test_individual(self):
        """Testing class Individual"""
        delores = self.g.get_individual('@I294@')

        self.assertEqual(delores.type(), 'Individual')

        self.assertEqual(delores.birth().dateplace(), ('24 JUL 1963', ''))
        self.assertEqual(delores.sex(), 'F')
        self.assertEqual(delores.given_name(), 'Delores')
        self.assertEqual(delores.surname(), 'Hyatt')
        self.assertEqual(delores.fathers_name(), 'HORACE')

        self.assertEqual(delores.deceased(), False)
        self.assertEqual(delores.death(), None)
           
        self.assertEqual(map(lambda x: x.xref(), delores.parent_families()), ['@F159@'])
        self.assertEqual(map(lambda x: x.xref(), delores.families()), ['@F295@'])
        self.assertEqual(delores in delores.father().children(), True)

    def test_family(self):
        """Testing class Family"""
        family = self.g.get_family('@F1@')

        self.assertEqual(family.husband().name(), ('Cosmond G', 'Wright'))
        self.assertEqual(family.married(), True)
        self.assertEqual(family.marriage().dateplace(), ('1 SEP 1973', 'Troronto, Ontario, Canada')) #sic :-)
        

if __name__ == '__main__':
    unittest.main()
