## @package pUtils
## @brief Package containing utilities of general interest.

import logging

## @brief Expand a specified string to a given length.
#
## @param string
#  The string to be formatted.
## @param length
#  The goal string length.

def expandString(string, targetLength, margin = 0):
    string         = str(string)
    originalLength = len(string)
    requiredSpaces = targetLength - originalLength
    if requiredSpaces >= margin:
        return '%s%s' % (string, ' '*requiredSpaces)
    else:
        leftMargin  = margin/2
        rightMargin = margin - leftMargin
        leftSplit   = (targetLength - 3)/2 + 1 - leftMargin
        rightSplit  = targetLength - 3 - leftSplit - 1 - rightMargin
        return '%s...%s%s' % (string[:leftSplit], string[-rightSplit:],
                              ' '*margin)

## @brief Format a number with a given number of decimal places, then expand
#  it as a string of given length.
## @param number
#  The real number to be formatted.
## @param numDecPlaces
#  The number of decimal places required.
## @param length
#  The goal string length.

def expandNumber(number, targetLength, margin = 0):
    string = '%s' % number
    originalLength = len(string)
    requiredSpaces = targetLength - originalLength
    if requiredSpaces >= margin:
        return '%s%s' % (string, ' '*requiredSpaces)
    else:
        return '%s%s' % (string[:targetLength - margin + 1], ' '*margin)

## @brief Format a string to be put in the LaTeX version of the report.
#
#  The following operations are performed:
#  @li Replace '_' with '\\_' (to allow the '_' out of the math mode).
## @param string
#  The string to be formatted.

def formatForLatex(string):
    return string.replace('_', '\_')

## @brief Format a string to appear with monospace (typesetter) font in the
#  test report
## @param string
#  The string to be formatted.

def verbatim(string):
    return '<tt>%s</tt>' % string


if __name__ == '__main__':
    print '"%s"' % expandString('test')
    print '"%s"' % expandString('test', 8)
    print '"%s"' % expandNumber(1.236547)
