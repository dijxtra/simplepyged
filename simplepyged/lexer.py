#-*- coding: utf-8 -*-
import ply.lex as lex
import re, copy

def set_delimiters(open, close):
    """Sets global variables open_brace and close_brace for use in
    t_WORD method. Must be called before lexer is started."""
    global open_brace, close_brace
    open_brace = open
    close_brace = close

tag_names = [ # GEDCOM tags which parser recognises
    'HEAD',

    'SUBN',

    'FAM',
    'INDI',
    'OBJE',
    'NOTE', 'CONC', 'CONT',
    'REPO',
    'SOUR',
    'SUBM',

    'TRLR',

    'TAG_NAME', # for matching yet undefined tag names
]

tokens = [
    'LEVEL',
    'XREF',
    'WORD',
    'LEVEL_UP',
    'LEVEL_DOWN',
]
tokens.extend(tag_names)

# everything can be recognised as a word except LEVEL_UP and LEVEL_DOWN delimiters; preprocessor guaratees that LEVEL_UP and LEVEL_DOWN do not show up as words
words = copy.copy(tokens)
words.remove('LEVEL_UP')
words.remove('LEVEL_DOWN')

regex_TAG_NAME = r'^_?[A-Z]{3,}$' # TAG_NAME is uppercase, maybe starts with
                                  # _ and is longer than 3 chars
regex_LEVEL = r'^[0-9]+$' # LEVEL is a number

def TAG_NAME(t):
    t.type = 'TAG_NAME'

    val = t.value.strip()

    for n in tag_names: # determine which tag specifficaly we have here
        if val == n:
            t.type = n
            return t

    return t

def LEVEL(t):
    t.type = 'LEVEL'

    t.value = int(t.value)

    return t

def t_WORD(t):
    r'[ ]+[^ ]+'

    tag_name = re.compile(regex_TAG_NAME)
    level = re.compile(regex_LEVEL)

    val = t.value.strip()

    t.type = 'WORD'
    t.value = val

    if val == open_brace:
        t.type = 'LEVEL_UP'
    elif val == close_brace:
        t.type = 'LEVEL_DOWN'
    elif val[0] == '@' and val[-1] == '@' and '@' not in val[1:-2]:
        t.type = 'XREF'
    elif tag_name.match(val):
        t = TAG_NAME(t)
    elif level.match(val):
        t = LEVEL(t)

    return t


# Define a rule so we can track line numbers
def t_newline(t):
    r'\n+'
    t.lexer.lineno += len(t.value)

# A string containing ignored characters
t_ignore  = '\t'

# Error handling rule
def t_error(t):
    print "Illegal character '%s'" % t.value[0]
    t.lexer.skip(1)

# Build the lexer
lexer = lex.lex()

if __name__ == "__main__":
    # preprocess the file
    from preparser import Preprocessor
#    preprocessor = Preprocessor('../test/wright.ged')
    preprocessor = Preprocessor('foo.ged')
    data = preprocessor.preprocess_file()
    set_delimiters(preprocessor.open_brace, preprocessor.close_brace)

    # Give the lexer some input
    lexer.input(data)

    # Tokenize
    while True:
        tok = lexer.token()
        if not tok: break      # No more input
        print tok

