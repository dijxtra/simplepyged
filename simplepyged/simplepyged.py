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

# __all__ = ["Gedcom", "Line", "GedcomParseError"]

# Global imports
import string

class Gedcom:
    """ Gedcom parser

    This parser is for the Gedcom 5.5 format.  For documentation of
    this format, see

    http://homepages.rootsweb.com/~pmcbride/gedcom/55gctoc.htm

    This parser reads a GEDCOM file and parses it into a set of lines.
    These lines can be accessed via a list (the order of the list is
    the same as the order of the lines in the GEDCOM file), or a
    dictionary (only lines that represent records: the key to the
    dictionary is a unique identifier of each record).

    """

    def __init__(self,file):
        """ Initialize a Gedcom parser. You must supply a Gedcom file.
        """
        self._line_list = []
        self._line_dict = {}
        self._individual_list = []
        self._individual_dict = {}
        self._family_list = []
        self._family_dict = {}
        self._line_top = Line(-1,"","TOP","",self._line_dict)
        self._current_level = -1
        self._current_line = self._line_top
        self._individuals = 0
        self._parse(file)

    def line_list(self):
        """ Return a list of all the lines in the Gedcom file.  The
        lines are in the same order as they appeared in the file.
        """
        return self._line_list

    def line_dict(self):
        """ Return a dictionary of records from the Gedcom file.  Only
        records that have xref defined are listed in the dictionary.
        The key for the dictionary is the xref.
        """
        return self._line_dict

    def individual_list(self):
        """ Return a list of all the individuals in the Gedcom file.  The
        individuals are in the same order as they appeared in the file.
        """
        return self._individual_list

    def individual_dict(self):
        """ Return a dictionary of individuals from the Gedcom file.  The
        key for the dictionary is individual's xref.
        """
        return self._individual_dict

    def family_list(self):
        """ Return a list of all the families in the Gedcom file.  The
        families are in the same order as they appeared in the file.
        """
        return self._family_list

    def family_dict(self):
        """ Return a dictionary of families from the Gedcom file.  The
        key for the dictionary is family's xref.
        """
        return self._family_dict

    def get_individual(self, xref):
        """ Return an object of class Individual identified by xref """
        return self.individual_dict()[xref]

    def get_family(self, xref):
        """ Return an object of class Family identified by xref """
        return self.family_dict()[xref]

    # Private methods

    def _parse(self,file):
        # open file
        # go through the lines
        f = open(file)
        number = 1
        for line in f.readlines():
            self._parse_line(number,line)
            number += 1

        for e in self.line_list():
            e._init()

    def _parse_line(self,number,line):
        # each line should have: Level SP (Xref SP)? Tag (SP Value)? (SP)? NL
        # parse the line
        parts = string.split(line)
        place = 0
        l = self._level(number,parts,place) #retireve line level
        place += 1
        p = self._xref(number,parts,place) #retrieve line xref if it exists
        if p != '':
            place += 1
        t = self._tag(number,parts,place) #retrieve line tag
        place += 1
        v = self._value(number,parts,place) #retrieve value of tag if it exists

        # create the line
        if l > self._current_level + 1:
            self._error(number,"Structure of GEDCOM file is corrupted")

        if l == 0: #current line is in fact a brand new record
            if t == "INDI":
                e = Individual(l,p,t,v,self.line_dict())
                self._individual_list.append(e)
                if p != '':
                    self._individual_dict[p] = e
            elif t == "FAM":
                e = Family(l,p,t,v,self.line_dict())
                self._family_list.append(e)
                if p != '':
                    self._family_dict[p] = e
            elif t == "OBJE":
                e = Multimedia(l,p,t,v,self.line_dict())
            elif t == "NOTE":
                e = Note(l,p,t,v,self.line_dict())
            elif t == "REPO":
                e = Repository(l,p,t,v,self.line_dict())
            elif t == "SOUR":
                e = Source(l,p,t,v,self.line_dict())
            elif t == "SUBN":
                e = Submission(l,p,t,v,self.line_dict())
            elif t == "SUBM":
                e = Submitter(l,p,t,v,self.line_dict())
            else:
                e = Record(l,p,t,v,self.line_dict())
        else:
            e = Line(l,p,t,v,self.line_dict())

        self._line_list.append(e)
        if p != '':
            self._line_dict[p] = e

        if l > self._current_level:
            self._current_line.add_child(e)
            e.add_parent_line(self._current_line)
        else:
            # l.value <= self._current_level:
            while (self._current_line.level() != l - 1):
                self._current_line = self._current_line.parent_line()
            self._current_line.add_child(e)
            e.add_parent_line(self._current_line)

        # finish up
        self._current_level = l
        self._current_line = e

    def _level(self,number,parts,place):
        if len(parts) <= place:
            self._error(number,"Empty line")
        try:
            l = int(parts[place])
        except ValueError:
            self._error(number,"Line must start with an integer level")

        if (l < 0):
            self._error(number,"Line must start with a positive integer")

        return l

    def _xref(self,number,parts,place):
        if len(parts) <= place:
            self._error(number,"Incomplete Line")
        p = ''
        part = parts[1]
        if part[0] == '@':
            if part[len(part)-1] == '@':
                p = part
                # could strip the xref to remove the @ with
                # string.strip(part,'@')
                # but it may be useful to identify xrefs outside this class
            else:
                self._error(number,"Xref must start and end with @")
        return p

    def _tag(self,number,parts,place):
        if len(parts) <= place:
            self._error(number,"Incomplete line")
        return parts[place]

    def _value(self,number,parts,place):
        if len(parts) <= place:
            return ''
