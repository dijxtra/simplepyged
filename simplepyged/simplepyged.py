#
# Gedcom 5.5 Parser
#
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
# To contact the author, see http://faculty.cs.byu.edu/~zappala

__all__ = ["Gedcom", "Element", "GedcomParseError"]

# Global imports
import string

class Gedcom:
    """ Gedcom parser

    This parser is for the Gedcom 5.5 format.  For documentation of
    this format, see

    http://homepages.rootsweb.com/~pmcbride/gedcom/55gctoc.htm

    This parser reads a GEDCOM file and parses it into a set of
    elements.  These elements can be accessed via a list (the order of
    the list is the same as the order of the elements in the GEDCOM
    file), or a dictionary (the key to the dictionary is a unique
    identifier that one element can use to point to another element).

    """

    def __init__(self,file):
        """ Initialize a Gedcom parser. You must supply a Gedcom file.
        """
        self.__element_list = []
        self.__element_dict = {}
        self.__individual_list = []
        self.__individual_dict = {}
        self.__family_list = []
        self.__family_dict = {}
        self.__element_top = Element(-1,"","TOP","",self.__element_dict)
        self.__current_level = -1
        self.__current_element = self.__element_top
        self.__individuals = 0
        self.__parse(file)

    def element_list(self):
        """ Return a list of all the elements in the Gedcom file.  The
        elements are in the same order as they appeared in the file.
        """
        return self.__element_list

    def element_dict(self):
        """ Return a dictionary of elements from the Gedcom file.  Only
        elements identified by a pointer are listed in the dictionary.  The
        key for the dictionary is the pointer.
        """
        return self.__element_dict

    def individual_list(self):
        """ Return a list of all the individuals in the Gedcom file.  The
        individuals are in the same order as they appeared in the file.
        """
        return self.__individual_list

    def individual_dict(self):
        """ Return a dictionary of individuals from the Gedcom file.  Only
        individuals identified by a pointer are listed in the dictionary.  The
        key for the dictionary is the pointer.
        """
        return self.__individual_dict

    def family_list(self):
        """ Return a list of all the families in the Gedcom file.  The
        families are in the same order as they appeared in the file.
        """
        return self.__family_list

    def family_dict(self):
        """ Return a dictionary of families from the Gedcom file.  Only
        families identified by a pointer are listed in the dictionary.  The
        key for the dictionary is the pointer.
        """
        return self.__family_dict

    def get_individual(self, pointer):
        """ Return an object of class Individual identified by pointer """
        return self.individual_dict()[pointer]

    def get_family(self, pointer):
        """ Return an object of class Family identified by pointer """
        return self.family_dict()[pointer]


    # Private methods

    def __parse(self,file):
        # open file
        # go through the lines
        f = open(file)
        number = 1
        for line in f.readlines():
            self.__parse_line(number,line)
            number += 1
        self.__count()

        for e in self.element_list():
            e._init()

    def __parse_line(self,number,line):
        # each line should have: Level SP (Pointer SP)? Tag (SP Value)? (SP)? NL
        # parse the line
        parts = string.split(line)
        place = 0
        l = self.__level(number,parts,place)
        place += 1
        p = self.__pointer(number,parts,place)
        if p != '':
            place += 1
        t = self.__tag(number,parts,place)
        place += 1
        v = self.__value(number,parts,place)

        # create the element
        if l > self.__current_level + 1:
            self.__error(number,"Structure of GEDCOM file is corrupted")

        if t == "INDI":
            e = Individual(l,p,t,v,self.element_dict())
            self.__individual_list.append(e)
            if p != '':
                self.__individual_dict[p] = e
        elif t == "FAM":
            e = Family(l,p,t,v,self.element_dict())
            self.__family_list.append(e)
            if p != '':
                self.__family_dict[p] = e
        else:
            e = Element(l,p,t,v,self.element_dict())

        self.__element_list.append(e)
        if p != '':
            self.__element_dict[p] = e

        if l > self.__current_level:
            self.__current_element.add_child(e)
            e.add_parent_element(self.__current_element)
        else:
            # l.value <= self.__current_level:
            while (self.__current_element.level() != l - 1):
                self.__current_element = self.__current_element.parent_element()
            self.__current_element.add_child(e)
            e.add_parent_element(self.__current_element)

        # finish up
        self.__current_level = l
        self.__current_element = e

    def __level(self,number,parts,place):
        if len(parts) <= place:
            self.__error(number,"Empty line")
        try:
            l = int(parts[place])
        except ValueError:
            self.__error(number,"Line must start with an integer level")

        if (l < 0):
            self.__error(number,"Line must start with a positive integer")

        return l

    def __pointer(self,number,parts,place):
        if len(parts) <= place:
            self.__error(number,"Incomplete Line")
        p = ''
        part = parts[1]
        if part[0] == '@':
            if part[len(part)-1] == '@':
                p = part
                # could strip the pointer to remove the @ with
                # string.strip(part,'@')
                # but it may be useful to identify pointers outside this class
            else:
                self.__error(number,"Pointer element must start and end with @")
        return p

    def __tag(self,number,parts,place):
        if len(parts) <= place:
            self.__error(number,"Incomplete line")
        return parts[place]

    def __value(self,number,parts,place):
        if len(parts) <= place:
            return ''
        p = self.__pointer(number,parts,place)
        if p != '':
            # rest of the line should be empty
            if len(parts) > place + 1:
                self.__error(number,"Too many elements")
            return p
        else:
            # rest of the line should be ours
            vlist = []
            while place < len(parts):
                vlist.append(parts[place])
                place += 1
            v = string.join(vlist)
            return v
            
    def __error(self,number,text):
        error = "Gedcom format error on line " + str(number) + ': ' + text
        raise GedcomParseError, error

    def __count(self):
        # Count number of individuals
        self.__individuals = 0
        for e in self.__element_list:
            if e.individual():
                self.__individuals += 1


    def __print(self):
        for e in self.element_list:
            print string.join([str(e.level()),e.pointer(),e.tag(),e.value()])


