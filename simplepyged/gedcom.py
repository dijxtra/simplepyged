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
import yaccer

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
        self._individual_list = []
        self._family_list = []
        self._individuals = 0
        self._header = None
        self._parse(file)

    def record_dict(self):
        """ Return a dictionary of records from the Gedcom file.  Only
        records that have xref defined are listed in the dictionary.
        The key for the dictionary is the xref.
        """
        return self._record_dict

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
        level_0_lines = yaccer.parse(file)
        self._header = level_0_lines[0]

        self._record_dict = {}
        for record in level_0_lines[1:]:
            self._record_dict[record._xref] = record

        for record in self._record_dict.values():
            record._init(self._record_dict)

        self._individual_list = []
        self._family_list = []
        for record in self._record_dict.values():
            if record.type() == "Individual":
                self._individual_list.append(record)
            if record.type() == "Family":
                self._family_list.append(record)
        
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

