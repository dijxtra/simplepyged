#-*- coding: utf-8 -*-
#
# Gedcom 5.5 Parser
#
# Copyright (C) 2010 Nikola Škorić (nskoric [ at ] gmail.com)
# Copyright (C) 2005 Daniel Zappala (zappala [ at ] cs.byu.edu)
# Copyright (C) 2005 Brigham Young University
#
# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
# 
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA  02111-1307, USA.
#
# Please see the GPL license at http://www.gnu.org/licenses/gpl.txt
#
# To contact the author, see http://github.com/dijxtra/simplepyged

class Line:
    """ Line of a GEDCOM file

    Each line in a Gedcom file has following format:

    level [xref] tag [value]

    where level and tag are required, and xref and value are optional.
    Lines are arranged hierarchically according to their level, and
    lines with a level of zero (called 'records') are at the top
    level.  Lines with a level greater than zero are children of their
    parent.

    A xref has the format @pname@, where pname is any sequence of
    characters and numbers.  The xref identifies the record being
    referenced to, so that any xref included as the value of any line
    points back to the original record.  For example, an line may have
    a FAMS tag whose value is @F1@, meaning that this line points to
    the family record in which the associated individual is a spouse.
    Likewise, an line with a tag of FAMC has a value that points to a
    family record in which the associated individual is a child.
    
    See a Gedcom file for examples of tags and their values.

    """

    def __init__(self,level,xref,tag,value,dict):
        """ Initialize a line.  You must include a level, xref,
        tag, value, and global line dictionary.  Normally initialized
        by the Gedcom parser, not by a user.
        """
        # basic line info
        self._level = level
        self._xref = xref
        self._tag = tag
        self._value = value
        self._dict = dict
        # structuring
        self._children_lines = []
        self._parent_line = None

    def _init(self):
        """ A method to which GEDCOM parser runs after all lines are available. Subclasses should implement this method if they want to work with other Lines at parse time, but after all Lines are parsed. """
        pass

    def type(self):
        """ Return class name of this instance

        Useful for determining if this line is Individual, Family, Note or some other record.
        """
        return self.__class__.__name__

    def level(self):
        """ Return the level of this line """
        return self._level

    def xref(self):
        """ Return the xref of this line """
        return self._xref
    
    def tag(self):
        """ Return the tag of this line """
        return self._tag

    def value(self):
        """ Return the value of this line """
        return self._value

    def children_lines(self):
        """ Return the child lines of this line """
        return self._children_lines

    def parent_line(self):
        """ Return the parent line of this line """
        return self._parent_line

    def add_child(self,line):
        """ Add a child line to this line """
        self.children_lines().append(line)
        
    def add_parent_line(self,line):
        """ Add a parent line to this line """
        self._parent_line = line

    def children_tags(self, tag):
        """ Returns list of child lines whos tag matches the argument. """
        lines = []
        for c in self.children_lines():
            if c.tag() == tag:
                lines.append(c)

        return lines

    def children_tag_records(self, tag):
        """ Returns list of records which are pointed by child lines with given tag. """
        lines = []
        for e in self.children_tags(tag):
            try:
                lines.append(self._dict[e.value()])
            except KeyError:
                pass

        return lines

    def gedcom(self):
        """ Return GEDCOM code for this line and all of its sub-lines """
        result = unicode(self)
        for e in self.children_lines():
            result += '\n' + e.gedcom()
        return result

    def __str__(self):
        """ Format this line as its original string """
        result = unicode(self.level())
        if self.xref() != "":
            result += ' ' + self.xref()
        result += ' ' + self.tag()
        if self.value() != "":
            result += ' ' + self.value()
        return result
