from simplepyged.gedcom import *
from LatexReport import *

#g = Gedcom(os.path.abspath('../../test/mcintyre.ged'))
#g = Gedcom(os.path.abspath('../../test/wright.ged'))
g = Gedcom(os.path.abspath('/home/nick/slova/rodoslovlje/moje.ged'))

l = LatexReport(g)

#l.home_person = g.get_individual('@P405366386@') # mary
#l.home_person = g.get_individual('@I0282@') # me
l.home_person = g.get_individual('@I0282@').mother().father() # deda novosel
#l.home_person = g.get_individual('@I13@') # evica
#l.home_person = g.get_individual('@I34@') # ante

# This is some old code that doesn't work anymore (TODO: rewrite this)
#fam = g.get_family('@F5@')
#stack = [fam]
#stack = construct_stack(stack, 6)

print l.get_home_person_latex()
#print l.get_latex()
