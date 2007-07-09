## @package pAsciiWriter
## @brief Module providing functions for writing generic ASCII files.

import pSafeLogger
logger = pSafeLogger.getLogger('pAsciiWriter')

import sys
import os


## @brief Implementation of an ASCII writer.

class pAsciiWriter:

    ## @var NUM_INDENT_SPACES
    ## @brief The default number of spaces for the indentation.
    
    NUM_INDENT_SPACES = 4

    ## @brief Constructor.
    ## @param self
    #  The class instance.
    ## @param outputFilePath
    #  The path for the output file (None by default).

    def __init__(self, outputFilePath = None):

        ## @var OutputFile
        ## @brief The actual output file.

        ## @var IndentLevel
        ## @brief The current indentation level.
        
        self.OutputFile  = None
        self.IndentLevel = None
        if outputFilePath is not None:
            self.openFile(outputFilePath)

    ## @brief Open an ASCII output file.
    ## @param self
    #  The class instance.
    ## @param outputFilePath
    #  The path to the output file.
    ## @param mode
    #  The file open mode.

    def openFile(self, outputFilePath, mode = 'w'):
        logger.debug('Opening output file %s...' % outputFilePath)
        self.OutputFile = file(outputFilePath, mode)
        self.setIndentLevel(0)

    ## @brief Close the output file.
    ## @param self
    #  The class instance.

    def closeFile(self):
        if self.OutputFile is not None:
            self.OutputFile.close()
            self.OutputFile  = None
            self.IndentLevel = None

    ## @brief Set the indentation level.
    ## @param self
    #  The class instance.
    ## @param level
    #  The target indentation level.
    
    def setIndentLevel(self, level):
        if level >= 0:
            self.IndentLevel = level
        else:
            logger.warning('Negative indent level requested, set to 0.')
            self.IndentLevel = 0

    ## @brief Increase the indentation level.
    ## @param self
    #  The class instance.
    ## @param numLevels
    #  The number of levels.
    
    def indent(self, numLevels = 1):
        self.setIndentLevel(self.IndentLevel + numLevels)

    ## @brief Decrease the indentation level.
    ## @param self
    #  The class instance.
    ## @param numLevels
    #  The number of levels.

    def backup(self, numLevels = 1):
        self.setIndentLevel(self.IndentLevel - numLevels)

    ## @brief Write a generic piece of text to the output file.
    ## @param self
    #  The class instance.
    ## @param text
    #  The text to be written.

    def __write(self, text):
        if self.OutputFile is not None:
            self.OutputFile.writelines(text)
        else:
            logger.error('Output file not existing.')
            sys.exit('Abort.')

    ## @brief Write a carriage return to the output file.
    ## @param self
    #  The class instance.

    def newLine(self):
        self.__write('\n')

    ## @brief Write a defined number of carriage returns to the output file.
    ## @param self
    #  The class instance.
    ## @param numLines
    #  The number of carriage returns to be written.

    def newLines(self, numLines):
        for i in range(numLines):
            self.newLine()

    ## @brief Write a line (correctly indented) to the output file.
    ## @param self
    #  The class instance.
    ## @param line
    #  The line to be written.    

    def writeLine(self, line):
        spaces = self.IndentLevel*self.NUM_INDENT_SPACES*' '
        self.__write('%s%s\n' % (spaces, line))
    


if __name__ == '__main__':
    writer = pAsciiWriter('ascii_test.txt')
    writer.writeLine('Howdy partner, how are you doing?')
    writer.indent(3)
    writer.writeLine('Well...')
    writer.writeLine('Not so bad!')
    writer.newLines(2)
    writer.backup()
    writer.writeLine('Slowly...')
    writer.backup()
    writer.writeLine('... going...')
    writer.backup()
    writer.writeLine('... back')
    writer.backup()
    writer.writeLine('Too much!')
    writer.closeFile()
