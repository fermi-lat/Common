#! /bin/env python

import os
import sys

from xml.dom     import minidom
from pXmlElement import pXmlElement
from pSafeROOT   import ROOT

class pXmlAlarmReader:

    def __init__(self, xmlFilePath, plotNamePattern, algorithmName):
        if os.path.exists(xmlFilePath):
            self.XmlDoc = minidom.parse(file(xmlFilePath))
        else:
            sys.exit('Input file %s not found. Exiting...' % xmlFilePath)
        self.PlotNamePattern = plotNamePattern
        self.AlgorithmName = algorithmName
        self.Histogram = None
        self.OutputList = []

    def parseFile(self):
        for plot in self.XmlDoc.getElementsByTagName('plot'):
            plotName = plot.getAttribute('name')
            if self.matchPattern(plotName, self.PlotNamePattern):
                plot = pXmlElement(plot)
                for alarm in plot.getElementsByTagName('alarm'):
                    if alarm.getAttribute('function') == self.AlgorithmName:
                        alarm = pXmlElement(alarm)
                        outputValue = alarm.evalTagValue('output')
                        print 'Output value for %s, %s: %.2f' %\
                            (plotName, self.AlgorithmName, outputValue)
                        self.OutputList.append(outputValue)

    def createHistogram(self, numBins = 10):
        xMin = min(self.OutputList)
        xMax = max(self.OutputList)
        xMin = 1
        xMax = 2
        histogramName = self.PlotNamePattern.replace('*', '')
        histogramTitle = self.PlotNamePattern.replace('*', '')
        self.Histogram = ROOT.TH1F(histogramName, histogramTitle,\
                                       numBins, xMin, xMax)
        self.Histogram.GetXaxis().SetTitle('Algorithm output value')
        self.Histogram.GetYaxis().SetTitle('Entries per bin')
        for value in self.OutputList:
            self.Histogram.Fill(value)
        self.Histogram.Draw()

    def matchPattern(self, plotName, pattern):
        patternPieces = pattern.split('*')
        for piece in patternPieces:
            plotName = plotName.replace(piece, '')
        if not plotName.isdigit():
            return False
        return True



if __name__ == '__main__':
    #filePath = '/data/work/isoc/opssim2/r0257835904_v000_reconEor.xml'
    filePath = '/data/work/isoc/opssim2/r0258175744_v000_reconEor.xml'
    #plotPattern = 'ReconAcdPhaMips_PMTA_Zoom_TH1_AcdTile_*'
    plotPattern = 'ReconEnergy_VeryLowEnergy_TH1_TowerCalLayerCalColumn_*_*_*'
    #algorithm = 'leftmost_edge'
    algorithm = 'x_min_bin'
    reader = pXmlAlarmReader(filePath, plotPattern, algorithm)
    reader.parseFile()
    reader.createHistogram()
    raw_input('Press enter to exit')
