## @package pBaseReportGenerator
## @brief Base package for autoamtic generation of test reports.
#
#  The basic strategy is to generate a set of doxygen pages which can
#  be automatically compiled to provide html output.
#  The following features are supported:
#  @li Multiple pages
#  @li Sections, subsections
#  @li Images (with the capability of producing png and eps files
#  directly from ROOT objects).
#  @li Tables
#  @li Formatted representation of python dictionaries.
#  @li Formatted representation of python lists.
#
#  @todo Add a reference mechanism to link objects (i.e. sections, tables,
#  images) within the report.

import pSafeLogger
logger = pSafeLogger.getLogger('pBaseReportGenerator')

import os
import sys
import commands
import time

import pUtils

from pSafeROOT import ROOT


## @brief Base class for automatic generation of test reports.

class pBaseReportGenerator:

    ## @var CONFIG_FILE_NAME
    ## @brief The name of the doxygen config file.

    ## @var MAIN_PAGE_LABEL
    ## @brief The label for the doxygen main page.

    ## @var HTML_DIR_NAME
    ## @brief The name of the html report directory.

    ## @var AUX_CANVAS_WIDTH
    ## @brief The width of the ROOT auxiliary canvas.

    ## @var AUX_CANVAS_HEIGHT
    ## @brief The height of the ROOT auxiliary canvas.

    ## @var MAIN_PAGE_TITLE
    ## @brief The title for the main page.

    ## @var REPORT_AUTHOR
    ## @brief The name of the report's author.

    CONFIG_FILE_NAME   = 'config.doxygen'
    MAIN_PAGE_LABEL    = 'mainpage'
    HTML_DIR_NAME      = 'html'
    AUX_CANVAS_WIDTH   = 650
    AUX_CANVAS_HEIGHT  = 400
    MAIN_PAGE_TITLE    = 'Main page'
    REPORT_AUTHOR      = 'Unknown'

    ## @brief Base constructor.
    ## @param self
    #  The class instance.
    ## @param outputDirPath
    #  The path to the directory in which the report must be created.
    #
    ## @param forceOverwrite
    #  If True (default) the output dir is overwritten without messages.
    
    def __init__(self, outputDirPath, forceOverwrite = True):

        ## @var OutputDirPath
        ## @brief The path to the output dir.

        ## @var ForceOverwrite
        ## @brief If True (default) overwrites existing folders without
        #  messages.

        ## @var HtmlDirPath
        ## @brief The path to the html report dir.

        ## @var ConfigFilePath
        ## @brief The path to the doxygen configuration file.

        ## @var DoxyFilesDict
        ## @brief Dictionary of doxygen files (one per page).

        ## @var AuxRootCanvas
        ## @brief Auxiliary ROOT canvas to draw ROOT objects on before they
        #  are included in the report as images.

        ## @var OutRootGuard
        ## @brief ROOT.TRedirectOutputGuard object used for redirecting the
        #  ROOT text output.
    
        self.OutputDirPath  = outputDirPath
        self.ForceOverwrite = forceOverwrite
        self.HtmlDirPath    = os.path.join(self.OutputDirPath,\
                                           self.HTML_DIR_NAME)
        self.ConfigFilePath = os.path.join(self.OutputDirPath,
                                           self.CONFIG_FILE_NAME)
        self.DoxyFilesDict  = {}
        self.AuxRootCanvas  = None
        self.OutRootGuard   = None

    ## @brief Create an auxiliary ROOT canvas to draw plots on.
    #
    #  Used for including in the report histograms and graphs from a ROOT file.
    ## @param self
    #  The class instance.
    ## @param batch
    #  If True (default) ROOT is set in batch mode for preventing the canvas
    #  from appearing on the screen.
    ## @param verbose
    #  If False (default) ROOT is prevented from printing informations on the
    #  screen while saving eps files.
    
    def createAuxRootCanvas(self, batch = True, verbose = False):
        if batch:
            self.disableRootGraphicsOutput()
        if self.AuxRootCanvas is None:
            self.AuxRootCanvas = ROOT.TCanvas('canvas', 'canvas',\
                                              self.AUX_CANVAS_WIDTH,\
                                              self.AUX_CANVAS_HEIGHT)

    ## @brief Delete the auxiliary ROOT canvas and put back ROOT in non-batch
    #  mode.
    ## @param self
    #  The class instance.

    def deleteAuxRootCanvas(self):
        if self.AuxRootCanvas is not None:
            self.AuxRootCanvas = None
        self.enableRootGraphicsOutput()

    ## @brief Set ROOT in batch mode.
    ## @param self
    #  The class instance.

    def disableRootGraphicsOutput(self):
        ROOT.gROOT.SetBatch(True)

    ## @brief Set ROOT in normal (graphics) mode.
    ## @param self
    #  The class instance.
        
    def enableRootGraphicsOutput(self):
        ROOT.gROOT.SetBatch(False)

    ## @brief Open the report.
    #
    #  Namely create the output directory structure and create the main page.
    ## @param self
    #  The class instance.

    def openReport(self):
        self.__createDirs()
        self.addPage(self.MAIN_PAGE_LABEL, self.MAIN_PAGE_TITLE)

    ## @brief Close the report.
    #
    #  Which means that the trailer is written and the files are closed.
    ## @param self
    #  The class instance.

    def closeReport(self):
        self.__writeTrailers()
        self.__closeDoxyFiles()

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

    ## @brief Create all the necessary output directories.
    ## @param self
    #  The class instance.
    
    def __createDirs(self):
        self.__createOutputDir()
        self.__createHtmlDir()

    ## @brief Open a generic file in write mode.
    ## @param self
    #  The class instance.
    ## @param filePath
    #  The file path.
    ## @param mode
    #  The open mode.

    def __openOutputFile(self, filePath, mode = 'w'):
        try:
            return file(filePath, mode)
        except:
            sys.exit('Could not open output file %s' % filePath)

    ## @brief Close all the opened doxygen files.
    
    def __closeDoxyFiles(self):
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

    def addPage(self, pageLabel, pageTitle):
        pageFileName = '%s.doxygen' % pageLabel.lower().replace(' ', '_')
        filePath = os.path.join(self.OutputDirPath, pageFileName)
        self.DoxyFilesDict[pageLabel] = self.__openOutputFile(filePath)
        self.__writePageHeader(pageLabel, pageTitle)
        if not os.path.exists(self.ConfigFilePath):
            configFile = self.__openOutputFile(self.ConfigFilePath)
            configFile.writelines('GENERATE_LATEX = NO\n')
            configFile.writelines('FILE_PATTERNS = %s '% pageFileName)
        else:
            configFile = self.__openOutputFile(self.ConfigFilePath, 'a')
            configFile.writelines('%s '% pageFileName)
        configFile.close()

    ## @brief Write a line to the doxygen main page file.
    ## @param self
    #  The class instance.
    ## @param line
    #  The ilne to be written.
    ## @param pageLabel
    #  The page label.

    def write(self, line, pageLabel = MAIN_PAGE_LABEL):
        self.DoxyFilesDict[pageLabel].writelines('%s\n' % line)

    ## @brief Write a carriage return to the doxygen main page file.
    ## @param self
    #  The class instance.
    ## @param pageLabel
    #  The page label.

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

    def __writePageHeader(self, pageLabel, pageTitle):
        if pageLabel == self.MAIN_PAGE_LABEL:
            header = '/** @%s %s\n' % (pageLabel, pageTitle) +\
                     '@htmlonly\n'                           +\
                     '<center>\n'                            +\
                     '</center>\n'                           +\
                     '@endhtmlonly\n'                        +\
                     '@author %s \n' % self.REPORT_AUTHOR    +\
                     '@date %s' % time.asctime()
        else:
            header = '/** @page %s %s' % (pageLabel, pageTitle)
        self.write(header, pageLabel)
        self.newline()

    ## @brief Write the trailers in the doxygen pages.
    ## @param self
    #  The class instance.

    def __writeTrailers(self):
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
        self.write('@htmlonly\n<br><br>\n@endhtmlonly')
        self.write('@section %s %s' % (label, title), pageLabel)
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
        self.write('@htmlonly\n<br>\n@endhtmlonly')
        self.write('@subsection %s %s' % (label, title), pageLabel)
        self.newline(pageLabel)

    ## @brief Return the header section for a html-formatted table.
    ## @param self
    #  The class instance.
    
    def getHtmlTableHeader(self):
        header = '@htmlonly\n'            +\
                 '<div align="center">\n' +\
                 '<table border="1", width="90%">'
        return header

    ## @brief Return the header row for a html-formatted table.
    ## @param self
    #  The class instance.
    ## @param items
    #  A python list containing the column labels.

    def getHtmlTableHeaderRow(self, items):
        return self.getHtmlTableRow(items, True)

    ## @brief Return a row for a html-formatted table.
    ## @param self
    #  The class instance.
    ## @param items
    #  A python list containing the row items.
    ## @param bold
    #  If True (not default) the content of the cell is displayed in bold.

    def getHtmlTableRow(self, items, bold = False):
        row = '<tr>\n'
        for item in items:
            row += '%s\n' % self.getHtmlTableCell(item, bold)
        row += '</tr>'
        return row

    ## @brief Return a cell for a html-formatted table.
    ## @param self
    #  The class instance.
    ## @param item
    #  The cell item.
    ## @param bold
    #  If True (not default) the content of the cell is displayed in bold.

    def getHtmlTableCell(self, item, bold = False):
        if not bold:
            return '<td>%s</td>' % item
        else:
            return '<td><b>%s</b></td>' % item

    ## @brief Return the trailer for a html-formatted table.
    ## @param self
    #  The class instance.
    ## @param title
    #  The table title.
    ## @param caption
    #  The table caption.

    def getHtmlTableTrailer(self, title, caption):
        trailer = '</table>\n'                                          +\
                  '<p><strong>%s.</strong> %s</p>\n' % (title, caption) +\
                  '</div>\n'                                            +\
                  '@endhtmlonly\n'
        return trailer

    ## @brief Write to a specific page of the report a html-formatted table.
    ## @param self
    #  The class instance.
    ## @param header
    #  A pyhton list of string representing the table header row.
    ## @param rows
    #  A pyhton list of lists of strings representing the actual rows.
    ## @param title
    #  The table title.
    ## @param caption
    #  The table caption.
    ## @param pageLabel
    #  The page label.

    def addHtmlTableBlock(self, header, rows, title = '', caption = '',\
                            pageLabel = MAIN_PAGE_LABEL):
        self.write(self.getHtmlTableHeader(), pageLabel)
        self.write(self.getHtmlTableHeaderRow(header), pageLabel)
        for row in rows:
            self.write(self.getHtmlTableRow(row), pageLabel)
        self.write(self.getHtmlTableTrailer(title, caption), pageLabel)

    ## @brief Write to a specific page of the report a table, formatted
    #  in html.
    ## @param self
    #  The class instance.
    ## @param header
    #  A pyhton list of string representing the table header row.
    ## @param rows
    #  A pyhton list of lists of strings representing the actual rows.
    ## @param title
    #  The table title.
    ## @param caption
    #  The table caption.
    ## @param pageLabel
    #  The page label.

    def addTable(self, header, rows, title = '', caption = '',\
                 pageLabel = MAIN_PAGE_LABEL):
        self.addHtmlTableBlock(header, rows, title, caption, pageLabel)

    ## @brief Return the doxygen block for adding a image to the html report.
    ## @param self
    #  The class instance.
    ## @param pngImagePath
    #  The path to the actual png image to be included. 
    ## @param title
    #  The image title.
    ## @param caption
    #  The image caption.

    def getHtmlImageBlock(self, pngImagePath, title, caption):
        block = '@htmlonly\n'                                              +\
                '<div align="center">\n'                                   +\
                '<img src="%s" alt="%s">\n' % (pngImagePath, pngImagePath) +\
                '<p><strong>%s.</strong><br/>%s</p>\n' % (title, caption)  +\
                '</div>\n'                                                 +\
                '@endhtmlonly'
        return block

    ## @brief Add to a specific page of the report a html-formatted image.
    ## @param self
    #  The class instance.
    ## @param pngImagePath
    #  The path to the actual png image.
    ## @param title
    #  The image title.
    ## @param caption
    #  The image caption.
    ## @param pageLabel
    #  The page label.print pageTitle

    def addHtmlImageBlock(self, pngImagePath, title = '', caption = '',\
                            pageLabel = MAIN_PAGE_LABEL):
        self.write(self.getHtmlImageBlock(pngImagePath, title, caption),\
                   pageLabel)

    ## @brief Add to a specific page of the report an image (in the html
    #  version).
    ## @param self
    #  The class instance.
    ## @param pngImagePath
    #  The path to the actual png image.
    ## @param title
    #  The image title.
    ## @param caption
    #  The image caption.
    ## @param pageLabel
    #  The page label.

    def addImage(self, pngImagePath, title = '', caption = '',\
                 pageLabel = MAIN_PAGE_LABEL):
        self.addHtmlImageBlock(pngImagePath, title, caption, pageLabel)

    ## @brief Add a ROOT object (either histogram ot graph or whatever)
    #  to the report (html version).
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
                      zLog = False, pageLabel = MAIN_PAGE_LABEL):
        logger.debug('Adding %s to the report...' % rootObject.GetName())
        self.createAuxRootCanvas()
        pngImageName = '%s.png' % rootObject.GetName()
        self.AuxRootCanvas.SetLogx(xLog)
        self.AuxRootCanvas.SetLogy(yLog)
        self.AuxRootCanvas.SetLogz(zLog)
        try:
            rootObject.Draw(drawOptions)
        except:
            logger.error('Could not draw %s.' % rootObject.GetName())
        self.AuxRootCanvas.SaveAs(os.path.join(self.HtmlDirPath, pngImageName))
        self.addImage(pngImageName, title, caption, pageLabel)
        self.deleteAuxRootCanvas()

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
    
    def addPlot(self, plotRep, name, pageLabel):
        rootObject = self.RootFileManager.get(name)
        if rootObject is not None:
            logger.debug('Adding %s to the report...' % rootObject.GetName())
            self.createAuxRootCanvas()
            pngImageName = '%s.png' % rootObject.GetName()
            self.AuxRootCanvas.SetLogx(plotRep.XLog)
            self.AuxRootCanvas.SetLogy(plotRep.YLog)
            self.AuxRootCanvas.SetLogz(plotRep.ZLog)
            try:
                plotRep.draw(rootObject)
            except:
                logger.error('Could not draw %s.' % name)
            self.AuxRootCanvas.SaveAs(os.path.join(self.HtmlDirPath,\
                                                   pngImageName))
            self.addImage(pngImageName, '%s (%s)' % (plotRep.Title, name),\
                          plotRep.Caption, pageLabel)
            self.deleteAuxRootCanvas()
        else:
            logger.error('Could not find %s.' % name)

    def addPlotsList(self, list):
        pageLabel = 'list_%s' % list.Name.replace(' ', '_')
        pageTitle = list.Name
        self.addPage(pageLabel, pageTitle)
        for plotRep in list.EnabledPlotRepsDict.values():
            for name in plotRep.getRootObjectsName():
                self.addPlot(plotRep, name, pageLabel)  

    ## @brief Return the representation of a pyhton list for the html report.
    ## @param self
    #  The class instance.
    ## @param name
    #  The list name appearing on the report.
    ## @param list
    #  The actual list.

    def getHtmlListBlock(self, name, list):
        block = ('@htmlonly\n'         +\
                 '<b>%s</b>: %s<br>\n' +\
                 '@endhtmlonly')       %\
                 (name, list)
        return block

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
        self.write(self.getHtmlListBlock(name, list), pageLabel)

    ## @brief Add a pyhton list to a specific page of the html report.
    ## @param self
    #  The class instance
    ## @param name
    #  The list name appearing on the report.
    ## @param list
    #  The actual list.
    ## @param pageLabel
    #  The page label.

    def addList(self, name, list, pageLabel = MAIN_PAGE_LABEL):
        self.addHtmlListBlock(name, list, pageLabel)

    ## @brief Return the representation of a pyhton dictionary for the
    #  html report.
    ## @param self
    #  The class instance.
    ## @param name
    #  The dictionary name appearing on the report.
    ## @param dictionary
    #  The actual dictionary.

    def getHtmlDictBlock(self, name, dictionary, anchor):
        block = '@htmlonly\n'
        if anchor is not None:
            block += '<a name = "%s"></a>\n' % anchor
        block += '<p><b>%s</b>\n' % (name)
        listOfKeys = dictionary.keys()
        listOfKeys.sort()
        for key in listOfKeys:
            value = dictionary[key]
            block += '<li><tt>%s</tt>: %s\n' % (key, value)
        block += '@endhtmlonly'
        return block

    ## @brief Write a python dictionary to a specific page of the html report.
    ## @param self
    #  The class instance.
    ## @param name
    #  The dictionary name appearing on the report.
    ## @param dictionary
    #  The actual dictionary.
    ## @param pageLabel
    #  The page label.

    def addHtmlDictBlock(self, name, dictionary, pageLabel, anchor):
        self.write(self.getHtmlDictBlock(name, dictionary, anchor),\
                   pageLabel)

    ## @brief Add a pyhton dictionary to a specific page of the html report.
    ## @param self
    #  The class instance
    ## @param name
    #  The dictionary name appearing on the report.
    ## @param dictionary
    #  The actual list.
    ## @param pageLabel
    #  The page label.

    def addDictionary(self, name, dictionary, pageLabel = MAIN_PAGE_LABEL,\
                      anchor = None):
        self.addHtmlDictBlock(name, dictionary, pageLabel, anchor)

    def getHtmlLinkBlock(self, text, address):
        return '<a href = "%s">%s</a>' % (address, text)

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

    ## @brief Compile the doxygen report.
    ## @param self
    #  The class instance.
    
    def compileReport(self, verbose = False):
        self.doxygenate(verbose)

    def viewReport(self):
        cmd = 'htmlview %s/index.html' % self.HtmlDirPath
        logger.info('Starting html viewer (%s)...' % cmd)
        out = commands.getoutput(cmd) 
        if out != '':
            logger.error('Wow... problems viewing the report!')
            print out