class GedcomParseError(Exception):
    """ Exception raised when a Gedcom parsing error occurs
    """
    
    def __init__(self, value):
        self.value = value
        
    def __str__(self):
        return `self.value`

class Element:
    """ Gedcom element

    Each line in a Gedcom file is an element with the format

    level [pointer] tag [value]

    where level and tag are required, and pointer and value are
    optional.  Elements are arranged hierarchically according to their
    level, and elements with a level of zero are at the top level.
    Elements with a level greater than zero are children of their
    parent.

    A pointer has the format @pname@, where pname is any sequence of
    characters and numbers.  The pointer identifies the object being
    pointed to, so that any pointer included as the value of any
    element points back to the original object.  For example, an
    element may have a FAMS tag whose value is @F1@, meaning that this
    element points to the family record in which the associated person
    is a spouse.  Likewise, an element with a tag of FAMC has a value
    that points to a family record in which the associated person is a
    child.
    
    See a Gedcom file for examples of tags and their values.

    """

    def __init__(self,level,pointer,tag,value,dict):
        """ Initialize an element.  You must include a level, pointer,
        tag, value, and global element dictionary.  Normally initialized
        by the Gedcom parser, not by a user.
        """
        # basic element info
        self.__level = level
        self.__pointer = pointer
        self.__tag = tag
        self.__value = value
        self.dict = dict #subclasses need to use it, so it is not private
        # structuring
        self.__children_elements = []
        self.__parent_element = None

    def _init(self):
        """ A method to which GEDCOM parser runs after all elements are available. Subclasses should implement this method if they want to work with other Elements at parse time, but after all Elements are parsed. """
        pass

    def level(self):
        """ Return the level of this element """
        return self.__level

    def pointer(self):
        """ Return the pointer of this element """
        return self.__pointer
    
    def tag(self):
        """ Return the tag of this element """
        return self.__tag

    def value(self):
        """ Return the value of this element """
        return self.__value

    def children_elements(self):
        """ Return the child elements of this element """
        return self.__children_elements

    def parent_element(self):
        """ Return the parent element of this element """
        return self.__parent_element

    def add_child(self,element):
        """ Add a child element to this element """
        self.children_elements().append(element)
        
    def add_parent_element(self,element):
        """ Add a parent element to this element """
        self.__parent_element = element

    def children_tag_elements(self, tag):
        """ Returns list of child elements who match the argument. """
        elements = []
        for c in self.children_elements():
            if c.tag() == tag:
                elements.append(c)

        return elements

    def children_tag_values(self, tag):
        """ Returns list of values of child elements who match the argument. """
        values = map(lambda x: x.value(), self.children_tag_elements(tag))

        return values

    def individual(self):
        """ Check if this element is an individual """
        return self.tag() == "INDI"

    # criteria matching

    def get_individual(self):
        """.. deprecated

        This method is obsolete, use Element.gedcom().
        """
        return self.gedcom()

    def gedcom(self):
        """ Return GEDCOM code for this element and all of its sub-elements """
        result = str(self)
        for e in self.children_elements():
            result += '\n' + e.get_individual()
        return result

    def get_family(self):
        result = self.get_individual()
        for e in self.children_elements():
            if e.tag() == "HUSB" or e.tag() == "WIFE" or e.tag() == "CHIL":
                f = self.dict.get(e.value())
                if f != None:
                    result += '\n' + f.get_individual()
        return result

    def __str__(self):
        """ Format this element as its original string """
        result = str(self.level())
        if self.pointer() != "":
            result += ' ' + self.pointer()
        result += ' ' + self.tag()
        if self.value() != "":
            result += ' ' + self.value()
        return result


