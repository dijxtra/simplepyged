import unittest
import os
from gedcom import *
from matches import *

class McIntyreTest(unittest.TestCase):
    """Unit tests for matches.py using mcintyre.ged."""

    def setUp(self):
        self.g = Gedcom(os.path.abspath('test/mcintyre.ged'))

    def test_matches(self):
        """ Testing class MatchIndividual """
        visited = 0
        for e in self.g.line_list():
            m = MatchIndividual(e)
            if m.individual.type() == 'Individual':
                if m.surname_match('Merriman'):
                    visited += 1
                    self.assertEqual(m.individual.name()[0], 'Lucy')
                if m.given_match('Archibald'):
                    visited += 1
                    self.assertEqual(m.individual.name()[1], 'McIntyre')
                    self.assertEqual(m.birth_range_match(1810,1820), True)
                    self.assertEqual(m.birth_year_match(1819), True)
                if m.birth_year_match(1904):
                    visited += 1
                    self.assertEqual(m.individual.name(), ('Carrie Lee', 'Horney'))
                    self.assertEqual(m.death_range_match(1970,1980), True)
                    self.assertEqual(m.death_year_match(1979), True)
                    self.assertEqual(m.death_year_match(1978), False)
                if m.marriage_year_match(1821):
                    if m.marriage_range_match(1820,1825):
                        if m.surname_match('McIntyre'):
                            visited += 1
                            self.assertEqual(m.individual.name(), ('John M', 'McIntyre'))
        self.assertEqual(visited, 4)

    def test_matchlist(self):
        """ Testing class MatchList """
        m = MatchList(self.g.individual_list())

        results = m.surname_match('Merriman')
        individual = results[0]
        self.assertEqual(individual.given_name(), 'Lucy')

        results = m.given_match('Archibald')
        individual = results[0]
        self.assertEqual(individual.surname(), 'McIntyre')

        results = m.birth_year_match(1904)
        individual = results[0]
        self.assertEqual(individual.xref(), '@P405538002@')

    def test_criteria(self):
        """ Testing criteria search """

        m = MatchList(self.g.individual_list())

        criteria = "surname=McIntyre:birthrange=1820-1840:deathrange=1865-1870"
        result = m.criteria_match(criteria)
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0].name(), ('Calvin Colin', 'McIntyre'))

        criteria = "surname=McIntyre:birth=1890:death=1953"
        result = m.criteria_match(criteria)
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0].name(), ('Ernest R', 'McIntyre'))

        criteria = "surname=McIntyre:marriage=1821"
        result = m.criteria_match(criteria)
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0].name(), ('John M', 'McIntyre'))

        criteria = "surname=McIntyre:marriagerange=1820-1825"
        result = m.criteria_match(criteria)
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0].name(), ('John M', 'McIntyre'))


if __name__ == '__main__':
    unittest.main()
