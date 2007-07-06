
import pSafeLogger
logger = pSafeLogger.getLogger('pBaseReportGenerator')

import os
import sys
import commands
import time

import pUtils

from pSafeROOT import ROOT


class pBaseReportGenerator:

    CONFIG_FILE_NAME   = 'config.doxygen'
    MAIN_PAGE_NAME     = 'mainpage'
    HTML_DIR_NAME      = 'html'
    LATEX_DIR_NAME     = 'latex'
    AUX_CANVAS_WIDTH   = 500
    AUX_CANVAS_HEIGHT  = 400
    AUX_CANVAS_COLOR   = 10
    LATEX_IMAGES_WIDTH = 11.0
    
    def __init__(self, outputDirPath, mainPageTitle, forceOverwrite = True):
        self.OutputDirPath  = outputDirPath
        self.MainPageTitle  = mainPageTitle
        self.ForceOverwrite = forceOverwrite
        self.HtmlDirPath    = os.path.join(self.OutputDirPath,\
                                           self.HTML_DIR_NAME)
        self.LatexDirPath   = os.path.join(self.OutputDirPath,\
                                           self.LATEX_DIR_NAME)
        self.ConfigFilePath = os.path.join(self.OutputDirPath,
                                           self.CONFIG_FILE_NAME)
        self.DoxyFilesDict  = {}
        self.AuxRootCanvas  = None

    def createAuxRootCanvas(self, batchMode = True):
        if batchMode:
            ROOT.gROOT.SetBatch(1)
        self.AuxRootCanvas  = ROOT.TCanvas('canvas', 'canvas',\
                                           self.AUX_CANVAS_WIDTH,\
                                           self.AUX_CANVAS_HEIGHT)
        self.AuxRootCanvas.SetFillColor(self.AUX_CANVAS_COLOR)

    def deleteAuxRootCanvas(self):
        self.AuxRootCanvas = None
        ROOT.gROOT.SetBatch(0)

    ## @brief Create the output directory for the report.
    ## @param self
    #  The class instance.
    
    def __createOutputDir(self):
        logger.info('Creating output directory...')
        if os.path.exists(self.OutputDirPath):
            if not self.ForceOverwrite:
                logger.warn('Output directory already exists.')
                answer = None
                while answer not in ['y', 'n']:
                    answer = raw_input('Do you want to overwrite the old ' +\
                                       'files (y or n)?\n')
                if answer == 'n':
                    sys.exit('Aborting...')
            logger.info('Cleaning old directory, first...')
            os.system('rm -rf %s' % self.OutputDirPath)
        os.makedirs(self.OutputDirPath)

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

    def openOutputFile(self, filePath, mode = 'w'):
        try:
            return file(filePath, mode)
        except:
            sys.exit('Could not open output file %s' % filePath)

    def addPage(self, pageName, pageTitle):
        pageFileName = '%s.doxygen' % pageName.lower().replace(' ', '_')
        filePath = os.path.join(self.OutputDirPath, pageFileName)
        self.DoxyFilesDict[pageName] = self.openOutputFile(filePath)
        self.writePageHeader(pageName, pageTitle)
        if not os.path.exists(self.ConfigFilePath):
            configFile = self.openOutputFile(self.ConfigFilePath)
            configFile.writelines('FILE_PATTERNS = %s '% pageFileName)
        else:
            configFile = self.openOutputFile(self.ConfigFilePath, 'a')
            configFile.writelines('%s '% pageFileName)
        configFile.close()
    
    def closeDoxyFiles(self):
        for file in self.DoxyFilesDict.values():
            file.close()

    ## @brief Write a line to the doxygen main page file.
    ## @param self
    #  The class instance.
    ## @param line
    #  The ilne to be written.

    def write(self, line, page = MAIN_PAGE_NAME):
        self.DoxyFilesDict[page].writelines(line)

    ## @brief Write a carriage return to the doxygen main page file.
    ## @param self
    #  The class instance.  

    def newline(self, page = MAIN_PAGE_NAME):
        self.write('\n', page)

    def writePageHeader(self, pageName, pageTitle):
        if pageName == self.MAIN_PAGE_NAME:
            header = '/** @%s %s\n' % (pageName, pageTitle)
        else:
            header = '/** @page %s %s\n' % (pageName, pageTitle)
        self.write(header, pageName)

    def writeMainHeader(self, author = 'unknown'):
        header = '@htmlonly\n'                                            +\
                 '<center>\n'                                             +\
                 '<a href="../latex/refman.ps" > PS report  </a> &nbsp\n' +\
                 '<a href="../latex/refman.pdf"> PDF report </a>\n'       +\
                 '</center>\n'                                            +\
                 '@endhtmlonly\n'                                         +\
                 '@author %s \n' % author                                 +\
                 '@date %s\n' % time.asctime()
        self.write(header)
        self.newline()

    ## @brief Write the trailer in the doxygen main page file.
    ## @param self
    #  The class instance.

    def writeTrailers(self):
        for pageName in self.DoxyFilesDict.keys():
            self.newline(pageName)
            self.write('*/', pageName)

    ## @brief Add a section to the doxygen main page file.
    ## @param self
    #  The class instance.
    ## @param label
    #  The section label.
    ## @param name
    #  The section name.

    def addSection(self, label, name, page = MAIN_PAGE_NAME):
        self.newline(page)
        self.write('@section %s %s\n' % (label, name), page)
        self.newline(page)

    def __LaTeXTableHeader(self, caption):
        header = '@latexonly\n'               +\
                 '\\begin{table}[!htb]\n'      +\
                 '\\begin{center}\n'           +\
                 '\\caption{%s}\n' % (caption) +\
                 '\\label{%s}\n' % (caption)
        return header

    def __LaTeXTableHeaderRow(self, items):
        line = '\\begin{tabular}{|'
        for i in items:
            line += "c|"
        line += '}\n\\hline\n' + self.__LaTeXTableRow(items) +\
                '\\hline\n\\hline\n'
        return line

    def __LaTeXTableRow(self, items):
        line = ''
        for item in items:
            line += str(item) + ' & '
        line = line[:-3] + '\\\\ \n\hline\n'
        return pUtils.formatForLatex(line)

    def __LaTeXTableTrailer(self):
        trailer = '\end{tabular}\n' +\
                  '\end{center}\n'  +\
                  '\end{table}\n'   +\
                  '@endlatexonly\n\n'
        return trailer

    def writeLaTeXTable(self, header, rows, caption = '',\
                       pageName = MAIN_PAGE_NAME):        
        self.write(self.__LaTeXTableHeader(caption), pageName)
        self.write(self.__LaTeXTableHeaderRow(header), pageName)
        for row in rows:
            self.write(self.__LaTeXTableRow(row), pageName)
        self.write(self.__LaTeXTableTrailer(), pageName)
    
    def __htmlTableHeader(self, caption):
        header = '@htmlonly\n'                         +\
                 '<table border="1" width="100%">\n'   +\
                 '<caption>%s</caption>\n' % (caption)
        return header

    def __htmlTableHeaderRow(self, items):
        return self.__htmlTableRow(items, True)

    def __htmlTableRow(self, items, bold = False):
        row = '<tr>\n'
        for item in items:
            row += '%s\n' % self.__htmlTableCell(item, bold)
        row += '</tr>\n'
        return row

    def __htmlTableCell(self, item, bold = False):
        if not bold:
            return '<td>%s</td>' % item
        else:
            return '<td><b>%s</b></td>' % item

    def __htmlTableTrailer(self):
        trailer = '</table>\n'   +\
                  '@endhtmlonly\n\n'
        return trailer

    def writeHtmlTable(self, header, rows, caption = '',\
                       pageName = MAIN_PAGE_NAME):
        self.write(self.__htmlTableHeader(caption), pageName)
        self.write(self.__htmlTableHeaderRow(header), pageName)
        for row in rows:
            self.write(self.__htmlTableRow(row), pageName)
        self.write(self.__htmlTableTrailer(), pageName)

    def writeTable(self, header, rows, caption = '',\
                       pageName = MAIN_PAGE_NAME):
        self.writeHtmlTable(header, rows, caption, pageName)
        self.writeLaTeXTable(header, rows, caption, pageName)

    ## @brief Add a plot to the doxygen main page file.
    ## @todo There's room for improvements, here (in particular one
    #  could write a method in pXmlPlotRep to return a list of plot reps
    #  for all the levels - with their names, titles, etc - and avoid
    #  the name parameter in this function).
    ## @param self
    #  The class instance.
    ## @param plotRep
    #  The pXmlPlotRep object representing the plot.
    ## @param name
    #  The plot name (needs to be passed because it may be different for all
    #  the towers/layers).
    
    def addPlot(self, plotRep, name):
        epsImagePath = os.path.join(self.LatexDirPath, ('%s.eps' % name))
        gifImagePath = os.path.join(self.HtmlDirPath , ('%s.gif' % name))
        epsImageName = os.path.basename(epsImagePath)
        gifImageName = os.path.basename(gifImagePath)
        self.AuxRootCanvas.SetLogx(plotRep.XLog)
        self.AuxRootCanvas.SetLogy(plotRep.YLog)
        try:
            self.InputRootFile.Get(name).Draw(plotRep.DrawOptions)
        except AttributeError:
            sys.exit('Object %s not found in the input file.' % name)
        self.AuxRootCanvas.SaveAs(epsImagePath)
        self.AuxRootCanvas.SaveAs(gifImagePath)
        title   = plotRep.Title
        caption = plotRep.Caption
        block   = ('@htmlonly\n'                                       +\
                   '<div align="center">\n'                            +\
                   '<p><strong>%s.</strong> %s</p>\n'                  +\
                   '<img src="%s" alt="%s">\n'                         +\
                   '</div>\n'                                          +\
                   '@endhtmlonly\n'                                    +\
                   '@latexonly\n'                                      +\
                   '\\begin{figure}[H]\n'                              +\
                   '\\begin{center}\n'                                 +\
                   '\\includegraphics[width=%scm]{%s}\n'               +\
                   '\\caption{{\\bf %s.} %s}\n'                        +\
                   '\\end{center}\n'                                   +\
                   '\\end{figure}\n'                                   +\
                   '@endlatexonly\n'                                   +\
                   '@latexonly\n'                                      +\
                   '\\nopagebreak\n'                                   +\
                   '@endlatexonly\n\n')                                %\
                   (title, caption, gifImageName, gifImageName,         \
                    self.LATEX_IMAGES_WIDTH, epsImageName, title, caption)
        self.write(block)

    ## @brief Run doxygen on the main page.
    ## @param self
    #  The class instance.
    
    def doxygenate(self, verbose = False):
        logger.info('Running doxygen...')
        startTime = time.time()
        command = 'cd %s; doxygen %s' % (self.OutputDirPath,\
                                         self.CONFIG_FILE_NAME)
        if verbose:
            os.system(command)
        else:
            commands.getoutput(command)
        logger.info('Done in %s s.\n' % (time.time() - startTime))

    ## @brief Compile the LaTeX report and make ps and pdf files.
    ## @param self
    #  The class instance.

    def compileLaTeX(self, verbose = False):
        logger.info('Compiling LaTeX report...')
        startTime = time.time()
        command = 'cd %s; make pdf' % self.LatexDirPath
        if verbose:
            os.system(command)
        else:
            commands.getoutput(command)
        logger.info('Done in %s s.\n' % (time.time() - startTime))

    def openReport(self, author = 'unknown'):
        self.createDirs()
        self.addPage(self.MAIN_PAGE_NAME, self.MainPageTitle)
        self.writeMainHeader(author)

    def closeReport(self):
        self.writeTrailers()
        self.closeDoxyFiles()
        
    def compileReport(self, compileLaTeX = True):
        self.doxygenate()
        if compileLaTeX:
            self.compileLaTeX()


if __name__ == '__main__':
    generator = pBaseReportGenerator('./report', 'Base report')
    generator.openReport()
    generator.addSection('test', 'test')
    tableHeader = ['a', 'b', 'c'] 
    tableRows   = [['my_test', 2, 3],
                   [4, 5, 6]]
    generator.writeTable(tableHeader, tableRows, 'Howdy, partner?')
    generator.addPage('details', 'Detailed page')
    generator.writeTable(tableHeader, tableRows, 'Second Test', 'details' )
    generator.closeReport()
    generator.compileReport()

