import pSafeLogger
logger = pSafeLogger.getLogger('pHistogramPair')

import os
import sys

from pSafeROOT  import ROOT


class pHistogramPair:

    def __init__(self, **kwargs):
        if kwargs.has_key('firstFile') and kwargs.has_key('secondFile') and \
           kwargs.has_key('histogramName'):
            self.FirstFile = kwargs['firstFile']
            self.SecondFile = kwargs['secondFile']
            self.FirstFileName = os.path.basename(self.FirstFile.GetPath())
            self.SecondFileName = os.path.basename(self.SecondFile.GetPath())
            self.FirstHistogram = self.FirstFile.Get(kwargs['histogramName'])
            self.SecondHistogram = self.SecondFile.Get(kwargs['histogramName'])
        elif kwargs.has_key('firstHisto') and kwargs.has_key('secondHisto'):
            self.FirstHistogram = kwargs['firstHisto']
            self.SecondHistogram = kwargs['secondHisto']
        else:
            sys.exit('Wrong keyword arguments to pHistogramPair. Abort.')
        self.DiffList = []
        self.ResidualsHistogram = None

    def delete(self):
        self.FirstHistogram.Delete()
        self.SecondHistogram.Delete()
        if self.ResidualsHistogram is not None:
            self.ResidualsHistogram.Delete()

    def getNumDifferences(self):
        return len(self.DiffList)

    def logDifference(self, difference):
        self.DiffList.append(difference)
        logger.error(difference)

    def compare(self, fullLog = False):
        numEntriesFirst  = self.FirstHistogram.GetEntries()
        numEntriesSecond = self.SecondHistogram.GetEntries()
        if numEntriesFirst != numEntriesSecond:
            self.logDifference('Number of entries (%d vs. %d)' %\
                               (numEntriesFirst, numEntriesSecond))
            if not fullLog:
                return
        numBinsFirst   = self.FirstHistogram.GetNbinsX()
        numBinsSecond  = self.SecondHistogram.GetNbinsX()
        numBins        = min(numBinsFirst, numBinsSecond)
        binWidthFirst  = self.FirstHistogram.GetBinWidth(1)
        binWidthSecond = self.SecondHistogram.GetBinWidth(1)
        xOffsetFirst   = 0
        xOffsetSecond  = 0
        xMinFirst      = self.FirstHistogram.GetBinLowEdge(0)
        xMinSecond     = self.SecondHistogram.GetBinLowEdge(0)
        if xMinFirst < xMinSecond:
            xOffsetSecond = int((xMinSecond - xMinFirst)/binWidthFirst)
        elif xMinFirst > xMinSecond:
            xOffsetFirst = int((xMinFirst - xMinSecond)/binWidthSecond)
        xOffset = max(xOffsetFirst, xOffsetSecond)
        for i in range(1 + xOffset, numBins + 1):
            binFirst  = i - xOffsetFirst
            binSecond = i - xOffsetSecond
            binCenterFirst  = self.FirstHistogram.GetBinCenter(binFirst)
            binCenterSecond = self.SecondHistogram.GetBinCenter(binSecond)
            if binCenterFirst != binCenterSecond:
                self.logDifference('Binning mismatch.')
                if not fullLog:
                    return
            valFirst   = self.FirstHistogram.GetBinContent(binFirst)
            valSecond = self.SecondHistogram.GetBinContent(binSecond)
            if valFirst != valSecond:
                self.logDifference('Content for bin %d (%.3f vs. %.3f)' %\
                                   (i, valFirst, valSecond))

    def createResidualsHistogram(self):
        try:
            self.ResidualsHistogram = self.FirstHistogram.Clone('Residuals')
            self.ResidualsHistogram.Add(self.SecondHistogram, -1)
        except:
            logger.error('Could not create residuals histogram.')

    def draw(self):
        self.FirstHistogram.SetLineColor(ROOT.kBlack)
        self.SecondHistogram.SetLineColor(ROOT.kRed)
        maxValue = max(self.FirstHistogram.GetMaximum(),\
                       self.SecondHistogram.GetMaximum())
        minValue = min(self.FirstHistogram.GetMinimum(),\
                       self.SecondHistogram.GetMinimum())
        self.FirstHistogram.SetMaximum(maxValue)
        self.SecondHistogram.SetMaximum(maxValue)
        self.FirstHistogram.SetMinimum(minValue)
        self.SecondHistogram.SetMinimum(minValue)
        self.SecondHistogram.Draw()
        ROOT.gPad.Update()
        statBox = self.SecondHistogram.GetListOfFunctions().FindObject("stats")
        statBox.SetX1NDC(statBox.GetX1NDC() - 1.1*ROOT.gStyle.GetStatW())
        statBox.SetX2NDC(statBox.GetX2NDC() - 1.1*ROOT.gStyle.GetStatW())
        statBox.SetTextColor(ROOT.kRed)
        self.FirstHistogram.Draw('sames')
        ROOT.gPad.Update()

    def drawResiduals(self):
        if self.ResidualsHistogram is None:
            self.createResidualsHistogram()
        self.ResidualsHistogram.Draw()
        ROOT.gPad.Update()



if __name__ == '__main__':
    h1 = ROOT.TH1F('h1', 'h1', 100, 0, 100)
    h2 = ROOT.TH1F('h2', 'h2', 100, 0, 100)
    h3 = ROOT.TH1F('h3', 'h3', 101, 0, 100)
    for i in range(100):
        h1.SetBinContent(i, i)
        h2.SetBinContent(i, i)
        h3.SetBinContent(i, i)
    pair1 = pHistogramPair(firstHisto = h1, secondHisto = h2)
    pair1.compare()
    print pair1.DiffList
    pair2 = pHistogramPair(firstHisto = h1, secondHisto = h3)
    pair2.compare()
    print pair2.DiffList
    h2.SetBinContent(59, 34)
    pair1.compare()
    print pair1.DiffList
    pair1.draw()
    raw_input('Press enter to continue...')
    pair1.drawResiduals()

