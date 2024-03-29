## @package pUtils
## @brief Package containing utilities of general interest.

import re
import types
import pSafeLogger
logger = pSafeLogger.getLogger('pUtils')

from math import log10

## @brief Convert a ROOT cut string to a string
#  representing a python valid line 
#
## @param CutString
#  The ROOT cut string
## @param prefix
#  The prefix to be added ("entry." by default)

def Root2PythonCutConverter(CutString, prefix = "entry." ):
    if CutString == '':
        return "True"
    CHANGE_DICT = {"&&":" and ",
                   "!": " not ",
                   "||": " or "}
    
    tmpCutString = AddCutPrefix(CutString, prefix)
   
    
    for (RootKey, PyKey) in  CHANGE_DICT.items():
        
        tmpCutString = tmpCutString.replace(RootKey, PyKey)
    return tmpCutString

## @brief Add a user selectable prefix to all the variables
#  of a ROOT Cut string
#
## @param CutString
#  The ROOT cut string
## @param prefix
#  The prefix to be added (empty by default)

def AddCutPrefix(CutString, prefix = "" ):

    Seeker = re.compile("[a-z_]+", re.IGNORECASE)

    tmpCutString = CutString
    CutIter = Seeker.finditer(CutString)

    varList = []
    for varMatch in CutIter:
        varName = varMatch.group()
        if varName not in varList:
	    tmpCutString = tmpCutString.replace(varName, prefix + varName)
	    varList.append(varName)

    return tmpCutString

## @brief Return a list of the variables involved in a cut.
#
#  Used for disabling the branches of a ROOT tree if necessary for speed.
## @param cut
#  The cut expression.

def getCutVariables(cut):
    seeker = re.compile("[a-z_12]+", re.IGNORECASE)
    iterator = seeker.finditer(cut)
    varList = []
    for item in iterator:
        varName = item.group()
        if varName not in varList and not varName.isdigit():
            varList.append(varName)
    return varList

## @brief Expand a specified string to a given length.
#
## @param string
#  The string to be formatted.
## @param targetLength
#  The goal string length.

def expandString(string, targetLength):
    string         = str(string)
    originalLength = len(string)
    requiredSpaces = targetLength - originalLength
    if requiredSpaces >= 0:
        return '%s%s' % (string, ' '*requiredSpaces)
    else:
        leftSplit   = (targetLength - 3)/2
        rightSplit  = (targetLength - 3)/2
        return '%s...%s' % (string[:leftSplit], string[-rightSplit:])

## @brief Format a number with a given number of decimal places, then expand
#  it as a string of given length.
## @param number
#  The real number to be formatted.
## @param targetLength
#  The goal string length.

def expandNumber(number, targetLength):
    string = '%s' % number
    originalLength = len(string)
    requiredSpaces = targetLength - originalLength
    if requiredSpaces >= 0:
        return '%s%s' % (string, ' '*requiredSpaces)
    else:
        return '%s' % string[:targetLength]

def formatFloat(number):
    try:
        if int(number) == number:
            return '%d' % int(number)
    except OverflowError:
        pass
    if abs(number) > 0.001 and abs(number) < 100:
        try:
	    numDecFigures = int(3 - log10(abs(number)))
        except:
	    numDecFigures = 3	
	formatString = '%' + '.%df' % numDecFigures
        return formatString % number
    elif abs(number) >= 100 and number < 10000:
        return '%.1f' % number
    else:
        return '%.2e' % number

## @brief Format a number in such a way it gets nicely printed on the
#  terminal or in the reports.
#
#  Depending on the type and magnitude different formatting strings are
#  used. At least three significant digits are guranteed.
#
## @param number
#  The number to be formatted.

def formatNumber(number):
    if number == 0:
        return '0'
    elif type(number) == types.IntType:
        return '%d' % number
    elif type(number) == types.FloatType:
        return formatFloat(number)
    else:
        try:
            return formatFloat(float(number))
        except:
            return number

## @brief Format a string to appear with monospace (typesetter) font in the
#  test report
## @param string
#  The string to be formatted.

def verbatim(string):
    return '<tt>%s</tt>' % string

## @brief Expand a string of the form 'a, b, c-d' into a pyhton list.
## @param string
#  The string to be expanded.

def expandList(string):
    outputList = []
    pieces = string.split(',')
    for piece in pieces:
        try:
            (min, max) = piece.split('-')
            outputList += range(eval(min), eval(max) + 1)
        except:
            outputList.append(eval(piece))
    return outputList



if __name__ == '__main__':
    print expandList('0-4, 16-20, 32-36, 48-52')
    #print getCutVariables("CalTransRms > 12.3 && CalTransRms < 34 && CalXtalsTrunc > 8 && CalXtalsTrunc < 20")
    #print getCutVariables("x:y:z")
