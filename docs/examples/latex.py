from simplepyged.gedcom import *
from LatexReport import *

g = Gedcom(os.path.abspath('../../test/mcintyre.ged'))
#g = Gedcom(os.path.abspath('../../test/wright.ged'))
l = LatexReport(g)

# This is some old code that doesn't work anymore (TODO: rewrite this)
#fam = g.get_family('@F5@')
#stack = [fam]
#stack = construct_stack(stack, 6)

print l.get_latex()
