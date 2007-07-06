## @package pBaseReportGenerator
## @brief Base package for autoamtic generation of test reports.
#
#  The basic strategy is to generate a set of doxygen pages which can
#  be automatically compiled to provide html, LaTeX, ps and pdf outputs.
#  The following features are supported:
#  @li Multiple pages
#  @li Sections, subsections
#  @li Images (with the capability of producing gif and eps files
#  directly from ROOT objects).
#  @li Tables (both in html and LaTeX)
#  @li Formatted representation of python dictionaries.


import pSafeLogger
logger = pSafeLogger.getLogger('pBaseReportGenerator')

import os
import sys
import commands
import time

import pUtils

from pSafeROOT import ROOT


## @brief Base class for aoutomatic generation of test reports.

class pBaseReportGenerator:

    CONFIG_FILE_NAME   = 'config.doxygen'
    MAIN_PAGE_LABEL    = 'mainpage'
    HTML_DIR_NAME      = 'html'
    LATEX_DIR_NAME     = 'latex'
    AUX_CANVAS_WIDTH   = 500
    AUX_CANVAS_HEIGHT  = 400
    AUX_CANVAS_COLOR   = 10
    LATEX_IMAGES_WIDTH = 11.0

    ## @brief Base constructor.
    ## @param self
    #  The class instance.
    ## @param outputDirPath
    #  The path to the directory in which the report must be created.
    #
    #  Two subdirectories (html and latex) will be created therein.
    ## @param mainPageTitle
    #  The title of the main page.
    ## @param forceOverwrite
    #  If True (default) the output dir is overwritten without messages.
    
    def __init__(self, outputDirPath, mainPageTitle = 'Main page',\
                 author = 'unknown', forceOverwrite = True):
        self.OutputDirPath  = outputDirPath
        self.MainPageTitle  = mainPageTitle
        self.Author         = author
        self.ForceOverwrite = forceOverwrite
        self.HtmlDirPath    = os.path.join(self.OutputDirPath,\
                                           self.HTML_DIR_NAME)
        self.LatexDirPath   = os.path.join(self.OutputDirPath,\
                                           self.LATEX_DIR_NAME)
        self.ConfigFilePath = os.path.join(self.OutputDirPath,
                                           self.CONFIG_FILE_NAME)
        self.DoxyFilesDict  = {}
        self.AuxRootCanvas  = None

    ## @brief Create an auxiliary ROOT canvas to draw plots on.
    #
    #  Used for including in the report histograms and graphs from a ROOT file.
    ## @param self
    #  The class instance.
    ## @param batchMode
    #  If True (default) ROOT is set in batch mode for preventing the canvas
    #  from appearing on the screen.
    
    def createAuxRootCanvas(self, batchMode = True, verbose = False):
        if batchMode:
            ROOT.gROOT.SetBatch(1)
        if not verbose:
            pass
        self.AuxRootCanvas  = ROOT.TCanvas('canvas', 'canvas',\
                                           self.AUX_CANVAS_WIDTH,\
                                           self.AUX_CANVAS_HEIGHT)
        self.AuxRootCanvas.SetFillColor(self.AUX_CANVAS_COLOR)

    ## @brief Delete the auxiliary ROOT canvas and put back ROOT in non-batch
    #  mode.
    ## @param self
    #  The class instance.

    def deleteAuxRootCanvas(self):
        self.AuxRootCanvas = None
        ROOT.gROOT.SetBatch(0)

    ## @brief Open the report.
    #
    #  Namely create the output directory structure and create the main page.
    ## @param self
    #  The class instance.
    ## @param author
    #  The page author (typically the script who generated it).

    def openReport(self):
        self.createDirs()
        self.addPage(self.MAIN_PAGE_LABEL, self.MainPageTitle)

    ## @brief Close the report.
    #
    #  Which means that the trailer is written and the files are closed.
    ## @param self
    #  The class instance.

    def closeReport(self):
        self.writeTrailers()
        self.closeDoxyFiles()

    ## @brief Create the base output directory for the report.
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
        logger.info('Done.\n')

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
    ## @param mode
    #  The open mode.

    def openOutputFile(self, filePath, mode = 'w'):
        try:
            return file(filePath, mode)
        except:
            sys.exit('Could not open output file %s' % filePath)

    ## @brief Close all the opened doxygen files.
    
    def closeDoxyFiles(self):
        for file in self.DoxyFilesDict.values():
            file.close()

    ## @brief Add a page to the report.
    #
    #  This involves the creation of a new doxygen file for the page which
    #  is then added with a new key to the DoxyFilesDict variable.
    #  The Doxygen configuration file is also updated.
    ## @param self
    #  The class instance.
    ## @param pageLabel
    #  The page label (used for the doxygen internal references).
    ## @param pageTitle
    #  The page title (appearing on the report)

    def addPage(self, label, title):
        pageFileName = '%s.doxygen' % label.lower().replace(' ', '_')
        filePath = os.path.join(self.OutputDirPath, pageFileName)
        self.DoxyFilesDict[label] = self.openOutputFile(filePath)
        self.writePageHeader(label, title)
        if not os.path.exists(self.ConfigFilePath):
            configFile = self.openOutputFile(self.ConfigFilePath)
            configFile.writelines('FILE_PATTERNS = %s '% pageFileName)
        else:
            configFile = self.openOutputFile(self.ConfigFilePath, 'a')
            configFile.writelines('%s '% pageFileName)
        configFile.close()

    ## @brief Write a line to the doxygen main page file.
    ## @param self
    #  The class instance.
    ## @param line
    #  The ilne to be written.

    def write(self, line, pageLabel = MAIN_PAGE_LABEL):
        self.DoxyFilesDict[pageLabel].writelines(line)

    ## @brief Write a carriage return to the doxygen main page file.
    ## @param self
    #  The class instance.  

    def newline(self, pageLabel = MAIN_PAGE_LABEL):
        self.write('\n', pageLabel)

    ## @brief Write the page header.
    #
    #  Note that the page header for the mainpage is slightly different
    #  with respect to those of the other pages.
    ## @param self
    #  The class instance
    ## @param pageLabel
    #  The page label (used for the doxygen internal references).
    ## @param pageTitle
    #  The page title (appearing on the report)

    def writePageHeader(self, pageLabel, pageTitle):
        if pageLabel == self.MAIN_PAGE_LABEL:
            header = '/** @%s %s\n' % (pageLabel, pageTitle)              +\
                     '@htmlonly\n'                                       +\
                     '<center>\n'                                        +\
                     '<a href="../latex/refman.ps">PS report</a>&nbsp\n' +\
                     '<a href="../latex/refman.pdf">PDF report</a>\n'    +\
                     '</center>\n'                                       +\
                     '@endhtmlonly\n'                                    +\
                     '@author %s \n' % self.Author                       +\
                     '@date %s\n' % time.asctime()
        else:
            header = '/** @page %s %s\n' % (pageLabel, pageTitle)
        self.write(header, pageLabel)
        self.newline()

    ## @brief Write the trailers in the doxygen pages.
    ## @param self
    #  The class instance.

    def writeTrailers(self):
        for pageLabel in self.DoxyFilesDict.keys():
            self.newline(pageLabel)
            self.write('*/', pageLabel)

    ## @brief Add a section to a doxygen page.
    ## @param self
    #  The class instance.
    ## @param label
    #  The section label.
    ## @param title
    #  The section title.
    ## @param pageLabel
    #  The page label.

    def addSection(self, label, title, pageLabel = MAIN_PAGE_LABEL):
        self.newline(pageLabel)
        self.write('@section %s %s\n' % (label, title), pageLabel)
        self.newline(pageLabel)

    ## @brief Add a subsection to a doxygen page.
    ## @param self
    #  The class instance.
    ## @param label
    #  The subsection label.
    ## @param title
    #  The subsection title.
    ## @param pageLabel
    #  The page label.

    def addSubsection(self, label, title, pageLabel = MAIN_PAGE_LABEL):
        self.newline(pageLabel)
        self.write('@subsection %s %s\n' % (label, title), pageLabel)
        self.newline(pageLabel)

    ## @brief Return the header section for a LaTeX-formatted table.
    ## @param self
    #  The class instance.
    ## @param caption
    #  The table caption.

    def __getLaTeXTableHeader(self, caption):
        header = '@latexonly\n'                +\
                 '\\begin{table}[!htb]\n'      +\
                 '\\begin{center}\n'           +\
                 '\\caption{%s}\n' % (caption) +\
                 '\\label{%s}\n' % (caption)
        return header

    ## @brief Return the header for a LaTeX-formatted table.
    ## @param self
    #  The class instance.
    ## @param items
    #  A python list containing the column labels.

    def __getLaTeXTableHeaderRow(self, items):
        line = '\\begin{tabular}{|'
        for i in items:
            line += "c|"
        line += '}\n\\hline\n' + self.__getLaTeXTableRow(items) +\
                '\\hline\n\\hline\n'
        return line

    ## @brief Return a row for a LaTeX-formatted table.
    ## @param self
    #  The class instance.
    ## @param items
    #  A python list containing the row items.

    def __getLaTeXTableRow(self, items):
        line = ''
        for item in items:
            line += str(item) + ' & '
        line = line[:-3] + '\\\\ \n\hline\n'
        return pUtils.formatForLatex(line)

    ## @brief Return the trailer for a LaTeX-formatted table.
    ## @param self
    #  The class instance.

    def __getLaTeXTableTrailer(self):
        trailer = '\end{tabular}\n' +\
                  '\end{center}\n'  +\
                  '\end{table}\n'   +\
                  '@endlatexonly\n\n'
        return trailer

    ## @brief Write to a specific page of the report a LaTeX-formatted table.
    ## @param self
    #  The class instance.
    ## @param header
    #  A pyhton list of string representing the table header row.
    ## @param rows
    #  A pyhton list of lists of strings representing the actual rows.
    ## @param caption
    #  The table caption.
    ## @param pageLabel
    #  The page label.

    def addLaTeXTable(self, header, rows, caption = '',\
                       pageLabel = MAIN_PAGE_LABEL):        
        self.write(self.__getLaTeXTableHeader(caption), pageLabel)
        self.write(self.__getLaTeXTableHeaderRow(header), pageLabel)
        for row in rows:
            self.write(self.__getLaTeXTableRow(row), pageLabel)
        self.write(self.__getLaTeXTableTrailer(), pageLabel)

    ## @brief Return the header section for a html-formatted table.
    ## @param self
    #  The class instance.
    ## @param caption
    #  The table caption.
    
    def __getHtmlTableHeader(self, caption):
        header = '@htmlonly\n'                       +\
                 '<table border="1" width="100%">\n' +\
                 '<caption>%s</caption>\n' % (caption)
        return header

    ## @brief Return the header row for a html-formatted table.
    ## @param self
    #  The class instance.
    ## @param items
    #  A python list containing the column labels.

    def __getHtmlTableHeaderRow(self, items):
        return self.__getHtmlTableRow(items, True)

    ## @brief Return a row for a html-formatted table.
    ## @param self
    #  The class instance.
    ## @param items
    #  A python list containing the row items.
    ## @param bold
    #  If True (not default) the content of the cell is displayed in bold.

    def __getHtmlTableRow(self, items, bold = False):
        row = '<tr>\n'
        for item in items:
            row += '%s\n' % self.__getHtmlTableCell(item, bold)
        row += '</tr>\n'
        return row

    ## @brief Return a cell for a html-formatted table.
    ## @param self
    #  The class instance.
    ## @param item
    #  The cell item.
    ## @param bold
    #  If True (not default) the content of the cell is displayed in bold.

    def __getHtmlTableCell(self, item, bold = False):
        if not bold:
            return '<td>%s</td>' % item
        else:
            return '<td><b>%s</b></td>' % item

    ## @brief Return the trailer for a html-formatted table.
    ## @param self
    #  The class instance.

    def __getHtmlTableTrailer(self):
        trailer = '</table>\n'   +\
                  '@endhtmlonly\n\n'
        return trailer

    ## @brief Write to a specific page of the report a html-formatted table.
    ## @param self
    #  The class instance.
    ## @param header
    #  A pyhton list of string representing the table header row.
    ## @param rows
    #  A pyhton list of lists of strings representing the actual rows.
    ## @param caption
    #  The table caption.
    ## @param pageLabel
    #  The page label.

    def addHtmlTable(self, header, rows, caption = '',\
                     pageLabel = MAIN_PAGE_LABEL):
        self.write(self.__getHtmlTableHeader(caption), pageLabel)
        self.write(self.__getHtmlTableHeaderRow(header), pageLabel)
        for row in rows:
            self.write(self.__getHtmlTableRow(row), pageLabel)
        self.write(self.__getHtmlTableTrailer(), pageLabel)

    ## @brief Write to a specific page of the report a table, formatted
    #  both in LaTeX and in html.
    ## @param self
    #  The class instance.
    ## @param header
    #  A pyhton list of string representing the table header row.
    ## @param rows
    #  A pyhton list of lists of strings representing the actual rows.
    ## @param caption
    #  The table caption.
    ## @param pageLabel
    #  The page label.

    def addTable(self, header, rows, caption = '',\
                 pageLabel = MAIN_PAGE_LABEL):
        self.addHtmlTable(header, rows, caption, pageLabel)
        self.addLaTeXTable(header, rows, caption, pageLabel)

    ## Return the doxygen block for adding an image to the LaTeX report.
    ## @param self
    #  The class instance.
    ## @param epsImagePath
    #  The path to the actual eps image to be included. 
    ## @param title
    #  The image title.
    ## @param caption
    #  The image caption.

    def __getLaTeXImageBlock(self, epsImagePath, title, caption):
        block = ('@latexonly\n'                        +\
                 '\\begin{figure}[H]\n'                +\
                 '\\begin{center}\n'                   +\
                 '\\includegraphics[width=%scm]{%s}\n' +\
                 '\\caption{{\\bf %s.} %s}\n'          +\
                 '\\end{center}\n'                     +\
                 '\\end{figure}\n'                     +\
                 '\\nopagebreak\n'                     +\
                 '@endlatexonly\n\n')                  %\
                 (self.LATEX_IMAGES_WIDTH, epsImagePath, title, caption)
        return block
    
    ## @brief Add to a specific page of the report a LaTeX-formatted image.
    ## @param self
    #  The class instance.
    ## @param epsImagePath
    #  The path to the actual eps image.
    ## @param title
    #  The image title.
    ## @param caption
    #  The image caption.
    ## @param pageLabel
    #  The page label.

    def addLaTeXImage(self, epsImagePath, title = '', caption = '',\
                      pageLabel = MAIN_PAGE_LABEL):
        self.write(self.__getLaTeXImageBlock(epsImagePath, title, caption),\
                   pageLabel)

    ## Return the doxygen block for adding a image to the html report.
    ## @param self
    #  The class instance.
    ## @param gifImagePath
    #  The path to the actual gif image to be included. 
    ## @param title
    #  The image title.
    ## @param caption
    #  The image caption.

    def __getHtmlImageBlock(self, gifImagePath, title, caption):
        block = ('@htmlonly\n'                      +\
                 '<div align="center">\n'           +\
                 '<p><strong>%s.</strong> %s</p>\n' +\
                 '<img src="%s" alt="%s">\n'        +\
                 '</div>\n'                         +\
                 '@endhtmlonly\n')                  %\
                 (title, caption, gifImagePath, gifImagePath)
        return block

    ## @brief Add to a specific page of the report a html-formatted image.
    ## @param self
    #  The class instance.
    ## @param gifImagePath
    #  The path to the actual gif image.
    ## @param title
    #  The image title.
    ## @param caption
    #  The image caption.
    ## @param pageLabel
    #  The page label.

    def addHtmlImage(self, gifImagePath, title = '', caption = '',\
                     pageLabel = MAIN_PAGE_LABEL):
        self.write(self.__getHtmlImageBlock(gifImagePath, title, caption),\
                   pageLabel)

    ## @brief Add to a specific page of the report an image (in both the html
    #  and the LaTeX version).
    ## @param self
    #  The class instance.
    ## @param gifImagePath
    #  The path to the actual gif image.
    ## @param epsImagePath
    #  The path to the actual eps image.
    ## @param title
    #  The image title.
    ## @param caption
    #  The image caption.
    ## @param pageLabel
    #  The page label.

    def addImage(self, gifImagePath, epsImagePath, title = '', caption = '',\
                 pageLabel = MAIN_PAGE_LABEL):
        self.addHtmlImage(gifImagePath, title, caption, pageLabel)
        self.addLaTeXImage(epsImagePath, title, caption, pageLabel)

    ## @brief Add a ROOT object (either histogram ot graph or whatever)
    #  to the report (both html and LaTeX versions).
    #
    #  The plot is first drawn on an auxiliary canvas (therefore the ROOT
    #  object must support the Draw() method) and it's then saved as image
    #  and put into the report.
    ## @param self
    #  The class instance.
    ## @param rootObject
    #  The plot to be added (TH1, TH2, TGraph, etc.).
    ## @param drawOptions
    #  The options for the Draw() method.
    ## @param title
    #  The image title.
    ## @param caption
    #  The image caption.
    ## @param xLog
    #  Flag to set the log scale on the x axis.
    ## @param yLog
    #  Flag to set the log scale on the y axis.
    ## @param pageLabel
    #  The page label.
 
    def addRootObject(self, rootObject , title = '', caption = '',\
                      drawOptions = '', xLog = False, yLog = False,\
                    pageLabel = MAIN_PAGE_LABEL):
        auxCanvasMissing = False
        if self.AuxRootCanvas is None:
            auxCanvasMissing = True
            logger.warn('Aux ROOT canvas needed to add a plot to the report.')
            self.createAuxRootCanvas()
            logger.info('Aux ROOT canvas created.')
        epsImageName = '%s.eps' % rootObject.GetName()
        gifImageName = '%s.gif' % rootObject.GetName()
        self.AuxRootCanvas.SetLogx(xLog)
        self.AuxRootCanvas.SetLogy(yLog)
        try:
            rootObject.Draw(drawOptions)
        except:
            logger.error('Could not draw %s.' % rootObject.GetName())
        self.AuxRootCanvas.SaveAs(os.path.join(self.LatexDirPath,epsImageName))
        self.AuxRootCanvas.SaveAs(os.path.join(self.HtmlDirPath, gifImageName))
        self.addImage(gifImageName, epsImageName, title, caption, pageLabel)
        if auxCanvasMissing:
            logger.info('Deleting aux ROOT canvas.')
            logger.warn('When saving multiple plots, you should probably ' +\
                        'create the aux ROOT canvas explicitly.')
            self.deleteAuxRootCanvas()

    ## @brief Return the representation of a pyhton list for the LaTeX report.
    ## @param self
    #  The class instance.
    ## @param name
    #  The list name appearing on the report.
    ## @param list
    #  The actual list.

    def __getLaTeXListBlock(self, name, list):
        block = ('@latexonly\n'              +\
                 '{\\bfseries %s}: %s\\\\\n' +\
                 '@endlatexonly\n\n')        %\
                 (name, list)
        return block

    ## @brief Return the representation of a pyhton list for the html report.
    ## @param self
    #  The class instance.
    ## @param name
    #  The list name appearing on the report.
    ## @param list
    #  The actual list.

    def __getHtmlListBlock(self, name, list):
        block = ('@htmlonly\n'         +\
                 '<b>%s</b>: %s<br>\n' +\
                 '@endhtmlonly\n')     %\
                 (name, list)
        return block

    ## @brief Write a python list to a specific page of the LaTeX report.
    ## @param self
    #  The class instance.
    ## @param name
    #  The list name appearing on the report.
    ## @param list
    #  The actual list.
    ## @param pageLabel
    #  The page label.

    def addLaTeXListBlock(self, name, list, pageLabel = MAIN_PAGE_LABEL):
        self.write(self.__getLaTeXListBlock(name, list), pageLabel)

    ## @brief Write a python list to a specific page of the html report.
    ## @param self
    #  The class instance.
    ## @param name
    #  The list name appearing on the report.
    ## @param list
    #  The actual list.
    ## @param pageLabel
    #  The page label.

    def addHtmlListBlock(self, name, list, pageLabel = MAIN_PAGE_LABEL):
        self.write(self.__getHtmlListBlock(name, list), pageLabel)

    ## @brief Add a pyhton list to a specific page of the (both LaTeX and
    #  html) report.
    ## @param self
    #  The class instance
    ## @param name
    #  The list name appearing on the report.
    ## @param list
    #  The actual list.
    ## @param pageLabel
    #  The page label.

    def addList(self, name, list, pageLabel = MAIN_PAGE_LABEL):
        self.addLaTeXListBlock(name, list, pageLabel)
        self.addHtmlListBlock(name, list, pageLabel)

    ## @brief Return the representation of a pyhton dictionary for the
    #  LaTeX report.
    ## @param self
    #  The class instance.
    ## @param name
    #  The dictionary name appearing on the report.
    ## @param dictionary
    #  The actual dictionary.

    def __getLaTeXDictBlock(self, name, dictionary):
        block = ('@latexonly\n'                  +\
                 '{\\bfseries %s}\n'             +\
                 '\\begin{itemize}\n')           %\
                 (name)
        for (key, value) in dictionary.items():
            block += '\\item{\\texttt %s}: %s\n' %\
                     (key, value)
        block += '\\end{itemize}\n'              +\
                 '@endlatexonly\n\n'
        return block

    ## @brief Return the representation of a pyhton dictionary for the
    #  html report.
    ## @param self
    #  The class instance.
    ## @param name
    #  The dictionary name appearing on the report.
    ## @param dictionary
    #  The actual dictionary.

    def __getHtmlDictBlock(self, name, dictionary):
        block = ('@htmlonly\n'               +\
                 '<b>%s</b>\n')              %\
                 (name)
        for (key, value) in dictionary.items():
            block += '<li><tt>%s</tt>: %s\n' %\
                     (key, value)
        block += '@endhtmlonly\n'
        return block

    ## @brief Write a python dictionary to a specific page of the LaTeX report.
    ## @param self
    #  The class instance.
    ## @param name
    #  The dictionary name appearing on the report.
    ## @param dictionary
    #  The actual dictionary.
    ## @param pageLabel
    #  The page label.

    def addLaTeXDictBlock(self, name, dictionary, pageLabel = MAIN_PAGE_LABEL):
        self.write(self.__getLaTeXDictBlock(name, dictionary), pageLabel)

    ## @brief Write a python dictionary to a specific page of the html report.
    ## @param self
    #  The class instance.
    ## @param name
    #  The dictionary name appearing on the report.
    ## @param dictionary
    #  The actual dictionary.
    ## @param pageLabel
    #  The page label.

    def addHtmlDictBlock(self, name, dictionary, pageLabel = MAIN_PAGE_LABEL):
        self.write(self.__getHtmlDictBlock(name, dictionary), pageLabel)

    ## @brief Add a pyhton dictionary to a specific page of the (both LaTeX
    #  and html) report.
    ## @param self
    #  The class instance
    ## @param name
    #  The list name appearing on the report.
    ## @param list
    #  The actual list.
    ## @param pageLabel
    #  The page label.

    def addDictionary(self, name, dictionary, pageLabel = MAIN_PAGE_LABEL):
        self.addLaTeXDictBlock(name, dictionary, pageLabel)
        self.addHtmlDictBlock(name, dictionary, pageLabel)

    ## @brief "Virtual" method to be overridden by the derived classes
    #  as to implement the actual generation of the reports.
    ## @param self
    #  The class instance.

    def run(self):
        print 'pBaseReportGenerator.run() not implemented, must be ' +\
              'overridden by the derived classes.'

    ## @brief Run doxygen on the main page.
    ## @param self
    #  The class instance.
    ## @param verbose
    #  If False (default), the usual doxygen output is masked to the user
    #  (meaning that, in case of errors, the system will just hang... the
    #  verbose option is indeed useful, in some cases).
    
    def doxygenate(self, verbose = False):
        logger.info('Running doxygen...')
        startTime = time.time()
        command = 'cd %s; doxygen %s' % (self.OutputDirPath,\
                                         self.CONFIG_FILE_NAME)
        if verbose:
            os.system(command)
        else:
            commands.getoutput(command)
        logger.info('Done in %.2f s.\n' % (time.time() - startTime))

    ## @brief Compile the LaTeX report and make ps and pdf files.
    ## @param self
    #  The class instance.
    ## @param verbose
    #  If False (default), the usual LaTeX output is masked to the user
    #  (meaning that, in case of errors, the system will just hang... the
    #  verbose option is indeed useful, in some cases).

    def compileLaTeX(self, verbose = False):
        logger.info('Compiling LaTeX report...')
        startTime = time.time()
        command = 'cd %s; make pdf' % self.LatexDirPath
        if verbose:
            os.system(command)
        else:
            commands.getoutput(command)
        logger.info('Done in %.2f s.\n' % (time.time() - startTime))

    ## @brief Compile the doxygen report and possibly the LaTeX output to
    #  produce the ps and pdf reports.
    ## @param self
    #  The class instance.
    ## @param compileLaTeX
    #  If True (default) the LaTeX report is compiled to ps and pdf.
        
    def compileReport(self, compileLaTeX = True):
        self.doxygenate()
        if compileLaTeX:
            self.compileLaTeX()


