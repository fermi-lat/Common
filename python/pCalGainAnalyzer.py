#! /bin/env python

import pSafeLogger
logger = pSafeLogger.getLogger('pCalGainAnalyzer')


import sys
import time

from pSafeROOT           import ROOT
from pRootFileManager    import pRootFileManager
from pAlarmBaseAlgorithm import pAlarmBaseAlgorithm


BASE_BRANCH_NAME  = 'CalXAdcPed_TH1_TowerCalLayerCalColumnFR'
FIT_RANGE_WIDTH   = 2.5
CAL_RANGE_DICT    = {0: 'LEX8', 1: 'LEX1', 2: 'HEX8', 3: 'HEX1'}
HISTOGRAMS_LABELS = ['Mean', 'RMS', 'ChiSquare', 'DOF', 'ReducedChiSquare']


class pCalGainAnalyzer(pRootFileManager, pAlarmBaseAlgorithm):

    def __init__(self, inputFilePath, outputFilePath):
        self.InputFilePath = inputFilePath
        self.OutputFilePath = outputFilePath
        self.ParamsDict = {}
        self.Gaussian = ROOT.TF1('cal_gain_gaussian', 'gaus')
        self.__createHistograms()

    def __createHistograms(self):
        self.HistogramsDict = {}
        for label in HISTOGRAMS_LABELS:
            self.HistogramsDict[label] = {}
            for (rangeIndex, rangeName) in CAL_RANGE_DICT.items():
                histogramName = 'CalXAdcPed%s_%s_TH1' % (label, rangeName)
                histogram = ROOT.TH1F(histogramName,\
                                      histogramName, 3072, -0.5, 3071.5)
                histogram.GetXaxis().SetTitle('Channel number (%s)' %\
                                              rangeName)
                histogram.GetYaxis().SetTitle(label)
                self.HistogramsDict[label][rangeIndex] = histogram

    def getHistogramChannel(self, tower, layer, column, face, range = None):
        if range is None:
            return tower*8*12*2 + layer*12*2 + column*2 + face
        else:
            return tower*8*12*2*4 + layer*12*2*4 + column*2*4 + face*4 + range

    def fitChannel(self, tower, layer, column, face, readoutRange):
        histogramName = '%s_%d_%d_%d_%d_%d' %\
               (BASE_BRANCH_NAME, tower, layer, column, face, readoutRange)
        self.RootObject = self.get(histogramName)
        if self.RootObject is None:
            sys.exit('Could not find %s. Abort.' % name)
        mean = self.RootObject.GetMean()
        rms = self.RootObject.GetRMS()
        self.ParamsDict['min'] = mean - FIT_RANGE_WIDTH*rms
        self.ParamsDict['max'] = mean + FIT_RANGE_WIDTH*rms
        (norm, mean, rms) = self.getFitParameters(self.Gaussian)
        chiSquare = self.Gaussian.GetChisquare()
        dof = self.Gaussian.GetNDF()
        try:
            reducedChiSquare = chiSquare/dof
        except ZeroDivisionError:
            reducedChiSquare = 0
        channel = self.getHistogramChannel(tower, layer, column, face)
        self.fillHistogram('Mean', readoutRange, channel, mean)
        self.fillHistogram('RMS', readoutRange, channel, rms)
        self.fillHistogram('ChiSquare', readoutRange, channel, chiSquare)
        self.fillHistogram('DOF', readoutRange, channel, dof)
        self.fillHistogram('ReducedChiSquare', readoutRange, channel,\
                           reducedChiSquare)
        self.RootObject.Delete()
        
    def fillHistogram(self, label, readoutRange, channel, value):
        self.HistogramsDict[label][readoutRange].Fill(channel, value)

    def run(self):
        logger.info('Starting CAL gain analysis...')
        startTime = time.time()
        self.openFile(inputFilePath)
        for tower in range(16):
            logger.debug('Fitting gains for tower %d...' % tower)
            for layer in range(8):
                for column in range(12):
                    for face in range(2):
                        for readoutRange in range(4):
                            self.fitChannel(tower, layer, column, face,\
                                            readoutRange)
        self.closeFile()
        elapsedTime = time.time() - startTime
        logger.info('Done in %.2f s.' % elapsedTime)
        self.writeOutputFile()

    def writeOutputFile(self):
        logger.info('Writing output file %s...' % self.OutputFilePath)
        outputFile = ROOT.TFile(self.OutputFilePath, 'RECREATE')
        for type in self.HistogramsDict.keys():
            for i in range(4):
                self.HistogramsDict[type][i].Write()
        outputFile.Close()
        logger.info('Done.')

    def drawHistograms(self):
        self.CanvasesDict = {}
        for label in HISTOGRAMS_LABELS:
            canvas = ROOT.TCanvas(label, label)
            canvas.Divide(2, 2)
            self.CanvasesDict[label] = canvas
            for i in range(4):
                self.CanvasesDict[label].cd(i + 1)
                self.HistogramsDict[label][i].Draw()
                self.CanvasesDict[label].Update()



if __name__ == '__main__':
    from optparse import OptionParser
    parser = OptionParser(usage = 'usage: %prog [options] filePath')
    parser.add_option('-o', '--output', dest = 'o',
                      default = None, type = str,
                      help = 'path to the output file')
    parser.add_option('-i', '--interactive', dest = 'i',
                      default = False, action = 'store_true',
                      help = 'run in interactive mode (show the plots)')
    (opts, args) = parser.parse_args()
    if len(args) != 1:
        parser.print_help()
        parser.error('Exactly one argument required.')
    inputFilePath = args[0]
    outputFilePath = opts.o
    if outputFilePath is None:
        outputFilePath = inputFilePath.replace('.root', '_output.root')
    analyzer = pCalGainAnalyzer(inputFilePath, outputFilePath)
    analyzer.run()
    if opts.i:
        analyzer.drawHistograms()
