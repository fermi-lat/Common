
import pSafeLogger
logger = pSafeLogger.getLogger('pCalBaseAnalyzer')

import sys
import time
import math

from pSafeROOT           import ROOT
from pRootFileManager    import pRootFileManager
from pAlarmBaseAlgorithm import pAlarmBaseAlgorithm


HISTOGRAM_GROUPS = ['Mean', 'RMS', 'ChiSquare', 'DOF', 'ReducedChiSquare']
GAUSSIAN = ROOT.TF1('gaussian', 'gaus')
HYPER_GAUSSIAN_FORMULA = '%s*[0]*exp(-(abs( (x-[1])/[2] )**[3])/2)' %\
                         (1.0/math.sqrt(2*math.pi))
HYPER_GAUSSIAN = ROOT.TF1('hyper_gaussian', HYPER_GAUSSIAN_FORMULA)
HYPER_GAUSSIAN_RMS_DICT  = {2 : 1.00000000000000000,
                            3 : 0.77044730829390562,
                            4 : 0.69190364639062063,
                            5 : 0.65497337224456775,
                            6 : 0.63418061567754813,
                            7 : 0.62090487573780351,
                            8 : 0.61251533816973947,
                            9 : 0.60609233201596469,
                            10: 0.60158429409781700,
                            11: 0.59830196288474891,
                            12: 0.59545136457909020,
                            13: 0.59363253699752849,
                            14: 0.59191057004935288,
                            15: 0.59013273872662664}
HYPER_GAUSSIAN_NORM_DICT = {2 : 1.0000005733034723,
                            3 : 1.1139741473603271,
                            4 : 1.162736634038237,
                            5 : 1.188314606937412,
                            6 : 1.2035708623129959,
                            7 : 1.2135029829388491,
                            8 : 1.2203908047360614,
                            9 : 1.2254005574337135,
                            10: 1.2291822069356093,
                            11: 1.2321229221337506,
                            12: 1.2344659238262117,
                            13: 1.236370789101618,
                            14: 1.2379460724714813,
                            15: 1.2392679120668064}



class pCalBaseAnalyzer(pRootFileManager, pAlarmBaseAlgorithm):

    def __init__(self, inputFilePath, outputFilePath, debug):
        self.InputFilePath = inputFilePath
        self.OutputFilePath = outputFilePath
        self.Debug = debug
        self.ParamsDict = {}
        self.HistogramsDict = {}
        if self.__class__.__name__ != 'pCalBaseAnalyzer':
            self.createHistograms()

    def getRmsCorrectionFactor(self):
        if self.FitFunction.GetName() == 'hyper_gaussian':
            exponent = self.FitFunction.GetParameter(3)
            try:
                return HYPER_GAUSSIAN_RMS_DICT[exponent]
            except KeyError:
                exponents = HYPER_GAUSSIAN_RMS_DICT.keys()
                exponents.sort()
                maxExponent = exponents[-1]
                return HYPER_GAUSSIAN_RMS_DICT[maxExponent]
        else:
            return 1

    def getNormCorrectionFactor(self):
        if self.FitFunction.GetName() == 'hyper_gaussian':
            sigma = self.FitFunction.GetParameter(2)
            exponent = self.FitFunction.GetParameter(3)
            try:
                return 1./(HYPER_GAUSSIAN_NORM_DICT[exponent]*sigma)
            except KeyError:
                exponents = HYPER_GAUSSIAN_RMS_DICT.keys()
                exponents.sort()
                maxExponent = exponents[-1]
                return 1./(HYPER_GAUSSIAN_RMS_DICT[maxExponent]*sigma)
        else:
            return 1

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
        normalization = binWidth*numEntries*self.getNormCorrectionFactor()
        self.FitFunction.SetParameter(0, normalization)
        self.FitFunction.SetParLimits(2, 0.8*self.RMS, 2.0*self.RMS)
        for i in range(self.NumFitIterations):
            self.ParamsDict['min'] = self.Mean - self.FitRangeWidth*self.RMS
            self.ParamsDict['max'] = self.Mean + self.FitRangeWidth*self.RMS 
            fitParameters = self.getFitParameters(self.FitFunction, 'QNB')
            (self.Mean, self.RMS) = fitParameters[1:3]
        self.RMS *= self.getRmsCorrectionFactor()
        self.ChiSquare = self.FitFunction.GetChisquare()
        self.DOF = self.FitFunction.GetNDF()
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
            print '*************************************************'
            print 'Debug information for %s (%d, %s, %s, %s, %s)' %\
                  (baseName, tower, layer, column, face, readoutRange)
            print 'Fit parameters    : %s' % fitParameters
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