if __name__ == '__main__':
    TEST_LIST         = [1, 2, 3]
    TEST_DICT         = {'First key': 1, 'Second key': 2, 'Third key': 3}
    TEST_TABLE_HEADER = ['Column 1', 'Column 2', 'Column 3']
    TEST_TABLE_ROWS   = [[1, 2, 3], [4, 5, 6]]
    TEST_HISTOGRAM    = ROOT.TH1F('histogram', 'histogram', 100, -5, 5)
    TEST_HISTOGRAM.FillRandom('gaus')
    
    generator = pBaseReportGenerator('./report', 'Test report', 'Luca Baldini')
    generator.openReport()
    generator.addSection('listsanddicts', 'Lists and dictionaries')
    generator.addSubsection('lists', 'Python lists')
    generator.addList('Example list', TEST_LIST)
    generator.addSubsection('dicts', 'Python dictionaries')
    generator.addDictionary('Example dictionary', TEST_DICT)
    generator.addSection('tables', 'Tables')
    generator.addTable(TEST_TABLE_HEADER, TEST_TABLE_ROWS, 'Example table')
    generator.addSection('rootobjects', 'Root objects')
    generator.addRootObject(TEST_HISTOGRAM, 'Example histogram',\
                            'Histogram filled with random gaussian numbers.')
    generator.addPage('details', 'Detailed page')
    generator.closeReport()
    generator.compileReport()
