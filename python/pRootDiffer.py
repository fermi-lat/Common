#! /usr/bin/env python

import pSafeLogger
logger = pSafeLogger.getLogger('pRootDiffer')

import os
import sys

from pSafeROOT        import ROOT
from pXmlWriter       import pXmlWriter
from pHistogramPair   import pHistogramPair
from pRootFileManager import pRootFileManager



class pRootDiffer:

    def __init__(self, firstFilePath, secondFilePath):
        self.FirstFileManager = pRootFileManager(firstFilePath)
        self.SecondFileManager = pRootFileManager(secondFilePath)
        self.DiffDict = {}

    def getNumDifferences(self):
        numDifferences = 0
        for diffList in self.DiffDict.values():
            numDifferences += len(diffList)
        return numDifferences

    def getNumPlots(self):
        return len(self.DiffDict)

    def getNumDiffPlots(self):
        numDiffPlots = 0
        for diffList in self.DiffDict.values():
            if len(diffList) > 0:
                numDiffPlots += 1
        return numDiffPlots

    def run(self, interactive = False):
        if interactive:
            self.Canvas = ROOT.TCanvas('Diff', 'Diff', 1000, 600)
            self.Canvas.Divide(2, 1)
            self.Canvas.Update()
        for (name, first) in self.FirstFileManager.getPlotsDict().items():
            if name in self.SecondFileManager.getPlotsDict().keys():
                second = self.SecondFileManager.getPlotsDict()[name]
                logger.debug('Comparing %s...' % name)
                pair = pHistogramPair(firstHisto = first, secondHisto = second)
                pair.compare()
                self.DiffDict[name] = pair.DiffList
                if interactive:
                    self.Canvas.cd(1); pair.draw()
                    self.Canvas.cd(2); pair.drawResiduals()
                    a = raw_input('Press enter to continue, q to quit...')
                    if a == 'q':
                        sys.exit('Done')
        logger.info('%d histogram pair(s) compared.' % self.getNumPlots())
        logger.info('Number of histograms with differences: %d' %\
                    self.getNumDiffPlots())
        logger.info('Total number of differences: %d' %\
                    self.getNumDifferences())

    def writeXmlSummary(self, filePath):
        logger.info('Writing summary xml file...')
        xmlWriter  = pXmlWriter(filePath)
        xmlWriter.openTag('differences')
        xmlWriter.indent()
        xmlWriter.newLine()
        xmlWriter.openTag('summary')
        xmlWriter.indent()
        xmlWriter.writeTag('numPlots', {}, self.getNumPlots())
        xmlWriter.writeTag('numDiffPlots', {}, self.getNumDiffPlots())
        xmlWriter.writeTag('numDifferences', {}, self.getNumDifferences())
        xmlWriter.backup()
        xmlWriter.closeTag('summary')
        xmlWriter.newLine()
        xmlWriter.openTag('details')
        xmlWriter.indent()
        for (histogramName, diffList) in self.DiffDict.items():
            if len(diffList):
                xmlWriter.openTag('plot', {'name': histogramName})
                xmlWriter.indent()
                for diff in diffList:
                    xmlWriter.writeTag('difference', {'detail': diff})
                xmlWriter.backup()
                xmlWriter.closeTag('plot')
        xmlWriter.backup()
        xmlWriter.closeTag('details')
        xmlWriter.backup()
        xmlWriter.newLine()
        xmlWriter.closeTag('differences')
        xmlWriter.closeFile()
        logger.info('Done.')


if __name__ == '__main__':
    from optparse import OptionParser
    parser = OptionParser(usage = 'usage: %prog [options] file1 file2')
    parser.add_option('-i', '--interactive', dest = 'i',
                      default = False, action = 'store_true',
                      help = 'run in interactive mode (show the plots)')
    parser.add_option('-o', '--output', dest = 'o',
                      default = None, type = str,
                      help = 'path to the output xml summary file')    
    (opts, args) = parser.parse_args()
    if len(args) != 2:
        parser.print_help()
        parser.error('Exactly two arguments required.')
    (firstFilePath, secondFilePath) = args        
    differ = pRootDiffer(firstFilePath, secondFilePath)
    differ.run(opts.i)
    if opts.o is not None:
        differ.writeXmlSummary(opts.o)


