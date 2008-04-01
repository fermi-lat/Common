
import pSafeLogger
logger = pSafeLogger.getLogger('pCalBaseAnalyzer')

import sys
import time

from pSafeROOT           import ROOT
from pRootFileManager    import pRootFileManager
from pAlarmBaseAlgorithm import pAlarmBaseAlgorithm


HISTOGRAM_GROUPS = ['Mean', 'RMS', 'ChiSquare', 'DOF', 'ReducedChiSquare']



class pCalBaseAnalyzer(pRootFileManager, pAlarmBaseAlgorithm):

    def __init__(self, inputFilePath, outputFilePath, debug):
        self.InputFilePath = inputFilePath
        self.OutputFilePath = outputFilePath
        self.Debug = debug
        self.ParamsDict = {}
        self.RebinningFactor = 1
        self.FitRangeWidth = 1.5
        self.NumFitIterations = 1
        self.Gaussian = ROOT.TF1('cal_gain_gaussian', 'gaus')
        self.HistogramsDict = {}
        self.createHistograms()

    def getNewHistogram(self, name, numBins, xlabel = None, ylabel = None):
        histogram = ROOT.TH1F(name, name, numBins, -0.5, numBins - 0.5)
        if xlabel is not None:
            histogram.GetXaxis().SetTitle(xlabel)
        if ylabel is not None:
            histogram.GetYaxis().SetTitle(ylabel)
        return histogram

    def getHistogram(self, group, subgroup):
        return self.HistogramsDict[self.getHistogramName(group, subgroup)]

    def fillHistogram(self, name, channel, value):
        self.HistogramsDict[name].Fill(channel, value)

    def fillHistograms(self, subgroup, channel):
        self.fillHistogram(self.getHistogramName('Mean', subgroup),\
                           channel, self.Mean)
        self.fillHistogram(self.getHistogramName('RMS', subgroup),\
                           channel, self.RMS)
        self.fillHistogram(self.getHistogramName('ChiSquare', subgroup),\
                           channel, self.ChiSquare)
        self.fillHistogram(self.getHistogramName('DOF', subgroup),\
                           channel, self.DOF)
        self.fillHistogram(self.getHistogramName('ReducedChiSquare',\
                                                 subgroup),\
                           channel, self.ReducedChiSquare)

    def getChannelNumber(self, tower, layer, column, face = None,\
                         readoutRange = None):
        if face is None and readoutRange is None:
            return tower*8*12 + layer*12 + column 
        elif readoutRange is None:
            return tower*8*12*2 + layer*12*2 + column*2 + face
        else:
            return tower*8*12*2*4 + layer*12*2*4 + column*2*4 + face*4 +\
                   readoutRange

    def getChannelName(self, baseName, tower, layer, column, face = None,\
                       readoutRange = None):
        if face is None and readoutRange is None:
            return '%s_%d_%d_%d' % (baseName, tower, layer, column)
        elif readoutRange is None:
            return '%s_%d_%d_%d_%d' % (baseName, tower, layer, column, face)
        else:
            return '%s_%d_%d_%d_%d_%d' % (baseName, tower, layer, column,\
                                          face, readoutRange)

    def fitChannel(self, baseName, tower, layer, column, face = None,\
                   readoutRange = None):
        channelName = self.getChannelName(baseName, tower, layer, column,\
                                          face, readoutRange)
        self.RootObject = self.get(channelName)
        if self.RebinningFactor > 1:
            self.RootObject.Rebin(self.RebinningFactor)
        if self.RootObject is None:
            sys.exit('Could not find %s. Abort.' % name)
        self.Mean = self.RootObject.GetMean()
        self.RMS = self.RootObject.GetRMS()
        self.Gaussian.SetParLimits(1, self.Mean-self.RMS, self.Mean+self.RMS)
        self.Gaussian.SetParLimits(2, 0.5*self.RMS, 2*self.RMS)
        for i in range(self.NumFitIterations):
            self.ParamsDict['min'] = self.Mean - self.FitRangeWidth*self.RMS
            self.ParamsDict['max'] = self.Mean + self.FitRangeWidth*self.RMS 
            (self.Normalization, self.Mean, self.RMS) =\
                                 self.getFitParameters(self.Gaussian, 'QNB')
        self.ChiSquare = self.Gaussian.GetChisquare()
        self.DOF = self.Gaussian.GetNDF()
        try:
            self.ReducedChiSquare = self.ChiSquare/self.DOF
        except ZeroDivisionError:
            self.ReducedChiSquare = 0
        if self.Debug:
            self.RootObject.GetXaxis().SetRangeUser(self.Mean - 10*self.RMS,
                                                    self.Mean + 10*self.RMS)
            self.RootObject.Draw()
            self.Gaussian.Draw('same')
            ROOT.gPad.Update()
            print '*************************************************'
            print 'Debug information for %s (%d, %s, %s, %s, %s)' %\
                  (baseName, tower, layer, column, face, readoutRange)
            print 'Mean              : %s' % self.Mean
            print 'RMS               : %s' % self.RMS
            print 'Reduced Chi Square: %s/%s = %s' %\
                  (self.ChiSquare, self.DOF, self.ReducedChiSquare)
            print '*************************************************'
            answer = raw_input('Press enter to exit, q to quit...')
            if answer == 'q':
                sys.exit('Done')
        self.RootObject.Delete()

    def writeOutputFile(self):
        logger.info('Writing output file %s...' % self.OutputFilePath)
        outputFile = ROOT.TFile(self.OutputFilePath, 'RECREATE')
        for group in HISTOGRAM_GROUPS:
            for subgroup in self.HISTOGRAM_SUB_GROUPS:
                self.getHistogram(group, subgroup).Write()
        outputFile.Close()
        logger.info('Done.')

    def drawHistograms(self):
        self.CanvasesDict = {}
        for group in HISTOGRAM_GROUPS:
            canvas = ROOT.TCanvas(group, group)
            canvas.Divide(2, 2)
            self.CanvasesDict[group] = canvas
            i = 1
            for subgroup in self.HISTOGRAM_SUB_GROUPS:
                canvas.cd(i)
                self.getHistogram(group, subgroup).Draw()
                canvas.Update()
                i+= 1
