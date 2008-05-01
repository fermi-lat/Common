#! /bin/env python

import os
import sys

import pSafeLogger
logger = pSafeLogger.getLogger('pXmlAlarmPostProcessor')

from pXmlBaseParser  import pXmlBaseParser
from pXmlBaseElement import pXmlBaseElement
from pXmlAlarmReader import pXmlAlarmReader
from pSafeROOT       import ROOT

MIN_NUM_BINS = 10
MAX_NUM_BINS = 1000


class pAlarmPostProcessorInstance:

    def __init__(self, plotName, algorithmName, xmin, xmax, numBins,\
                 undefinedValue):
        self.PlotName = plotName
        self.AlgorithmName = algorithmName
        self.UndefinedValue = undefinedValue
        self.OutputValues = []
        self.Histogram = ROOT.TH1F(self.PlotName.replace('_*', ''),
                                   self.PlotName.replace('_*', ''),
                                   numBins, xmin, xmax)
        self.Histogram.GetXaxis().SetTitle('Algorithm output value')
        self.Histogram.GetYaxis().SetTitle('Entries per bin')

    def matchPattern(self, plotName, pattern):
        patternPieces = pattern.split('*')
        for piece in patternPieces:
            plotName = plotName.replace(piece, '')
        if not plotName.isdigit():
            return False
        return True

    def fillOutputValues(self, xmlDoc):
        logger.info('Retrieving output values...')
        self.OutputValues = []
        numMatches = 0
        numValidOutputs = 0
        for plotElement in xmlDoc.getElementsByTagName('plot'):
            plotName = plotElement.getAttribute('name')
            if self.matchPattern(plotName, self.PlotName):
                plotElement = pXmlBaseElement(plotElement)
                for alarmElement in plotElement.getElementsByTagName('alarm'):
                    if alarmElement.getAttribute('function') ==\
                           self.AlgorithmName:
                        numMatches += 1
                        alarmElement = pXmlBaseElement(alarmElement)
                        outputValue = alarmElement.evalTagValue('output')
                        if outputValue is not None:
                            numValidOutputs += 1
                            self.OutputValues.append(outputValue)
                        else:
                            self.OutputValues.append(self.UndefinedValue)
        logger.info('Found %d valid output values out of %d matches.' %\
                    (numValidOutputs, numMatches))

    def fillHistogram(self):
        logger.info('Filling output histogram...')
        for value in self.OutputValues:
            self.Histogram.Fill(value)


class pAlarmPostProcessorXmlParser(pXmlBaseParser):

    def __init__(self, xmlConfigFilePath):
        pXmlBaseParser.__init__(self, xmlConfigFilePath)
        self.Instances = []
        for element in self.XmlDoc.getElementsByTagName('alarmSet'):
            element = pXmlBaseElement(element)
            plotName = element.getAttribute('name')
            algorithmName = element.getAttribute('algorithm')
            xmin = element.evalTagValue('xmin', 0)
            xmax = element.evalTagValue('xmax', 1)
            numBins = element.evalTagValue('xbins', 100)
            undefinedValue = element.evalTagValue('undefined_value', -1)
            instance = pAlarmPostProcessorInstance(plotName, algorithmName,
                                                   xmin, xmax, numBins,
                                                   undefinedValue)
            self.Instances.append(instance)
            

class pAlarmPostProcessor(pXmlBaseParser):

    def __init__(self, xmlInputFilePath, xmlConfigFilePath):
        pXmlBaseParser.__init__(self, xmlInputFilePath)
        self.XmlParser = pAlarmPostProcessorXmlParser(xmlConfigFilePath)
        for instance in self.XmlParser.Instances:
            self.processInstance(instance)

    def processInstance(self, instance):
        logger.info('Processing instance %s, algorithm %s...' %\
                    (instance.PlotName, instance.AlgorithmName))
        instance.fillOutputValues(self.XmlDoc)
        instance.fillHistogram()

    def writeOutputFile(self, outputFilePath):
        logger.info('Writing output file %s...' % outputFilePath)
        outputFile = ROOT.TFile(outputFilePath, 'RECREATE')
        for instance in self.XmlParser.Instances:
            instance.Histogram.Write()
        outputFile.Close()
        logger.info('Done.')





if __name__ == '__main__':
    from pOptionParser import pOptionParser
    optparser = pOptionParser('co', 1, 1, False)
    if optparser.Options.c is None:
        optparser.error('Specify a xml configuration file.')
    if optparser.Options.o is None:
        optparser.error('Specify the output file path.')
    postProcessor = pAlarmPostProcessor(optparser.Argument,\
                                        optparser.Options.c)
    postProcessor.writeOutputFile(optparser.Options.o)
