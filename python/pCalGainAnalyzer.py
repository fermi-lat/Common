#! /bin/env python

import pSafeLogger
logger = pSafeLogger.getLogger('pCalGainAnalyzer')


import sys
import time

from pSafeROOT           import ROOT
from pRootFileManager    import pRootFileManager
from pAlarmBaseAlgorithm import pAlarmBaseAlgorithm


BASE_BRANCH_NAME = 'CalXAdcPed_TH1_TowerCalLayerCalColumnFR'
FIT_RANGE_WIDTH  = 1.5
CAL_RANGE_DICT   = {0: 'LEX8', 1: 'LEX1', 2: 'HEX8', 3: 'HEX1'}



class pCalGainAnalyzer(pRootFileManager, pAlarmBaseAlgorithm):

    def __init__(self, inputFilePath, outputFilePath):
        self.InputFilePath = inputFilePath
        self.OutputFilePath = outputFilePath
        self.ParamsDict = {}
        self.Gaussian = ROOT.TF1('cal_gain_gaussian', 'gaus')
        self.__createHistograms()

    def __createHistograms(self):
        self.HistogramsDict = {'Mean': {}, 'RMS': {}}
        for type in self.HistogramsDict.keys():
            for (rIndex, rName) in CAL_RANGE_DICT.items():
                hname = 'CalXAdcPed%s_%s_TH1' % (type, rName)
                self.HistogramsDict[type][rIndex] =\
                                                  ROOT.TH1F(hname, hname,\
                                                            3072, -0.5, 3071.5)

    def getHistogramChannel(self, tower, layer, column, face, range = None):
        if range is None:
            return tower*8*12*2 + layer*12*2 + column*2 + face
        else:
            return tower*8*12*2*4 + layer*12*2*4 + column*2*4 + face*4 + range

    def fitHistogram(self, tower, layer, column, face, range):
        name = '%s_%d_%d_%d_%d_%d' %\
               (BASE_BRANCH_NAME, tower, layer, column, face, range)
        self.RootObject = self.get(name)
        if self.RootObject is None:
            sys.exit('Could not find %s. Abort.' % name)
        mean = self.RootObject.GetMean()
        rms = self.RootObject.GetRMS()
        self.ParamsDict['min'] = mean - FIT_RANGE_WIDTH*rms
        self.ParamsDict['max'] = mean + FIT_RANGE_WIDTH*rms
        (norm, mean, rms) = self.getFitParameters(self.Gaussian)
        channel = self.getHistogramChannel(tower, layer, column, face)
        self.HistogramsDict['Mean'][range].Fill(channel, mean)
        self.HistogramsDict['RMS'][range].Fill(channel, rms)

    def run(self):
        logger.info('Starting CAL gain analysis...')
        startTime = time.time()
        self.openFile(inputFilePath)
        for t in range(16):
            logger.debug('Fitting gains for tower %d...' % t)
            for l in range(8):
                for c in range(12):
                    for f in range(2):
                        for r in range(4):
                            self.fitHistogram(t, l, c, f, r)
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
        self.CanvasesDict['Mean'] = ROOT.TCanvas('Mean', 'Mean')
        self.CanvasesDict['RMS']  = ROOT.TCanvas('RMS', 'RMS')
        for canvas in self.CanvasesDict.values():
            canvas.Divide(2, 2)
        for type in self.HistogramsDict.keys():
            for i in range(4):
                self.CanvasesDict[type].cd(i + 1)
                self.HistogramsDict[type][i].Draw()
                self.CanvasesDict[type].Update()



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