if __name__ == '__main__':
    TEST_LIST         = [1, 2, 3]
    TEST_DICT         = {'First key': 1, 'Second key': 2, 'Third key': 3}
    TEST_TABLE_HEADER = ['Column 1', 'Column 2', 'Column 3']
    TEST_TABLE_ROWS   = [[1, 2, 3], [4, 5, 6]]
    TEST_HISTOGRAM    = ROOT.TH1F('histogram', 'histogram', 100, -5, 5)
    TEST_HISTOGRAM.FillRandom('gaus')
    
    generator = pBaseReportGenerator('./testreport')
    generator.openReport()
    generator.addSection('listsanddicts', 'Lists and dictionaries')
    generator.addSubsection('lists', 'Python lists')
    generator.addList('Example list', TEST_LIST)
    generator.addSubsection('dicts', 'Python dictionaries')
    generator.addDictionary('Example dictionary', TEST_DICT)
    generator.addDictionary('Example dictionary', TEST_DICT)
    generator.addSection('tables', 'Tables')
    generator.addTable(TEST_TABLE_HEADER, TEST_TABLE_ROWS, 'Example table',\
                       'A very stupid table, actually.')
    generator.addSection('rootobjects', 'Root objects')
    generator.createAuxRootCanvas()
    generator.addRootObject(TEST_HISTOGRAM, 'Example histogram',\
                            'Histogram filled with random gaussian numbers.')
    generator.deleteAuxRootCanvas()
    generator.addPage('details', 'Detailed page')
    generator.closeReport()
    generator.compileReport()
    generator.viewReport()
