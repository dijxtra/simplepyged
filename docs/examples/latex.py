import os
from simplepyged import *

g = Gedcom(os.path.abspath('mcintyre.ged'))
fam = g.get_family('@F5@')

def name(person):
    return str(person.surname()) + ", " + str(person.given_name())

def name_link_html(person, prefix=""):
    return "<a href=\"#" + prefix + str(person.pointer()) + "\">" + name(person) + "</a> "

def name_link_latex(person, prefix=""):
    return name(person) + ' (str. \pageref{' + prefix + str(person.pointer()) + '})'

def anchor(person):
    return "[" + str(person.pointer()) + "] "

def anchor_html(person, prefix=""):
    if person == None:
        return "__________"
    return "<a name=\"" + prefix + str(person.pointer()) + "\"></a> "

def anchor_latex(person, prefix=""):
    return '\label{' + prefix + str(person.pointer()) + '}'

def text(family):
    retval = ""
    retval += anchor(family.husband()) + "Husband: " + name(family.husband()) + "\n"
    retval += anchor(family.wife()) + "Wife: " + name(family.wife()) + "\n"
    for c in family.children():
        retval += anchor(c) + "Child: " + name(c) + "\n"
    retval += "\n"
    retval += "\n"

    return retval

def start_html():
    retval = ""
    retval += "<html><head><title>Burek</title></head><body>"
    return retval

def html(family):
    retval = ""
    retval += "\n<hr>\n"
    retval += anchor_html(family.husband(), "up_") + "Husband: " + name_link_html(family.husband(), "down_") + "<br />\n"
    retval += anchor_html(family.wife(), "up_") + "Wife: " + name_link_html(family.wife(), "down_") + "<br />\n"
    for c in family.children():
        retval += anchor_html(c, "down_") + "Child: " + name_link_html(c, "up_") + "<br />\n"

    return retval

def end_html():
    retval = ""
    retval += "<body></html>"
    return retval

def start_latex():
    retval = ''
    retval += '\documentstyle[11pt]{article}\\begin{document}' + "\n"
    return retval

def latex(family):
    retval = ''
    retval += anchor_latex(family.husband(), 'up_') + 'Husband: ' + name_link_latex(family.husband(), 'down_') + "\n\n"
    retval += anchor_latex(family.wife(), 'up_') + 'Wife: ' + name_link_latex(family.wife(), 'down_') + "\n\n"
    for c in family.children():
        retval += anchor_latex(c, 'down_') + 'Child: ' + name_link_latex(c, 'up_') + "\n\n"

    retval += '\\newpage' + "\n\n"
    return retval

def end_latex():
    retval = ''
    retval += '\end{document}'
    return retval

def print_stack(fn, stack):
    retval = ""
    for family in stack:
        retval += fn(family)

    return retval

def push(stack, item):
    if item == None:
        return stack

    if item in stack:
        return stack

    stack.append(item)
    return stack

def construct_stack(stack, depth):
    if depth == 0:
        return []
    if stack == []:
        return []

    for family in stack:
        if family == None:
            continue
        addendum = []
        for p in family.parents():
            addendum = push(addendum, p.parent_family())
        for c in family.children():
            for f in c.families():
                addendum = push(addendum, f)

    expanded_family = construct_stack(addendum, depth - 1)

    for e in expanded_family:
        stack = push(stack, e)

    return stack

stack = [fam]
stack = construct_stack(stack, 6)
print start_latex()
print print_stack(latex, stack)
print end_latex()

