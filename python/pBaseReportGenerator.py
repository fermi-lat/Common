
import os
import sys
import logging
import commands
import time

import pUtils


class pBaseReportGenerator:

    DOXY_CONFIG_FILE_NAME = 'config.doxygen'
    DOXY_MAIN_FILE_NAME   = 'mainpage.doxygen'
    HTML_DIR_NAME         = 'html'
    LATEX_DIR_NAME        = 'latex'
    
    def __init__(self, outputDirPath, forceOverwrite=True):
        self.OutputDirPath  = outputDirPath
        self.ForceOverwrite = forceOverwrite
        self.HtmlDirPath    = os.path.join(self.OutputDirPath,\
                                           self.HTML_DIR_NAME)
        self.LatexDirPath   = os.path.join(self.OutputDirPath,\
                                           self.LATEX_DIR_NAME)
        self.DoxyMainFile   = None
    
    
    ## @brief Create the output directory for the report.
    ## @param self
    #  The class instance.
    ## @param force
    #  If this flag is set, existing files are overwritten without prompting.
    
    def __createOutputDir(self):
        logging.info('Creating output directory...')
        if os.path.exists(self.OutputDirPath):
            if not self.ForceOverwrite:
                logging.warn('Output directory already exists.')
                answer = None
                while answer not in ['y', 'n']:
                    answer = raw_input('Do you want to overwrite the old ' +\
                                       'files (y or n)?\n')
                if answer == 'n':
                    sys.exit('Aborting...')
            logging.info('Cleaning old directory, first...')
            os.system('rm -rf %s' % self.OutputDirPath)
        os.makedirs(self.OutputDirPath)
        logging.info('Done.\n')

    ## @brief Create the output html report directory.
    ## @param self
    #  The class instance.
    
    def __createHtmlDir(self):
        os.makedirs(self.HtmlDirPath)

    ## @brief Create the output LaTeX report directory.
    ## @param self
    #  The class instance.

    def __createLatexDir(self):
        os.makedirs(self.LatexDirPath)

    ## @brief Create all the necessary output directories.
    ## @param self
    #  The class instance.
    
    def createDirs(self):
        self.__createOutputDir()
        self.__createHtmlDir()
        self.__createLatexDir()

    ## @brief Open a generic file in write mode.
    ## @param self
    #  The class instance.
    ## @param filePath
    #  The file path.

    def openOutputFile(self, filePath):
        try:
            return file(filePath, 'w')
        except:
            sys.exit('Could not open output file %s' % filePath)

        ## @brief Create the doxygen configuration file.
    ## @param self
    #  The class instance.  

    def createDoxyConfigFile(self):
        filePath   = os.path.join(self.OutputDirPath,\
                                  self.DOXY_CONFIG_FILE_NAME)
        configFile = self.openOutputFile(filePath)
        configFile.writelines('FILE_PATTERNS=%s\n' % self.DOXY_MAIN_FILE_NAME)
        configFile.close()

    ## @brief Open the doxygen main page file.
    ## @param self
    #  The class instance.

    def openDoxyMainFile(self):
        filePath = os.path.join(self.OutputDirPath, self.DOXY_MAIN_FILE_NAME)
        self.DoxyMainFile = self.openOutputFile(filePath)

    ## @brief Close the doxygen main page file.
    ## @param self
    #  The class instance.
    
    def closeDoxyMainFile(self):
        self.DoxyMainFile.close()

    ## @brief Write a line to the doxygen main page file.
    ## @param self
    #  The class instance.
    ## @param line
    #  The ilne to be written.

    def write(self, line):
        self.DoxyMainFile.writelines(line)

    ## @brief Write a carriage return to the doxygen main page file.
    ## @param self
    #  The class instance.  

    def skipLine(self):
        self.write('\n')

    ## @brief Write the header in the doxygen main page file.
    ## @param self
    #  The class instance.

    def writeHeader(self, author = 'automatically generated'):
        header = '/** @mainpage Fast monitor report\n'                    +\
                 '@htmlonly\n'                                            +\
                 '<center>\n'                                             +\
                 '<a href="../latex/refman.ps" > PS report  </a> &nbsp\n' +\
                 '<a href="../latex/refman.pdf"> PDF report </a>\n'       +\
                 '</center>\n'                                            +\
                 '@endhtmlonly\n'                                         +\
                 '@author %s \n' % author                                 +\
                 '@date %s\n' % time.asctime()
        self.write(header)
        self.skipLine()

    ## @brief Write the trailer in the doxygen main page file.
    ## @param self
    #  The class instance.

    def writeTrailer(self):
        self.skipLine()
        self.write('*/')

    ## @brief Add a section to the doxygen main page file.
    ## @param self
    #  The class instance.
    ## @param label
    #  The section label.
    ## @param name
    #  The section name.

    def addSection(self, label, name):
        self.skipLine()
        self.write('@section %s %s\n' % (label, name))
        self.skipLine()

    ## @brief Run doxygen on the main page.
    ## @param self
    #  The class instance.
    
    def doxygenate(self, verbose = False):
        logging.info('Running doxygen...')
        startTime = time.time()
        command = 'cd %s; doxygen %s' % (self.OutputDirPath,\
                                         self.DOXY_CONFIG_FILE_NAME)
        if verbose:
            os.system(command)
        else:
            commands.getoutput(command)
        logging.info('Done in %s s.\n' % (time.time() - startTime))

    ## @brief Compile the LaTeX report and make ps and pdf files.
    ## @param self
    #  The class instance.

    def compileLaTeX(self, verbose = False):
        logging.info('Compiling LaTeX report...')
        startTime = time.time()
        command = 'cd %s; make pdf' % self.LatexDirPath
        if verbose:
            os.system(command)
        else:
            commands.getoutput(command)
        logging.info('Done in %s s.\n' % (time.time() - startTime))

    def openReport(self):
        self.createDirs()
        self.createDoxyConfigFile()
        self.openDoxyMainFile()
        self.writeHeader()

    def closeReport(self):
        self.writeTrailer()
        self.closeDoxyMainFile()

    def compileReport(self):
        self.doxygenate()
        self.compileLaTeX()


if __name__ == '__main__':
    logging.basicConfig(level = logging.DEBUG)
    generator = pBaseReportGenerator('./report')
    generator.openReport()
    generator.addSection('test', 'test')
    generator.closeReport()
    generator.compileReport()

