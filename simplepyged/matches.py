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

from records import Individual

class MatchIndividual():
    """ Class for determining whether an Individual matches certain criteria """

    def __init__(self, individual):
        self.individual = individual

    def surname_match(self,name):
        """ Match a string with the surname of an individual """
        (first,last) = self.individual.name()
        return last.find(name) >= 0

    def given_match(self,name):
        """ Match a string with the given names of an individual """
        (first,last) = self.individual.name()
        return first.find(name) >= 0

    def birth_year_match(self,year):
        """ Match the birth year of an individual.  Year is an integer. """
        return self.individual.birth_year() == year

    def birth_range_match(self,year1,year2):
        """ Check if the birth year of an individual is in a given range.
        Years are integers.
        """
        year = self.individual.birth_year()
        if year >= year1 and year <= year2:
            return True
        return False

    def death_year_match(self,year):
        """ Match the death year of an individual.  Year is an integer. """
        return self.individual.death_year() == year

    def death_range_match(self,year1,year2):
        """ Check if the death year of an individual is in a given range.
        Years are integers.
        """
        year = self.individual.death_year()
        if year >= year1 and year <= year2:
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
        years = self.individual.marriage_years()
        return year in years

    def marriage_range_match(self,year1,year2):
        """ Check if one of the marriage year of an individual is in a
        given range.  Years are integers.
        """
        years = self.individual.marriage_years()
        for year in years:
            if year >= year1 and year <= year2:
                return True
        return False


class MatchList:
    """ Class for matching individuals against list of records

    For each boolean method of MatchIndividual class, there is method
    in MatchList with same name which returns list of Individuals in
    the list for which given method returns True.

    Example:
.. code-block:: python

    gedcom = Gedcom(somefile)
    list = gedcom.individual_list()
    individual = gedcom.get_individual(xref)
    
    if MatchIndividual(individual).given_match(some_name):
        individual in MatchList(list).given_match(some_name) # this line returns True
    """

    def __init__(self, record_list):
        self.records = record_list

        methods = [method for method in dir(MatchIndividual) if callable(getattr(MatchIndividual, method)) and not method.startswith('__') ]

        for method in methods:
            setattr(self, method, self.__factory(method))

    def __factory(self, method):
        def product(*args):
            return self.__abstract(method, *args)
        return product
        
    def __abstract(self, method, *args):
        retval = []
        for record in self.records:
            if getattr(MatchIndividual(record), method)(*args):
                retval.append(record)

        return retval


