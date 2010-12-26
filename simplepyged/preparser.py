#-*- coding: utf-8 -*-
class Preprocessor:
    """Replaces GEDCOM level format with braces. GEDCOM format is
    inposible to parse with lex/yacc, so we have to preprocess it in a
    parsable form.

    Example:
    if GEDCOM file looks like this:
    0 @I0@ INDI
    1 NAME Renée Simone /Wright/
    2 GIVN Renée Simone
    2 SURN Wright
    1 SEX F
    1 BIRT
    2 DATE 21 JAN 1974
    it si replaced with:
    { @I0@ INDI
    { NAME Renée Simone /Wright/
    { GIVN Renée Simone }
    { SURN Wright } }
    { SEX F }
    { BIRT 
    { DATE 21 JAN 1974 } } }
    """
    def __init__(self, filename):
        self.open_brace = None
        self.close_brace = None
        self.filename = filename

        self._init_delimiters()
        
    def _init_delimiters(self):
        """Finds symboly for opening and closing brace which do not
        show up in the file already.

        Searches GEDCOM file for shortest pair of strings
        consisting of only { and } respectively which do not exist in
        the file and sets them as delimiters.

        Examples:
        * if file does not contain string '{' or '}', then delimiters will be '{'
          and '}'
        * if file contains string '}', then delimiters will be '{{'
          and '}}'
        * if file contains string '{{', then delimiters will be '{{{'
          and '}}}'
        * if file contains string '}}}}}', then delimiters will be
          '{{{{{{' and '}}}}}}'
        """
        f = open(self.filename)

        data = f.read()

        self.open_brace = r'{'
        self.close_brace = r'}'

        while (self.open_brace in data) or (self.close_brace in data):
            self.open_brace += r'{'
            self.close_brace += r'}'

        f.close()

        return

    def preprocess_file(self):
        """Preprocesses the GEDCOM file. See parent class docstring for details."""
        f = open(self.filename)

        retval = ''
        current_level = -1
        for line in f.readlines():
            parts = line.split(' ')
            level = int(parts[0])
            delim = ''

            if level == current_level:
                delim = ' ' + self.close_brace
            elif level == current_level + 1:
                pass
                current_level += 1
            elif level < current_level:
                delim = ''
                while level < current_level:
                    delim += ' ' + self.close_brace
                    current_level -= 1
                delim += ' ' + self.close_brace
            else:
                raise Exception('Faulted level nesting.')

            retval += delim + ' ' + self.open_brace + ' ' + line.rstrip() + '\n'

        retval += ' ' + self.close_brace

        return retval
    
if __name__ == "__main__":
    print Preprocessor('../test/wright.ged').preprocess_file()
