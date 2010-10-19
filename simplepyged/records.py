#-*- coding: utf-8 -*-
#
# Gedcom 5.5 Parser
#
# Copyright (C) 2010 Nikola Škorić (nskoric [ at ] gmail.com)
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

# Global imports
import string
from line import Line
from events import Event

class Record(Line):
    """ Gedcom line with level 0 represents a record

    Child class of Line

    """
    
    pass


class Multimedia(Record):
    pass


class Note(Record):
    pass


class Repository(Record):
    pass


class Source(Record):
    pass


class Submitter(Record):
    pass


class Individual(Record):
    """ Gedcom record representing an individual

    Child class of Record

    """

    def __init__(self,level,xref,tag,value,dict):
        Record.__init__(self,level,xref,tag,value,dict)

    def _init(self):
        """ Implementing Line._init() """
        self._parent_family = self.get_parent_family()
        self._families = self.get_families()

        self.birth_events = self._parse_generic_event_list("BIRT")
        self.death_events = self._parse_generic_event_list("DEAT")

    def _parse_generic_event_list(self, tag):
        """ Creates new event for each line with given tag"""
        retval = []
        for event_line in self.children_tags(tag):
            retval.append(Event(event_line))

        return retval
        
    def sex(self):
        """ Returns 'M' for males, 'F' for females """
        return self.children_tags("SEX")[0].value()

    def parent_family(self):
        return self._parent_family

    def families(self):
        return self._families

    def father(self):
        if self.parent_family() != None:
            if self.parent_family().husband() != None:
                return self.parent_family().husband()

    def mother(self):
        if self.parent_family() != None:
            if self.parent_family().wife() != None:
                return self.parent_family().wife()

    def children(self):
        retval = []

        for f in self.families():
            for c in f.children():
                retval.append(c)

        return retval

    def get_families(self):
        """ Return a list of all of the family records of a person. """
        return self.children_tag_records("FAMS")

    def get_parent_family(self):
        """ Return a family record in which this individual is a child. """
        famc = self.children_tag_records("FAMC")
        
        if len(famc) > 1:
            raise Exception('Individual has multiple parent families.')

        if len(famc) == 0:
            return None
        
        return famc[0]
    
    def name(self):
        """ Return a person's names as a tuple: (first,last) """
        first = ""
        last = ""
        for e in self.children_lines():
            if e.tag() == "NAME":
                # some older Gedcom files don't use child tags but instead
                # place the name in the value of the NAME tag
                if e.value() != "":
                    name = string.split(e.value(),'/')
                    first = string.strip(name[0])
                    last = string.strip(name[1])
                else:
                    for c in e.children_lines():
                        if c.tag() == "GIVN":
                            first = c.value()
                        if c.tag() == "SURN":
                            last = c.value()
        return (first,last)

    def given_name(self):
        """ Return person's given name """
        try:
            return self.name()[0]
        except IndexError:
            return None

    def surname(self):
        """ Return person's surname """
        try:
            return self.name()[1]
        except IndexError:
            return None

    def fathers_name(self):
        """ Return father's name (patronymic) """
        return self.father().given_name()
        
    def birth(self):
        """ Return one randomly chosen birth event

        If a person has only one birth event (which is most common
        case), return that one birth event. For list of all birth
        events see self.birth_events.
        """

        if len(self.birth_events) == 0:
            return None

        return self.birth_events[0]

    def birth_year(self):
        """ Return the birth year of a person in integer format """

        if self.birth() == None:
            return -1

        if self.birth().date == None:
            return -1

        try:
            date = int(string.split(self.birth().date)[-1])
            return date
        except ValueError:
            return -1

    def alive(self):
        """ Return True if individual lacks death entry """
        return self.death() is None

    def death(self):
        """ Return one randomly chosen death event

        If a person has only one death event (which is most common
        case), return that one death event. For list of all death
        events see self.death_events.
        """

        if len(self.death_events) == 0:
            return None

        return self.death_events[0]

    def death_year(self):
        """ Return the death year of a person in integer format """

        if self.death() == None:
            return -1

        if self.death().date == None:
            return -1

        try:
            date = int(string.split(self.death().date)[-1])
            return date
        except ValueError:
            return -1

    def deceased(self):
        """ Check if a person is deceased """
        return not self.alive()

    def marriages(self):
        """ Return a list of marriage tuples for a person, each listing
        (date,place).
        """
        retval = []

        for f in self.families():
            if f.married():
                retval.append(f.marriage())

        return retval

    def marriage_years(self):
        """ Return a list of marriage years for a person, each in integer
        format.
        """

        return map(lambda x: int(x[0].split(" ")[-1]), self.marriages())


class Family(Record):
    """ Gedcom record representing a family

    Child class of Record

    """

    def __init__(self,level,xref,tag,value,dict):
        Record.__init__(self,level,xref,tag,value,dict)

    def _init(self):
        """ Implementing Line._init()

        Initialise husband, wife and children attributes. """
        
        try:
            self._husband = self.children_tag_records("HUSB")[0]
        except IndexError:
            self._husband = None

        try:
            self._wife = self.children_tag_records("WIFE")[0]
        except IndexError:
            self._wife = None

        try:
            self._children = self.children_tag_records("CHIL")
        except IndexError:
            self._children = []

    def husband(self):
        """ Return husband this family """
        return self._husband

    def wife(self):
        """ Return wife this family """
        return self._wife

    def parents(self):
        """ Return list of parents in this family """
        return [self._husband, self._wife]

    def children(self):
        """ Return list of children in this family """
        return self._children

    def married(self):
        """ Return True if parents were married """
        return len(self.children_tags("MARR")) > 0

    def marriage(self):
        """ Return (date, place) tuple of (first) marriage of family parents. """

        for marr in self.children_tags("MARR"):
            try:
               date = marr.children_tags("DATE")[0].value()
            except:
                date = ''
            try:
                place = marr.children_tags("PLAC")[0].value()
            except:
                place = ''

            return (date, place)
        return ('', '')
