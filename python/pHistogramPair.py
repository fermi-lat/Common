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

    def compare(self):
        numFirstBins = self.FirstHistogram.GetNbinsX()
        numSecondBins = self.SecondHistogram.GetNbinsX()
        if numFirstBins == numSecondBins:
            numBins = numFirstBins
        else:
            diff = 'Number of bins (%d vs. %d)' % (numFirstBins, numSecondBins)
            logger.error(diff)
            self.DiffList.append(diff)
            return
        for i in range(1, numBins + 1):
            firstVal = self.FirstHistogram.GetBinContent(i)
            secondVal = self.SecondHistogram.GetBinContent(i)
            if firstVal != secondVal:
                diff = 'Content for bin %d (%.3f vs. %.3f)' % (i, firstVal,
                                                               secondVal)
                self.DiffList.append(diff)

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

