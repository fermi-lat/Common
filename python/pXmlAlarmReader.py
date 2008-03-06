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
                        self.OutputList.append(outputValue)

    def createHistogram(self, numBins = 20):
        minValue = min(self.OutputList)
        maxValue = max(self.OutputList)
        valuesRange = maxValue - minValue
        minValue -= 2*valuesRange/float(numBins)
        maxValue += 2*valuesRange/float(numBins)
        histogramName = self.PlotNamePattern.replace('*', '')
        histogramTitle = self.PlotNamePattern.replace('*', '')
        self.Histogram = ROOT.TH1F(histogramName, histogramTitle,\
                                       numBins, minValue, maxValue)
        self.Histogram.GetXaxis().SetTitle('Algorithm output value')
        self.Histogram.GetYaxis().SetTitle('Entries per bin')
        for value in self.OutputList:
            self.Histogram.Fill(value)

    def drawHistogram(self):
        self.Histogram.Draw()

    def matchPattern(self, plotName, pattern):
        patternPieces = pattern.split('*')
        for piece in patternPieces:
            plotName = plotName.replace(piece, '')
        if not plotName.isdigit():
            return False
        return True



if __name__ == '__main__':
    from optparse import OptionParser 
    parser = OptionParser()
    parser.add_option('-p', '--pattern', dest = 'p',
                      default = None, type = str,
                      help = 'the patter matching the plot name')
    parser.add_option('-a', '--algorithm', dest = 'a',
                      default = None, type = str,
                      help = 'the name of the required algorithm')
    (opts, args) = parser.parse_args()
    if len(args) != 1:
        parser.print_help()
        parser.error('Exactly one argument required.')
    arg = args[0]
    if opts.p is None:
        parser.print_help()
        parser.error('Pattern to match plot names missing. Abort.')
    if opts.a is None:
        parser.print_help()
        parser.error('Algorithm name missing. Abort.')
    reader = pXmlAlarmReader(arg, opts.p, opts.a)
    reader.parseFile()
    reader.createHistogram()
    reader.drawHistogram()
    raw_input('Press enter to exit')
