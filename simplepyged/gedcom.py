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

# __all__ = ["Gedcom", "Line", "GedcomParseError"]

# Global imports
import string
from records import *

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
        self._record_dict = {}
        self._line_list = []
        self._individual_list = []
        self._family_list = []
        self._line_top = Line(-1,"","TOP","",self._record_dict)
        self._current_level = -1
        self._current_line = self._line_top
        self._individuals = 0
        self._parse(file)

    def record_dict(self):
        """ Return a dictionary of records from the Gedcom file.  Only
        records that have xref defined are listed in the dictionary.
        The key for the dictionary is the xref.
        """
        return self._record_dict

    def line_list(self):
        """ Return a list of all the lines in the Gedcom file.  The
        lines are in the same order as they appeared in the file.
        """
        return self._line_list

    def individual_list(self):
        """ Return a list of all the individuals in the Gedcom file.  The
        individuals are in the same order as they appeared in the file.
        """
        return self._individual_list

    def family_list(self):
        """ Return a list of all the families in the Gedcom file.  The
        families are in the same order as they appeared in the file.
        """
        return self._family_list

    def get_record(self, xref):
        """ Return an object of class Record (or it's subclass) identified by xref """
        return self.record_dict()[xref]

    def get_individual(self, xref):
        """ Return an object of class Individual identified by xref """
        record = self.get_record(xref)
        if record.type() == 'Individual':
            return record
        else:
            return None

    def get_family(self, xref):
        """ Return an object of class Family identified by xref """
        record = self.get_record(xref)
        if record.type() == 'Family':
            return record
        else:
            return None

    # Private methods

    def _parse(self,file):
        # open file
        # go through the lines
        f = open(file)
        number = 1
        for line in f.readlines():
            self._parse_line(number,line.decode("utf-8-sig"))
            number += 1

        for e in self.line_list():
            e._init()

    def _parse_line(self,number,line):
        # each line should have: Level SP (Xref SP)? Tag (SP Value)? (SP)? NL
        # parse the line
        tail = line.strip()

        if tail == '':
            self._error(number,"Empty line")

        try:
            [head, tail] = tail.split(' ', 1)
        except ValueError:
            self._error(number,"Incomplete line")

        l = self._level(number,head) #retireve line level

        try:
            [head, tail] = tail.split(' ', 1)
        except ValueError:
            [head, tail] = [tail, '']
        p = self._xref(number,head) #retrieve line xref if it exists
        if p != '':
            try:
                [head, tail] = tail.split(' ', 1)
            except ValueError:
                [head, tail] = [tail, '']
        t = self._tag(number,head) #retrieve line tag

        v = tail #retrieve value of tag if it exists
        
        # create the line
        if l > self._current_level + 1:
            self._error(number,"Structure of GEDCOM file is corrupted")

        if l == 0: #current line is in fact a brand new record
            if t == "INDI":
                e = Individual(l,p,t,v,self.record_dict())
                self._individual_list.append(e)
            elif t == "FAM":
                e = Family(l,p,t,v,self.record_dict())
                self._family_list.append(e)
            elif t == "OBJE":
                e = Multimedia(l,p,t,v,self.record_dict())
            elif t == "NOTE":
                e = Note(l,p,t,v,self.record_dict())
            elif t == "REPO":
                e = Repository(l,p,t,v,self.record_dict())
            elif t == "SOUR":
                e = Source(l,p,t,v,self.record_dict())
            elif t == "SUBN":
                e = Submission(l,p,t,v,self.record_dict())
            elif t == "SUBM":
                e = Submitter(l,p,t,v,self.record_dict())
            else:
                e = Record(l,p,t,v,self.record_dict())
        else:
            e = Line(l,p,t,v,self.record_dict())

        self._line_list.append(e)
        if p != '':
            self._record_dict[p] = e

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

    def _level(self,number,head):
        try:
            l = int(head)
        except ValueError:
            self._error(number,"Line must start with an integer level")

        if (l < 0):
            self._error(number,"Line must start with a positive integer")

        return l

    def _xref(self,number,head):
        if head == '':
            self._error(number,"Incomplete Line")
        p = ''
        if head[0] == '@':
            if head[len(head)-1] == '@':
                p = head
                # could strip the xref to remove the @ with
                # string.strip(head,'@')
                # but it may be useful to identify xrefs outside this class
            else:
                self._error(number,"Xref must start and end with @")
        return p

    def _tag(self,number,head):
        if head == '':
            self._error(number,"Incomplete Line")
        return head

    def _error(self,number,text):
        error = "Gedcom format error on line " + unicode(number) + ': ' + text
        raise GedcomParseError(error)

    def _print(self):
        for e in self.line_list:
            print string.join([unicode(e.level()),e.xref(),e.tag(),e.value()])


class GedcomParseError(Exception):
    """ Exception raised when a Gedcom parsing error occurs
    """
    
    def __init__(self, value):
        self.value = value
        
    def __str__(self):
        return self.value

