import unittest
import os
from simplepyged.gedcom import *


class McIntyreTest(unittest.TestCase):
    """Unit tests for records.py using mcintyre.ged."""

    def setUp(self):
        self.g = Gedcom(os.path.abspath('test/mcintyre.ged'))
        self.kim = self.g.get_individual('@P405313470@')
        self.marsha = self.g.get_individual('@P405342543@')
        self.mary = self.g.get_individual('@P405366386@')
        self.chris = self.g.get_individual('@P405749335@')
        self.barbara = self.g.get_individual('@P407946950@')
        self.marys_husband = self.g.get_individual('@P405364205@')

    def test_individual(self):
        """Testing class Individual"""
        self.assertEqual(self.mary.type(), 'Individual')
       
        self.assertEqual(self.mary.birth().dateplace(), ('19 Nov 1923', 'Louisiana, USA'))
        self.assertEqual(self.mary.alive(), True)
        self.assertEqual(self.mary.father().alive(), False)
        self.assertEqual(self.mary.father().death().dateplace(), ('19 Aug 1975', 'Bastrop, Louisiana'))
        self.assertEqual(self.mary.sex(), 'F')
        self.assertEqual(self.mary.given_name(), 'Mary Christine')
        self.assertEqual(self.mary.surname(), 'Hern')
        self.assertEqual(self.mary.fathers_name(), 'Thomas Clyde')

        self.assertEqual(self.mary.deceased(), False)
        self.assertEqual(self.mary.death(), None)
           
        self.assertEqual(self.mary.parent_family().xref(), '@F5@')
        self.assertEqual(self.mary.parent_family().husband().xref(), '@P405368888@')
        self.assertEqual(map(lambda x: x.xref(), self.mary.parent_families()), ['@F5@'])
        self.assertEqual(map(lambda x: x.husband().xref(), self.mary.parent_families()), ['@P405368888@'])
        self.assertEqual(self.mary.father().xref(), '@P405368888@')
        self.assertEqual(self.mary.mother().xref(), '@P405538002@')
        self.assertEqual(self.mary.family().xref(), '@F4@')
        self.assertEqual(map(lambda x: x.xref(), self.mary.families()), ['@F4@'])
        self.assertEqual(self.mary.father().children(), [self.mary])

    def test_family(self):
        """Testing class Family"""
        fam = self.g.get_family('@F8@')

        self.assertEqual(fam.marriage().dateplace(), ('22 Oct 1821', 'Jefferson County, Mississippi, USA'))

        daniel = fam.children()[0]
        calvin = fam.children()[2]

        self.assertEqual(map(lambda x: x.xref(), daniel.siblings()), ['@P405608614@', '@P405613353@', '@P405421877@'])
        self.assertEqual(daniel.mutual_parent_families(calvin), [fam])
        
        self.assertEqual(map(lambda x: x.xref(), self.kim.common_ancestor_families(self.barbara)), ['@F4@'])
        
        michael = self.kim.siblings()[1]
        self.assertEqual(self.kim.mutual_parent_families(michael), self.kim.parent_families())
        self.assertEqual(self.kim.mutual_parent_families(self.barbara), [])

    def test_ancestors(self):
        """Testing Individual methods concerned with finding ancestors"""
        self.assertRaises(MultipleReturnValues, self.mary.common_ancestor, self.mary)
        self.assertEqual(self.mary.common_ancestors(self.mary), [self.mary.father(), self.mary.mother()])
        self.assertEqual(self.mary.common_ancestors(self.mary.father()), [self.mary.father().father(), self.mary.father().mother()])
        self.assertRaises(MultipleReturnValues, self.mary.father().common_ancestor, self.mary)
        self.assertEqual(self.mary.father().common_ancestors(self.mary), self.mary.father().parents())
        
        self.assertEqual(self.mary.common_ancestor_families(self.mary), self.mary.parent_families())
        self.assertEqual(self.mary.common_ancestor_families(self.mary.father()), self.mary.father().parent_families())
        self.assertEqual(self.mary.father().common_ancestor_families(self.mary), self.mary.father().parent_families())

        self.assertEqual(self.mary.father().common_ancestor_families(self.marys_husband), [])

        self.assertRaises(MultipleReturnValues, self.barbara.common_ancestor, self.chris)
        self.assertEqual(self.chris.common_ancestors(self.barbara), [self.marys_husband, self.mary])
        self.assertEqual(self.chris.common_ancestors(self.barbara), [self.marys_husband, self.mary])
        self.assertEqual(self.chris.common_ancestor_families(self.barbara), self.mary.families())
        self.assertEqual(self.barbara.common_ancestor_families(self.chris), self.mary.families())


    def test_relatives(self):
        """Testing Individual methods concerned with finding a relative"""
        self.assertEqual(self.barbara.is_relative(self.chris), True)
        self.assertEqual(self.chris.is_relative(self.barbara), True)

        self.assertEqual(self.barbara.distance_to_ancestor(self.mary), 1)
        self.assertEqual(self.chris.distance_to_ancestor(self.mary), 3)
        
        self.assertTrue(self.marsha.is_relative(self.kim))
        self.assertTrue(self.kim.is_relative(self.marsha))

        self.assertFalse(self.marsha.is_parent(self.kim))
        self.assertTrue(self.kim.is_parent(self.marsha))

        self.assertFalse(self.marsha.is_sibling(self.kim))
        self.assertFalse(self.kim.is_sibling(self.marsha))

        self.assertFalse(self.marsha.is_parent(self.barbara))
        self.assertFalse(self.barbara.is_parent(self.marsha))

        self.assertTrue(self.marsha.is_sibling(self.barbara))
        self.assertTrue(self.barbara.is_sibling(self.marsha))

    def test_family_relatives(self):
        """Testing Family methods concerned with finding a relative"""
        self.assertFalse(self.barbara.parent_family().is_relative(self.chris.father()))

        self.assertTrue(self.barbara.parent_family().is_relative(self.chris))
        self.assertTrue(self.chris.parent_family().is_relative(self.barbara))

        self.assertTrue(self.marsha.parent_family().is_relative(self.kim))
        self.assertTrue(self.kim.parent_family().is_relative(self.marsha))

        self.assertTrue(self.marsha.family().is_relative(self.kim))
        self.assertTrue(self.kim.family().is_relative(self.marsha))


    def test_direct_ancestors(self):
        """Test relatives which are direct ancestors."""

        will = self.chris.father()
        self.assertFalse(self.barbara.is_relative(will))
        self.assertTrue(self.chris.is_parent(will))
        self.assertTrue(self.chris.is_ancestor(will))
        self.assertTrue(self.chris.is_relative(will))

        john = self.g.get_individual('@P405431718@')
        p1 = john.children()[0]
        p2 = john.children()[3].children()[0].children()[0].children()[0].children()[1]

        self.assertTrue(p1.is_relative(p2))
        self.assertTrue(p2.is_relative(p1))
        self.assertTrue(p1.is_relative(john))
        self.assertTrue(p2.is_relative(john))
        self.assertTrue(john.is_relative(p1))
        self.assertTrue(john.is_relative(p2))

        self.assertFalse(john.is_ancestor(p1))
        self.assertFalse(john.is_ancestor(p2))

        self.assertTrue(p1.is_ancestor(john))
        self.assertTrue(p2.is_ancestor(john))
        
    def test_down_paths(self):
        """Testing Individual.down_path(). """
        self.assertEqual(map(lambda x: x.xref(), Individual.down_path(self.mary, self.mary)), ['@P405366386@'])
        self.assertEqual(map(lambda x: x.xref(), Individual.down_path(self.mary, self.barbara)), ['@P405366386@', '@P407946950@'])
        self.assertEqual(Individual.down_path(self.mary, self.chris, 2), None)
        self.assertEqual(map(lambda x: x.xref(), Individual.down_path(self.mary, self.chris, 3)), ['@P405366386@', '@P405342543@', '@P405313470@', '@P405749335@'])
        self.assertEqual(map(lambda x: x.xref(), Individual.down_path(self.mary, self.chris, 10)), ['@P405366386@', '@P405342543@', '@P405313470@', '@P405749335@'])
        self.assertEqual(map(lambda x: x.xref(), Individual.down_path(self.mary, self.chris)), ['@P405366386@', '@P405342543@', '@P405313470@', '@P405749335@'])


    def test_paths(self):
        """Testing paths to relatives. """
        self.assertEqual(self.mary.father().path_to_relative(self.marys_husband), None)

        self.assertEqual(map(lambda (x, y): (x.xref(), y), self.mary.path_to_relative(self.mary)), [('@P405366386@', 'start')])
        self.assertEqual(map(lambda (x, y): (x.xref(), y), self.mary.path_to_relative(self.barbara)), [('@P405366386@', 'start'), ('@P407946950@', 'child')])
        self.assertEqual(map(lambda (x, y): (x.xref(), y), self.mary.path_to_relative(self.chris)), [('@P405366386@', 'start'), ('@P405342543@', 'child'), ('@P405313470@', 'child'), ('@P405749335@', 'child')])
        self.assertEqual(map(lambda (x, y): (x.xref(), y), self.chris.path_to_relative(self.mary)), [('@P405749335@', 'start'), ('@P405313470@', 'parent'), ('@P405342543@', 'parent'), ('@P405366386@', 'parent')])

        self.assertEqual(map(lambda (x, y): (x.xref(), y), self.chris.path_to_relative(self.barbara)), [('@P405749335@', 'start'), ('@P405313470@', 'parent'), ('@P405342543@', 'parent'), ('@P405364205@', 'parent'), ('@P407946950@', 'child')])
        self.assertEqual(map(lambda (x, y): (x.xref(), y), self.chris.path_to_relative(self.barbara, compact = True)), [('@P405749335@', 'start'), ('@P405313470@', 'parent'), ('@P405342543@', 'parent'), ('@P407946950@', 'sibling')])
        
        self.assertEqual(map(lambda (x, y): (x.xref(), y), self.barbara.path_to_relative(self.chris)), [('@P407946950@', 'start'), ('@P405364205@', 'parent'), ('@P405342543@', 'child'), ('@P405313470@', 'child'), ('@P405749335@', 'child')])
        self.assertEqual(map(lambda (x, y): (x.xref(), y), self.barbara.path_to_relative(self.chris, compact = True)), [('@P407946950@', 'start'), ('@P405342543@', 'sibling'), ('@P405313470@', 'child'), ('@P405749335@', 'child')])

    def test_spaces(self):
        """Testing indenting spaces"""
        ernest = self.g.get_individual('@P405362004@')

        self.assertEqual(ernest.type(), 'Individual')

        notes = ernest.children_tags('NOTE')
        self.assertEqual(len(notes), 1)
        self.assertEqual(notes[0].value(), '    Ma and Papa')

    def test_parent_families(self):
        """Testing Family.parent_families and Family.ancestor_families_with_distance."""
        self.assertEqual(map(lambda x: x.xref(), self.chris.parent_family().parent_families()), ['@F1@'])

        katherine = self.g.get_individual('@P405433289@')
        john = self.g.get_individual('@P405421877@')
        kary = self.g.get_individual('@P405313479@')

        self.assertEqual(map(lambda (x, y): (x.xref(), y), katherine.ancestor_families_with_distance()), [('@F11@', 0)])        
        self.assertEqual(map(lambda (x, y): (x.xref(), y), john.ancestor_families_with_distance()), [('@F8@', 0), ('@F11@', 1)])        
        self.assertEqual(map(lambda (x, y): (x.xref(), y), kary.ancestor_families_with_distance()), [('@F2@', 0), ('@F3@', 1), ('@F15@', 1), ('@F6@', 2), ('@F7@', 3), ('@F8@', 4), ('@F16@', 4), ('@F11@', 5)])
        
    def test_latex_bug(self):
        """Unittests replicating a bug in latex example."""
        fam12 = self.g.get_family('@F12@')
        fam13 = self.g.get_family('@F13@')

        self.assertTrue(self.mary.is_relative(fam12.husband()))
        self.assertTrue(self.mary.path_to_relative(fam12.husband()))
        self.assertTrue(self.mary.is_relative(fam12.wife()))
        self.assertTrue(self.mary.path_to_relative(fam12.wife()))

        self.assertTrue(self.mary.is_relative(fam13.husband()))
        self.assertTrue(self.mary.path_to_relative(fam13.husband()))
        self.assertTrue(self.mary.is_relative(fam13.wife()))
        self.assertTrue(self.mary.path_to_relative(fam13.wife()))

        
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
        
        self.assertEqual(delores.parent_family().xref(), '@F159@')
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
