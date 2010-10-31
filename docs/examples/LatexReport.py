#this code is used from latex.py
from mako.template import Template
import os
import locale

class Stack:
    def __init__(self, stack = []):
        self.stack = stack
        self.sort = self.stack.sort

    def __contains__(self, item):
        return item in self.stack

    def push(self, item):
        if item == None:
            return

        if item in self.stack:
            return

        self.stack.append(item)

    def empty(self):
        return self.stack == []

    def __iter__(self):
        return self.stack.__iter__()

    def next(self):
        return self.stack.next()

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

    def construct_stack(self, stack, depth):
        """ Construct a stack full of depth distant relatives of members of stack (a recursion, obviously) """
        
        if depth == 0:
            return []
        if stack.empty():
            return stack

        for family in stack:
            if family == None:
                continue
            addendum = Stack()
            for p in family.parents():
                addendum.push(p.parent_family())
            for c in family.children():
                for f in c.families():
                    addendum.push(f)

        expanded_family = construct_stack(addendum, depth - 1)

        for e in expanded_family:
            stack.push(e)

        return stack

    def latex_index(self, stack):
        """ Create an index of all individuals printed in report """
        
        individuals = Stack()
        for family in stack:
            for p in family.parents():
                individuals.push(p)
            for c in family.children():
                individuals.push(c)

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

    def get_latex(self, stack = None):
        """ Print out latex code using mako template engine """
        
        if stack is None:
            stack = Stack(self.gedcom.family_list())

        latex = Template(
            filename = self.template,
            default_filters=['unicode', 'escape_latex'],
            imports=['from LatexReport import escape_latex']) # so that mako.template.Template can find escape_latex
        source = latex.render_unicode(
            stack=stack.stack,
            index=self.latex_index(stack.stack),
            pages=self.pages,
            ).encode('utf-8')

        return source

escape_latex = LatexReport.escape_latex # so that mako.template.Template can find escape_latex