class Individual(Element):
    """ Gedcom element representing an individual

    Child class of Element

    """

    def __init__(self,level,pointer,tag,value,dict):
        Element.__init__(self,level,pointer,tag,value,dict)

        self._init()

    def _init(self):
        self.__parent_family = None
        self.__families = []

        if self.parent_family_pointer() != None:
            self.__parent_family = self.dict[self.parent_family_pointer()]

        if self.families_pointers() != []:
            for f in self.families_pointers():
                self.__families.append(self.dict[f])
                

    def parent_family(self):
        return self.__parent_family

    def families(self):
        return self.__families

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

    def surname_match(self,name):
        """ Match a string with the surname of an individual """
        (first,last) = self.name()
        return last.find(name) >= 0

    def given_match(self,name):
        """ Match a string with the given names of an individual """
        (first,last) = self.name()
        return first.find(name) >= 0

    def birth_year_match(self,year):
        """ Match the birth year of an individual.  Year is an integer. """
        return self.birth_year() == year

    def birth_range_match(self,year1,year2):
        """ Check if the birth year of an individual is in a given range.
        Years are integers.
        """
        year = self.birth_year()
        if year >= year1 and year <= year2:
            return True
        return False

    def death_year_match(self,year):
        """ Match the death year of an individual.  Year is an integer. """
        return self.death_year() == year

    def death_range_match(self,year1,year2):
        """ Check if the death year of an individual is in a given range.
        Years are integers.
        """
        year = self.death_year()
        if year >= year1 and year <= year2:
            return True
        return False

    def families_pointers(self):
        """ Return a list of pointers of all of the family elements of a person. """
        results = []
        for e in self.children_elements():
            if e.tag() == "FAMS":
                if e.value() != None:
                    results.append(e.value())
#                f = self.dict.get(e.value(),None) #old version (why did this need to go through __dict?)
#                if f != None:
#                    results.append(f)
        return results

    def parent_family_pointer(self):
        """ Return a family element of a person in which the person is a child. """
        results = []
        for e in self.children_elements():
            if e.tag() == "FAMC":
                if e.value() != None:
                    results.append(e.value())
