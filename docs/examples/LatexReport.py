#this code is used from latex.py
import locale
import os
from mako.template import Template


def push(stack, item):
    if item == None:
        return stack

    if item in stack:
        return stack

    stack.append(item)
    
    return stack

class LatexReport:
    def __init__(self, gedcom):
        self.template = 'template.tex'
        self.gedcom = gedcom

    @staticmethod
    def name(person):
        """ Format person's name as you wish """
        
        if person is None:
            return ""

        if person.surname() is None:
            s = ''
        else:
            s = person.surname()

        if person.given_name() is None:
            g = ''
        else:
            g = person.given_name()
        return s + ", " + g

    @staticmethod
    def escape_latex(in_str):
        """ Escaping LaTeX special characters """
        
        map = {'#': '\\#', 
            '$': '\\$', 
            '%': '\\%', 
            '^': '\\textasciicircum{}', 
            '&': '\\&', 
            '_': '\\_', 
            '{': '\\{', 
            '}': '\\}', 
            '~': '\\~{}', 
            '\\': '\\textbackslash{}'}

        in_str = unicode(in_str)

        retval = ''
        for c in in_str:
            if c in map.keys():
                c = map[c]
            retval += c

        return retval

    def construct_stack(self, stack, depth = None):
        """ Construct a stack full of depth distant relatives of members of stack (a recursion, obviously) """
        
        if depth == 0:
            return []
        if not stack: # empty stack
            return stack

        for family in stack:
            if family == None:
                continue
            addendum = []
            for p in family.parents():
                addendum = push(addendum, p.parent_family())
            for c in family.children():
                for f in c.families():
                    addendum = push(addendum, f)

        if depth is None:
            expanded_family = construct_stack(addendum)
        else:
            expanded_family = construct_stack(addendum, depth - 1)

        for e in expanded_family:
            stack = push(stack, e)

        return stack

    def latex_index(self, stack):
        """ Create an index of all individuals printed in report """
        
        individuals = []
        for family in stack:
            for p in family.parents():
                individuals = push(individuals, p)
            for c in family.children():
                individuals = push(individuals, c)

        locale.setlocale(locale.LC_ALL, '')
        individuals.sort(cmp=lambda x, y: locale.strcoll(self.name(x), self.name(y)))

        return individuals

    def pages(self, individual):
        """ Return list of xrefs of families in which a person can be found """
        
        pages = []
        if individual.parent_family() is not None:
            return [individual.parent_family().xref()] # Person's parent's family is preferable link to person
        for f in individual.families(): # If person doesn't have parent family, then index his child families
            if f is not None:
                pages.append(f.xref())

        return pages

    @staticmethod
    def arrow(in_str):
        """ Format an arrow """
        d = ''
        if in_str == 'parent':
            d = '\\leftarrow'
        elif in_str == 'child':
            d = '\\rightarrow'
        elif in_str == 'sibling':
            d = '\\Leftrightarrow'
        if d != '':
            return unicode('$' + d + '$')
        else:
            return unicode('')


    def get_home_person_latex(self, stack = None):
        """ Print out latex code for home_person relatives """
        
        if stack is None:
            stack = self.gedcom.family_list()

        filtered = []

        for family in stack:
            if family.is_relative(self.home_person):
                filtered = push(filtered, family)

        return self.get_latex(filtered)
            

    def get_latex(self, stack = None):
        """ Print out latex code using mako template engine """
        
        if stack is None:
            stack = self.gedcom.family_list()

        locale.setlocale(locale.LC_ALL, '')
        stack.sort(cmp=lambda x, y:
                locale.strcoll(
                  self.name(x.husband()) + self.name(x.wife()),
                  self.name(y.husband()) + self.name(y.wife())))

        latex = Template(
            filename = self.template,
            default_filters=['unicode', 'escape_latex', 'empty_none'],
            imports=['from LatexReport import escape_latex, empty_none']) # so that mako.template.Template can find escape_latex
        source = latex.render_unicode(
            home_person = self.home_person,
            stack=stack,
            index=self.latex_index(stack),
            pages=self.pages,
            name=self.name,
            fmt_arrow=self.arrow,
            ).encode('utf-8')

        return source

escape_latex = LatexReport.escape_latex # so that mako.template.Template can find escape_latex
def empty_none(in_str):
    if in_str == 'None':
        return ''

    return in_str
