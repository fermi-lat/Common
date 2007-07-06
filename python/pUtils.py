## @package pUtils
## @brief Package containing utilities of general interest.

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
