#!/bin/env python

import pSafeLogger
logger = pSafeLogger.getLogger('pTreeProcessor')

import sys
import os
import time

from pXmlBaseParser       import pXmlBaseParser
from pBaseTreeProcessor   import pBaseTreeProcessor
from pBaseReportGenerator import pBaseReportGenerator
from pRootFileManager     import pRootFileManager


class pTreeProcessorXmlParser(pXmlBaseParser):

    def __init__(self, configFilePath = None):
        pXmlBaseParser.__init__(self, configFilePath)
        logger.info('Reading the output lists...')
        self.InputRootTreeName   = self.getInputRootTreeName()
        self.EnabledPlotLists    = self.getEnabledPlotLists()
        self.EnabledPlotRepsDict = {}
        for list in self.EnabledPlotLists:
            for (key, value) in list.EnabledPlotRepsDict.items():
                self.EnabledPlotRepsDict[key] = value
        logger.info('%d enabled plots found in the output lists.' %\
                    len(self.EnabledPlotRepsDict))


class pTreeProcessorReportGenerator(pBaseReportGenerator):

    MAIN_PAGE_TITLE = 'Tree processor monitor report'
    REPORT_AUTHOR   = 'Automatically generated by pTreeProcessor.py'

    def __init__(self, treeProcessor):
        self.TreeProcessor = treeProcessor
        self.RootFilePath  = self.TreeProcessor.OutputFilePath
        reportDirPath      = os.path.dirname(self.RootFilePath)
        reportDirPath      = os.path.join(reportDirPath, 'report')
        pBaseReportGenerator.__init__(self, reportDirPath)
        self.RootFileManager = pRootFileManager()

    def run(self, verbose = False, compileLaTeX = True):
        logger.info('Writing doxygen report files...')
        startTime = time.time()
        self.RootFileManager.openFile(self.RootFilePath)
        self.openReport()
        self.fillMainPage()
        self.createAuxRootCanvas(True, verbose)
        self.addPlots()
        self.deleteAuxRootCanvas()
        self.closeReport()
        self.RootFileManager.closeFile()
        logger.info('Done in %.2f s.\n' % (time.time() - startTime))
        self.compileReport(verbose, compileLaTeX)
        
    def fillMainPage(self):
        self.addSection('main_summary', 'Summary')
        self.write('@n Look at the related pages for details.')

    def addPlots(self):
        for list in self.TreeProcessor.XmlParser.EnabledPlotLists:
            self.addPlotList(list)

    ## There's a clear conflict with the FastMon stuff, here.
    ## To be fixed.

    def addPlotList(self, list):
        pageLabel = 'list_%s' % list.Name.replace(' ', '_')
        pageTitle = '%s plots list' % list.Name
        self.addPage(pageLabel, pageTitle)
        for plotRep in list.EnabledPlotRepsDict.values():
            self.addPlot(plotRep, plotRep.Name, pageLabel)



class pTreeProcessor(pBaseTreeProcessor):

    def __init__(self, xmlParser, inputFilePath, outputFilePath = None):
        rootTreeName = xmlParser.InputRootTreeName
        pBaseTreeProcessor.__init__(self, xmlParser, inputFilePath,\
                                    rootTreeName, outputFilePath)


if __name__ == '__main__':
    from optparse import OptionParser
    parser = OptionParser(usage='usage: %prog [options] data_file')
    parser.add_option('-c', '--config-file', dest='config_file',
                      default='../xml/config.xml', type=str,
                      help='path to the input xml configuration file')
    parser.add_option('-o', '--output-file', dest='output_file',
                      default=None, type=str,
                      help='path to the output xml file')
    parser.add_option('-r', '--create-report', action='store_true',
                      dest='create_report', default=False,
                      help='generate the report from the processed ROOT file')
    parser.add_option('-v', '--verbose', action='store_true',
                      dest='verbose', default=False,
                      help='print a lot of ROOT/doxygen/LaTeX related stuff')
    parser.add_option('-L', '--disable-LaTeX', action='store_true',
                      dest='disable_LaTeX', default=False,
                      help='do not compile the LaTeX version of the report')
    parser.add_option('-V', '--view-report', action='store_true',
                      dest='view_report', default=False,
                      help='view the report right after it has been generated')

    (options, args) = parser.parse_args()
    if len(args) != 1:
        parser.print_help()
        parser.error('incorrect number of arguments')
        sys.exit()
    if not os.path.isfile(args[0]):
        parser.error('first argument is not an existing file')
        sys.exit()
    if not os.path.isfile(options.config_file):
        parser.error('input configuration file (%s) not found'%\
                     (options.config_file))
        sys.exit()
           
    parser    = pTreeProcessorXmlParser(options.config_file)
    processor = pTreeProcessor(parser, args[0])
    processor.run()
    if options.create_report:
        reportGenerator = pTreeProcessorReportGenerator(processor)
        reportGenerator.run(options.verbose, options.disable_LaTeX)
        if options.view_report:
            reportGenerator.viewReport()