#                f = self.dict.get(e.value(),None) #old version (why did this need to go through __dict?)
#                if f != None:
#                    results.append(f)
        if len(results) > 1:
            raise Exception('Individual has multiple parent families.')

        if len(results) == 0:
            return None
        
        return results[0]

    def name(self):
        """ Return a person's names as a tuple: (first,last) """
        first = ""
        last = ""
        if not self.individual():
            return (first,last)
        for e in self.children_elements():
            if e.tag() == "NAME":
                # some older Gedcom files don't use child tags but instead
                # place the name in the value of the NAME tag
                if e.value() != "":
                    name = string.split(e.value(),'/')
                    first = string.strip(name[0])
                    last = string.strip(name[1])
                else:
                    for c in e.children_elements():
                        if c.tag() == "GIVN":
                            first = c.value()
                        if c.tag() == "SURN":
                            last = c.value()
        return (first,last)

    def given_name(self):
        """ Return person's given name """
        try:
            return self.name()[0]
        except:
            return None

    def surname(self):
        """ Return person's surname """
        try:
            return self.name()[1]
        except:
            return None

    def fathers_name(self):
        """ Return father's name (patronymic) """
        return self.father().given_name()
        
    def birth(self):
        """ Return the birth tuple of a person as (date,place) """
        date = ""
        place = ""
        if not self.individual():
            return (date,place)
        for e in self.children_elements():
            if e.tag() == "BIRT":
                for c in e.children_elements():
                    if c.tag() == "DATE":
                        date = c.value()
                    if c.tag() == "PLAC":
                        place = c.value()
        return (date,place)

    def birth_year(self):
        """ Return the birth year of a person in integer format """
        date = ""
        if not self.individual():
            return date
        for e in self.children_elements():
            if e.tag() == "BIRT":
                for c in e.children_elements():
                    if c.tag() == "DATE":
                        datel = string.split(c.value())
                        date = datel[len(datel)-1]
        if date == "":
            return -1
        try:
            return int(date)
        except:
            return -1

    def death(self):
        """ Return the death tuple of a person as (date,place) """
        date = ""
        place = ""
        if not self.individual():
            return (date,place)
        for e in self.children_elements():
            if e.tag() == "DEAT":
                for c in e.children_elements():
                    if c.tag() == "DATE":
                        date = c.value()
                    if c.tag() == "PLAC":
                        place = c.value()
        return (date,place)

    def death_year(self):
        """ Return the death year of a person in integer format """
        date = ""
        if not self.individual():
            return date
        for e in self.children_elements():
            if e.tag() == "DEAT":
                for c in e.children_elements():
                    if c.tag() == "DATE":
                        datel = string.split(c.value())
                        date = datel[len(datel)-1]
        if date == "":
            return -1
        try:
            return int(date)
        except:
            return -1

    def deceased(self):
        """ Check if a person is deceased """
        if not self.individual():
            return False
        for e in self.children_elements():
            if e.tag() == "DEAT":
                return True
        return False

    def criteria_match(self,criteria):
        """ Check in this element matches all of the given criteria.

        The criteria is a colon-separated list, where each item in the list has the form [name]=[value]. The following criteria are supported:

        * surname=[name] - Match a person with [name] in any part of the surname.
        * name=[name] - Match a person with [name] in any part of the given name.
        * birth=[year] - Match a person whose birth year is a four-digit [year].
        * birthrange=[year1-year2] - Match a person whose birth year is in the range of years from [year1] to [year2], including both [year1] and [year2].
        * death=[year]
        * deathrange=[year1-year2]
        * marriage=[year]
        * marriagerange=[year1-year2]
        
        """

        # error checking on the criteria
        try:
            for crit in criteria.split(':'):
                key,value = crit.split('=')
        except:
            return False
        match = True
        for crit in criteria.split(':'):
            key,value = crit.split('=')
            if key == "surname" and not self.surname_match(value):
                match = False
            elif key == "name" and not self.given_match(value):
                match = False
            elif key == "birth":
                try:
                    year = int(value)
                    if not self.birth_year_match(year):
                        match = False
                except:
                    match = False
            elif key == "birthrange":
                try:
                    year1,year2 = value.split('-')
                    year1 = int(year1)
                    year2 = int(year2)
                    if not self.birth_range_match(year1,year2):
                        match = False
                except:
                    match = False
            elif key == "death":
                try:
                    year = int(value)
                    if not self.death_year_match(year):
                        match = False
                except:
                    match = False
            elif key == "deathrange":
                try:
                    year1,year2 = value.split('-')
                    year1 = int(year1)
                    year2 = int(year2)
                    if not self.death_range_match(year1,year2):
                        match = False
                except:
                    match = False
            elif key == "marriage":
                try:
                    year = int(value)
                    if not self.marriage_year_match(year):
                        match = False
                except:
                    match = False
            elif key == "marriagerange":
                try:
                    year1,year2 = value.split('-')
                    year1 = int(year1)
                    year2 = int(year2)
                    if not self.marriage_range_match(year1,year2):
                        match = False
                except:
                    match = False
                    
        return match

    def marriage_year_match(self,year):
        """ Check if one of the marriage years of an individual matches
        the supplied year.  Year is an integer. """
        years = self.marriage_years()
        return year in years

    def marriage_range_match(self,year1,year2):
        """ Check if one of the marriage year of an individual is in a
        given range.  Years are integers.
        """
        years = self.marriage_years()
        for year in years:
            if year >= year1 and year <= year2:
                return True
        return False

    def marriage(self):
        """ Return a list of marriage tuples for a person, each listing
        (date,place).
        """
        date = ""
        place = ""
        if not self.individual():
            return (date,place)

        for e in self.children_elements():
            if e.tag() == "FAMS":
                f = self.dict.get(e.value(),None)
                if f == None:
                    return (date,place)
                for g in f.children_elements():
                    if g.tag() == "MARR":
                        for h in g.children_elements():
                            if h.tag() == "DATE":
                                date = h.value()
                            if h.tag() == "PLAC":
                                place = h.value()
        return (date,place)

    def marriage_years(self):
        """ Return a list of marriage years for a person, each in integer
        format.
        """
        dates = []
        if not self.individual():
            return dates
        for e in self.children_elements():
            if e.tag() == "FAMS":
                f = self.dict.get(e.value(),None)
                if f == None:
                    return dates
                for g in f.children_elements():
                    if g.tag() == "MARR":
                        for h in g.children_elements():
                            if h.tag() == "DATE":
                                datel = string.split(h.value())
                                date = datel[len(datel)-1]
                                try:
                                    dates.append(int(date))
                                except:
                                    pass
        return dates


    

class Family(Element):
    """ Gedcom element representing a family

    Child class of Element

    """

    def __init__(self,level,pointer,tag,value,dict):
        Element.__init__(self,level,pointer,tag,value,dict)

    def _init(self):
        self.__husband = None
        self.__wife = None
        self.__children = []
 
        for e in self.children_elements():
            if e.value() != None:
                if e.tag() == "HUSB":
                    self.__husband = self.dict[e.value()]
                elif e.tag() == "WIFE":
                    self.__wife = self.dict[e.value()]
                elif e.tag() == "CHIL":
                    self.__children.append(self.dict[e.value()])

    def husband(self):
        """ Return husband this family """
        return self.__husband

    def wife(self):
        """ Return wife this family """
        return self.__wife

    def parents(self):
        """ Return list of parents in this family """
        return [self.__husband, self.__wife]

    def children(self):
        """ Return list of children in this family """
        return self.__children
