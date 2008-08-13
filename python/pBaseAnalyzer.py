
import pSafeLogger
logger = pSafeLogger.getLogger('pBaseAnalyzer')

import sys
import time
import math

from pSafeROOT           import ROOT
from pRootFileManager    import pRootFileManager
from pAlarmBaseAlgorithm import pAlarmBaseAlgorithm


HISTOGRAM_GROUPS = ['Mean', 'RMS', 'ChiSquare', 'DOF', 'ReducedChiSquare',
                    'FitProb', 'MeanDist', 'RMSDist', 'ReducedChiSquareDist']
GAUSSIAN = ROOT.TF1('gaussian', 'gaus')
HYPER_GAUSSIAN_FORMULA = '%s*[0]*exp(-(abs( (x-[1])/[2] )**[3])/2)' %\
                         (1.0/math.sqrt(2*math.pi))
HYPER_GAUSSIAN = ROOT.TF1('hyper_gaussian', HYPER_GAUSSIAN_FORMULA)


class pBaseAnalyzer(pRootFileManager, pAlarmBaseAlgorithm):

    def __init__(self, inputFilePath, outputFilePath, debug):
        self.InputFilePath = inputFilePath
        self.OutputFilePath = outputFilePath or \
                              inputFilePath.replace('.root', '_%s.root' %\
                                                    self.getAnalysisType())
        self.Debug = debug
        self.ParamsDict = {}
        self.HistogramsDict = {}
        if self.__class__.__name__ != 'pBaseAnalyzer':
            self.createHistograms()
        self.ExcludeMaximum = False

    def getAnalysisType(self):
        return self.__class__.__name__.replace('Analyzer', '')[1:]

    def getRmsCorrectionFactor(self):
        if self.FitFunction.GetName() == 'hyper_gaussian':
            exponent = self.FitFunction.GetParameter(3)
            return 0.573244 + 1.559419*(exponent**(-1.813875))
        else:
            return 1.0

    def getNormCorrectionFactor(self):
        if self.FitFunction.GetName() == 'hyper_gaussian':
            sigma = self.FitFunction.GetParameter(2)
            exponent = self.FitFunction.GetParameter(3)
            factor = 0.801328 + 0.693462*(exponent**(-1.781011))
            try:
                return factor/(sigma*self.getRmsCorrectionFactor())
            except ZeroDivisionError:
                return None
        else:
            return 1.0

    def getNewHistogram(self, name, numBins, xmin, xmax,\
                            xlabel = None, ylabel = None):
        histogram = ROOT.TH1F(name, name, numBins, xmin - 0.5, xmax - 0.5)
        if xlabel is not None:
            histogram.GetXaxis().SetTitle(xlabel)
        if ylabel is not None:
            histogram.GetYaxis().SetTitle(ylabel)
        return histogram

    def fixFitExponent(self, exponent):
        self.FitFunction.FixParameter(3, exponent)

    def getHistogram(self, group, subgroup):
        return self.HistogramsDict[self.getHistogramName(group, subgroup)]

    def fillHistogram(self, name, channel, value = None, error = 0.0):
        if value is not None:
            self.HistogramsDict[name].Fill(channel, value)
            self.HistogramsDict[name].SetBinError(channel, error)
        else:
            self.HistogramsDict[name].Fill(channel)

    def fillHistograms(self, subgroup, channel):
        self.fillHistogram(self.getHistogramName('Mean', subgroup),\
                           channel, self.Mean, self.MeanError)
        self.fillHistogram(self.getHistogramName('MeanDist', subgroup),\
                           self.Mean)
        self.fillHistogram(self.getHistogramName('RMS', subgroup),\
                           channel, self.RMS, self.RMSError)
        self.fillHistogram(self.getHistogramName('RMSDist', subgroup),\
                           self.RMS)
        self.fillHistogram(self.getHistogramName('ChiSquare', subgroup),\
                           channel, self.ChiSquare)
        self.fillHistogram(self.getHistogramName('DOF', subgroup),\
                           channel, self.DOF)
        self.fillHistogram(self.getHistogramName('ReducedChiSquare',\
                                                 subgroup),\
                           channel, self.ReducedChiSquare)
        self.fillHistogram(self.getHistogramName('ReducedChiSquareDist',\
                                                     subgroup),\
                               self.ReducedChiSquare)
        self.fillHistogram(self.getHistogramName('FitProb', subgroup),\
                           channel, self.FitProb)

    def fit(self, channelName):
        self.RootObject = self.get(channelName)
        if self.RootObject is None:
            sys.exit('Could not find %s. Abort.' % channelName)
        if self.RootObject.GetEntries() == 0:
            self.Mean = -1
            self.MeanError = 0
            self.RMS = -1
            self.RMSError = 0
            self.ChiSquare = -1
            self.DOF = -1
            self.ReducedChiSquare = -1
            self.FitProb = -1
            self.RootObject.Delete()
            return
        if self.RebinningFactor > 1:
            self.RootObject.Rebin(self.RebinningFactor)
        if self.ExcludeMaximum:
            maxBin = self.RootObject.GetMaximumBin()
            maxValue = self.RootObject.GetBinContent(maxBin)
            self.RootObject.SetBinError(maxBin, maxValue)
        self.Mean = self.RootObject.GetMean()
        self.RMS = self.RootObject.GetRMS()
        self.RootObject.GetXaxis().SetRangeUser(self.Mean - 10*self.RMS,
                                                self.Mean + 10*self.RMS)
        self.Mean = self.RootObject.GetMean()
        self.RMS = self.RootObject.GetRMS()
        self.FitFunction.SetParameter(1, self.Mean)
        self.FitFunction.SetParameter(2, self.RMS)
        self.FitFunction.SetParLimits(1, self.Mean - 0.5*self.RMS,\
                                      self.Mean + 0.5*self.RMS)
        binWidth = self.RootObject.GetBinWidth(1)
        numEntries = self.RootObject.GetEntries()
        try:
            normalization = binWidth*numEntries*self.getNormCorrectionFactor()
        except TypeError:
            logger.warn('Skipping zero division for channel %s.' % channelName)
            normalization = binWidth*numEntries
        self.FitFunction.SetParameter(0, normalization)
        self.FitFunction.SetParLimits(2, 0.8*self.RMS, 2.0*self.RMS)
        self.FitFunction.SetParLimits(2, 0, 10.0*self.RMS)
        if self.Debug:
            print 'Inititial par values: [%.4e, %.4e, %.4e]' %\
                  (normalization, self.Mean, self.RMS)
        for i in range(self.NumFitIterations):
            self.ParamsDict['min'] = self.Mean - self.FitRangeLeft*self.RMS
            self.ParamsDict['max'] = self.Mean + self.FitRangeRight*self.RMS
            if self.Debug:
                print 'Fitting in [%.4f, %.4f]' %\
                      (self.ParamsDict['min'], self.ParamsDict['max'])
            ([self.Mean, self.RMS], [self.MeanError, self.RMSError]) =\
                         self.getFitOutput(self.FitFunction, [1, 2])
        self.RMS *= self.getRmsCorrectionFactor()
        self.ChiSquare = self.FitFunction.GetChisquare()
        self.DOF = self.FitFunction.GetNDF()
        self.FitProb = ROOT.TMath.Prob(self.ChiSquare, self.DOF)
        try:
            self.ReducedChiSquare = self.ChiSquare/self.DOF
        except ZeroDivisionError:
            self.ReducedChiSquare = 0
        if self.Debug:
            self.RootObject.GetXaxis().SetRangeUser(self.Mean - 10*self.RMS,
                                                    self.Mean + 10*self.RMS)
            self.RootObject.Draw()
            self.FitFunction.Draw('same')
            ROOT.gPad.Update()
            print 'Fit parameters    : %s' % ['%.4e'%p for p in fitParameters]
            print 'Mean              : %s +- %s' % (self.Mean, self.MeanError)
            print 'RMS               : %s +- %s' % (self.RMS, self.RMSError)
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
        ROOT.gStyle.SetOptStat(111111)
        self.CanvasesDict = {}
        for group in HISTOGRAM_GROUPS:
            if len(self.HISTOGRAM_SUB_GROUPS) == 2:
                canvas = ROOT.TCanvas(group, group, 1000, 350)
                canvas.Divide(2, 1)
            else:
                canvas = ROOT.TCanvas(group, group, 1000, 700)
                canvas.Divide(2, 2)
            self.CanvasesDict[group] = canvas
            i = 1
            for subgroup in self.HISTOGRAM_SUB_GROUPS:
                canvas.cd(i)
                self.getHistogram(group, subgroup).Draw()
                canvas.Update()
                i+= 1


if __name__ == '__main__':
    f = NORM_HYPER_GAUSSIAN
    f.SetParameter(0, 1)
    f.SetParameter(1, 0)
    f.SetParameter(2, 0.1)
    for i in range(2, 10):
        f.SetParameter(3, i)
        f.Draw()
        ROOT.gPad.Update()
        print f.Integral(-10, 10)
