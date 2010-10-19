import os
from simplepyged.gedcom import *
from simplepyged.matches import *

g = Gedcom(os.path.abspath('../../test/mcintyre.ged'))

m = MatchList(g.individual_list())

mcintyres = m.surname_match('McIntyre')

for century in [18, 19, 20]:
    (start, end) = ((century - 1) * 100 + 1, century * 100)

    results = MatchList(mcintyres).birth_range_match(start, end)

    results.sort(key=lambda x: x.birth_year())

    print 'McIntyres born in ' + str(century) + 'th century:'
    for individual in results:
        print str(individual.birth_year()) + ': ' + individual.given_name()

    print

    