#        p = self._xref(number,parts,place)
#        if p != '':
#            # rest of the line should be empty
#            if len(parts) > place + 1:
#                self._error(number,"Too many parts of line")
#            return p
#        else:
        # rest of the line should be ours
        vlist = []
        while place < len(parts):
            vlist.append(parts[place])
            place += 1
        v = string.join(vlist)
        return v
            
    def _error(self,number,text):
        error = "Gedcom format error on line " + str(number) + ': ' + text
        raise GedcomParseError(error)

    def _print(self):
        for e in self.line_list:
            print string.join([str(e.level()),e.xref(),e.tag(),e.value()])


class GedcomParseError(Exception):
    """ Exception raised when a Gedcom parsing error occurs
    """
    
    def __init__(self, value):
        self.value = value
        
    def __str__(self):
        return self.value

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
        result = str(self)
        for e in self.children_lines():
            result += '\n' + e.gedcom()
        return result

    def __str__(self):
        """ Format this line as its original string """
        result = str(self.level())
        if self.xref() != "":
            result += ' ' + self.xref()
        result += ' ' + self.tag()
        if self.value() != "":
            result += ' ' + self.value()
        return result

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
        """ Return the birth tuple of a person as (date,place) """
        date = ""
        place = ""

        for e in self.children_lines():
            if e.tag() == "BIRT":
                for c in e.children_lines():
                    if c.tag() == "DATE":
                        date = c.value()
                    if c.tag() == "PLAC":
                        place = c.value()
        return (date,place)

    def birth_year(self):
        """ Return the birth year of a person in integer format """
        date = ""
        for e in self.children_lines():
            if e.tag() == "BIRT":
                for c in e.children_lines():
                    if c.tag() == "DATE":
                        datel = string.split(c.value())
                        date = datel[len(datel)-1]
        if date == "":
            return -1
        try:
            return int(date)
        except ValueError:
            return -1

    def alive(self):
        """ Return True if individual lacks death entry """
        return self.death() == ('', '')

    def death(self):
        """ Return the death tuple of a person as (date,place) """
        for deat in self.children_tags("DEAT"):
            try:
               date = deat.children_tags("DATE")[0].value()
            except:
                date = ''
            try:
                place = deat.children_tags("PLAC")[0].value()
            except:
                place = ''
            return (date, place)
        return ('', '')

    def death_year(self):
        """ Return the death year of a person in integer format """
        date = ""
        for e in self.children_lines():
            if e.tag() == "DEAT":
                for c in e.children_lines():
                    if c.tag() == "DATE":
                        datel = string.split(c.value())
                        date = datel[len(datel)-1]
        if date == "":
            return -1
        try:
            return int(date)
        except ValueError:
            return -1

    def deceased(self):
        """ Check if a person is deceased """
        for e in self.children_lines():
            if e.tag() == "DEAT":
                return True
        return False

    def criteria_match(self,criteria):
        """ Check in this individual matches all of the given criteria.

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
        except ValueError:
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
                except ValueError:
                    match = False
            elif key == "birthrange":
                try:
                    year1,year2 = value.split('-')
                    year1 = int(year1)
                    year2 = int(year2)
                    if not self.birth_range_match(year1,year2):
                        match = False
                except ValueError:
                    match = False
            elif key == "death":
                try:
                    year = int(value)
                    if not self.death_year_match(year):
                        match = False
                except ValueError:
                    match = False
            elif key == "deathrange":
                try:
                    year1,year2 = value.split('-')
                    year1 = int(year1)
                    year2 = int(year2)
                    if not self.death_range_match(year1,year2):
                        match = False
                except ValueError:
                    match = False
            elif key == "marriage":
                try:
                    year = int(value)
                    if not self.marriage_year_match(year):
                        match = False
                except ValueError:
                    match = False
            elif key == "marriagerange":
                try:
                    year1,year2 = value.split('-')
                    year1 = int(year1)
                    year2 = int(year2)
                    if not self.marriage_range_match(year1,year2):
                        match = False
                except ValueError:
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

        return map(lambda x: x[0].split(" ")[-1], self.marriages())

    

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
