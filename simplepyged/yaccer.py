#-*- coding: utf-8 -*-
from lexer import tokens, words, tag_names, set_delimiters
import copy
import time
import records
import ply.yacc as yacc
from preparser import Preprocessor

# UGLY HACK
# for some reason parse() method cannot access return value of
# p_gedcom method, so those two methods use global variable to
# communicate
level_0_global = None

def p_gedcom(p):
    """gedcom : header submission_record records
              | header records"""
    header = p[1]
    if len(p) == 3:
        records = p[2]
    elif len(p) == 4:
        records = p[3]
    else:
        raise Exception('Error in head production.')

    retval = records
    retval.append(header)
    retval.reverse()

    global level_0_global # ugly hack, see beginning or this file
    level_0_global = copy.copy(retval)
    return retval

def p_records_trlr(p):
    'records : trailer'
    p[0] = []

#This is more elegant version, but doesn't work for some reason:
#def p_gedcom(p):
#    """gedcom : header submission_record records trailer
#              | header records trailer
#    """
#    None

#def p_records_last(p):
#    'records : record'
#    None
    


###################
# TOP LEVEL NODES #
###################

def p_header(p):
    'header : LEVEL_UP LEVEL HEAD lines LEVEL_DOWN'
    None

def p_submission_record(p):
    'submission_record : LEVEL_UP LEVEL XREF SUBN lines LEVEL_DOWN'
    None
    
def p_records(p):
    'records : record records'
#    print fmt_record(p[1])
#    print
#    print
    retval = p[2]
    retval.append(p[1])
    p[0] = retval

def p_trailer(p):
    'trailer : LEVEL_UP LEVEL TRLR LEVEL_DOWN'
    None
    
###########
# RECORDS #
###########

def p_record(p):
    """record : fam_record
            | individual_record
            | submitter_record
            | note_record 
            | multimedia_record 
            | repository_record 
            | source_record"""

#    print fmt_record(p[1])
    p[0] = p[1]

def init_record(cls, p, value = None):
    level = p[2]
    xref = p[3]
    tag = p[4]
    children = p[5]
        
    if level != 0:
        raise Exception('Found record in line with nonzero level.')

    record = cls(level, xref, tag, value, children)

    for child in children:
        child._parent_line = record

    return record
        
def p_fam_record(p):
    """fam_record : LEVEL_UP LEVEL XREF FAM lines LEVEL_DOWN"""
    p[0] = init_record(records.Family, p)

def p_individual_record(p):
    """individual_record : LEVEL_UP LEVEL XREF INDI lines LEVEL_DOWN"""
    p[0] = init_record(records.Individual, p)

def p_multimedia_record(p):
    """multimedia_record : LEVEL_UP LEVEL XREF OBJE lines LEVEL_DOWN"""
    p[0] = init_record(records.Multimedia, p)

def p_note_record(p):
    """note_record : LEVEL_UP LEVEL XREF NOTE words lines LEVEL_DOWN"""
    #Note has value (other records don't), so it has to be rewired a bit
    p[0] = init_record(records.Note, [p[0], p[1], p[2], p[3], p[4], p[6]], p[5])

def p_repository_record(p):
    """repository_record : LEVEL_UP LEVEL XREF REPO lines LEVEL_DOWN"""
    p[0] = init_record(records.Repository, p)

def p_source_record(p):
    """source_record : LEVEL_UP LEVEL XREF SOUR lines LEVEL_DOWN"""
    p[0] = init_record(records.Source, p)

def p_submitter_record(p):
    """submitter_record : LEVEL_UP LEVEL XREF SUBM lines LEVEL_DOWN"""
    p[0] = init_record(records.Submitter, p)


#########
# LINES #
#########
    
def p_lines(p):
    'lines : lines line'
    retval = p[1]
    retval.append(p[2])
    p[0] = retval

def p_lines_empty(p):
    'lines : '
    p[0] = []

def p_line(p):
    'line : LEVEL_UP LEVEL line_content lines LEVEL_DOWN'
    level = p[2]
    [xref, tag, value] = p[3]
    children = p[4]
        
    if xref is not None:
        raise Exception('Found XREF in line with nonzero level.')

    line = records.Line(level, None, tag, value, children)

    for child in children:
        child._parent_line = line

    p[0] = line


def p_line_content(p):
    'line_content : optional_xref tag_name optional_line_value'
    p[0] = p[1:]

def p_optional_xref(p):
    'optional_xref : XREF'
    p[0] = p[1]
    
def p_optional_xref_empty(p):
    'optional_xref : '
    p[0] = None

def p_tag_name(p):
    p[0] = str(p[1])
p_tag_name.__doc__ = 'tag_name : ' + '\n| '.join(tag_names)
    
def p_optional_line_value(p):
    'optional_line_value : words'
    p[0] = p[1]
    
def p_optional_line_value_empty(p):
    'optional_line_value : '
    p[0] = None
    
#########
# WORDS #
#########
    
def p_words(p):
    'words : words word'
    p[0] = p[1] + ' ' + p[2]

def p_words_last(p):
    'words : word'
    p[0] = p[1]

def p_word(p):
    p[0] = str(p[1])
p_word.__doc__ = 'word : ' + '\n| '.join(words)


# Error rule for syntax errors
def p_error(p):
    print "Error: " + str(p)


def parse(filename):
    preprocessor = Preprocessor(filename)
    data = preprocessor.preprocess_file()
    set_delimiters(preprocessor.open_brace, preprocessor.close_brace)

    # Build the parser
    parser = yacc.yacc()

    global level_0_global # ugly hack, see beginning or this file
    level_0_global = None
    result = parser.parse(data)
    return level_0_global

if __name__ == "__main__":
#    level_0 = parse('foo.ged')
#    level_0 = parse('../test/wright.ged')
    level_0 = parse('../test/moje.ged')

#    for record in level_0[1:]:
#        print record.xref()

def fmt_record(arg):
    """Method for displaying a record while debugging."""
    retval = ''
    if type(arg) == type([1, 2]):
        [xref, tag, lines] = arg
        retval += tag + ': ' + xref + "\n"
        retval += "=========" + "\n"
        retval += str(lines) + "\n\n"
    else:
        retval += arg._tag + ': ' + arg._xref + "\n"
        retval += "=========" + "\n"
        if arg._value is not None:
            retval += "Value: " + arg._value + "\n"
        retval += str(arg._children_lines) + "\n\n"
        
    return retval
