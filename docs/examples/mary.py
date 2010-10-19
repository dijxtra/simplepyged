import os
from simplepyged.gedcom import *

g = Gedcom(os.path.abspath('../../test/mcintyre.ged'))
mary = g.get_individual('@P405366386@')

print mary.name()

#parents
print mary.father().name()
print mary.parent_family().husband().name()

#husband
print map(lambda x: x.husband().name(), mary.families())

#children
print map(lambda x: x.name(), mary.children())
