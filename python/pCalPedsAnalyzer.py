#! /bin/env python

from pBaseAnalyzer import *
from copy          import copy



class pCalPedsAnalyzer(pBaseAnalyzer):

    HISTOGRAM_GROUPS = copy(BASE_HISTOGRAM_GROUPS)
    HISTOGRAM_GROUPS += ['PedMeanDeviation', 'PedMeanDifference',
                         'PedRMSDifference', 'MeanDevDist']
    HISTOGRAM_SUB_GROUPS = ['LEX8', 'LEX1', 'HEX8', 'HEX1']
    CAL_RANGE_DICT = {0: 'LEX8', 1: 'LEX1', 2: 'HEX8', 3: 'HEX1'}
    CAL_RANGE_INVERSE_DICT = {'LEX8': 0, 'LEX1': 1, 'HEX8': 2, 'HEX1': 3}
    FIT_RANGE_LEFT_DICT  = {'LEX8': 2.5, 'LEX1': 3.0, 'HEX8': 2.5, 'HEX1': 3.0}
    FIT_RANGE_RIGHT_DICT = {'LEX8': 3.5, 'LEX1': 3.0, 'HEX8': 3.5, 'HEX1': 3.0}
    BASE_NAME = 'CalXAdcPed_TH1_TowerCalLayerCalColumnFR'
    HISTOGRAM_SETTINGS = {
        'MeanDist'            : (100,  0  , 1000 , 'Pedestal mean'),
        'MeanDevDist'         : (100,  -20, 20   , 'Pedestal deviation'),
        'RMSDist'             : (100,  0  , 10   , 'Pedestal RMS'),
        'ReducedChiSquareDist': (100,  0  , 80   , 'Reduced chi square'),
        'Default'             : (3072, 0  , 3072 , 'Channel number')
        }

    def __init__(self, inputFilePath, outputFilePath, debug):
        pBaseAnalyzer.__init__(self, inputFilePath, outputFilePath, debug)
        self.FitFunction = GAUSSIAN
        self.RebinningFactor = 1
        self.NumFitIterations = 1

    def createHistograms(self):
        for group in self.HISTOGRAM_GROUPS:
            for subgroup in self.HISTOGRAM_SUB_GROUPS:
                if group in self.HISTOGRAM_SETTINGS.keys():
                    key = group
                else:
                    key = 'Default'
                (nBins, xmin, xmax, xlabel) = self.HISTOGRAM_SETTINGS[key]
                ylabel = '%s (%s)' % (group, subgroup)
                name = self.getHistogramName(group, subgroup)
                self.HistogramsDict[name] = self.getNewHistogram(name, nBins,
                                                                 xmin, xmax,
                                                                 xlabel,
                                                                 ylabel)

    def getHistogramName(self, group, subgroup):
        return 'CalXAdcPed%s_%s_TH1' % (group, subgroup)

    def getChannelNumber(self, tower, layer, column, face,\
                         readoutRange = None):
        if readoutRange is None:
            return tower*8*12*2 + layer*12*2 + column*2 + face
        else:
            return tower*8*12*2*4 + layer*12*2*4 + column*2*4 + face*4 +\
                   readoutRange

    def getChannelName(self, baseName, tower, layer, column, face,\
                       readoutRange = None):
        if readoutRange is None:
            return '%s_%d_%d_%d_%d' % (baseName, tower, layer, column, face)
        else:
            return '%s_%d_%d_%d_%d_%d' % (baseName, tower, layer, column,\
                                          face, readoutRange)

    def fitChannel(self, baseName, tower, layer, column, face, readoutRange):
        key = self.CAL_RANGE_DICT[readoutRange]
        self.FitRangeLeft = self.FIT_RANGE_LEFT_DICT[key]
        self.FitRangeRight = self.FIT_RANGE_RIGHT_DICT[key]
        channelName = self.getChannelName(baseName, tower, layer, column,\
                                          face, readoutRange)
        if self.Debug:
            print '*************************************************'
            print 'Debug information for %s (%d, %s, %s, %s, %s)' %\
                  (baseName, tower, layer, column, face, readoutRange)
        self.fit(channelName)

    def inspectChannel(self, channel):
        self.openFile(self.InputFilePath)
        tower = channel/(8*12*2)
        layer = (channel - tower*8*12*2)/(12*2)
        column = (channel - tower*8*12*2 - layer*12*2)/2
        face = channel - tower*8*12*2 - layer*12*2 - column*2
        self.Debug = True
        for readoutRange in range(4):
            self.fitChannel(self.BASE_NAME, tower, layer, column, face,\
                            readoutRange)
        self.closeFile()

    def getTruncAvePedMean(self, subgroup, channel):
        return self.TruncPedMeanHistDict[subgroup].GetBinContent(channel + 1)

    def getTruncAvePedRMS(self, subgroup, channel):
        return self.TruncPedRMSHistDict[subgroup].GetBinContent(channel + 1)

    def getPedMeanReference(self, subgroup, channel):
        try:
            bin = channel*4 + self.CAL_RANGE_INVERSE_DICT[subgroup] + 1
            firstRef = self.PedMeanFirstRefHist.GetBinContent(bin)
            lastRef = self.PedMeanLastRefHist.GetBinContent(bin)
            if firstRef != lastRef:
                logger.warn('Pedestals changed during the run, averaging...')
                return (firstRef + lastRef)/2.0
            else:
                return firstRef
        except:
            logger.error('Could not get the ped. reference, returning 0.')
            return 0

    def fillHistograms(self, subgroup, channel):
        pBaseAnalyzer.fillHistograms(self, subgroup, channel)
        histName = self.getHistogramName('PedMeanDeviation', subgroup)
        valueDiff = self.Mean - self.getPedMeanReference(subgroup, channel)
        errorDiff = self.MeanError
        self.fillHistogram(histName, channel, valueDiff, errorDiff)
        histName = self.getHistogramName('MeanDevDist', subgroup)
        self.fillHistogram(histName, valueDiff)
        histName = self.getHistogramName('PedMeanDifference', subgroup)
        valueDiff = self.Mean - self.getTruncAvePedMean(subgroup, channel)
        errorDiff = self.MeanError
        self.fillHistogram(histName, channel, valueDiff, errorDiff)
        histName = self.getHistogramName('PedRMSDifference', subgroup)
        valueDiff = self.RMS - self.getTruncAvePedRMS(subgroup, channel)
        errorDiff = self.RMSError
        self.fillHistogram(histName, channel, valueDiff, errorDiff)

    def run(self):
        logger.info('Starting CAL peds analysis...')
        startTime = time.time()
        self.TruncPedMeanHistDict = {}
        self.TruncPedRMSHistDict = {}
        self.openFile(self.InputFilePath)
        for subgroup in self.HISTOGRAM_SUB_GROUPS:
            self.TruncPedMeanHistDict[subgroup] =\
                 self.get('CalXAdcPedMean_%s_TH1' % subgroup)
            self.TruncPedRMSHistDict[subgroup] =\
                 self.get('CalXAdcPedRMS_%s_TH1' % subgroup)
        self.PedMeanFirstRefHist = self.get('CalXPedDB_FirstVal_TH1')
        self.PedMeanLastRefHist = self.get('CalXPedDB_FirstVal_TH1')
        for tower in range(16):
            logger.debug('Fitting pedestals for tower %d...' % tower)
            for layer in range(8):
                for column in range(12):
                    for face in range(2):
                        for readoutRange in range(4):
                            self.fitChannel(self.BASE_NAME, tower, layer,\
                                            column, face, readoutRange)
                            chan = self.getChannelNumber(tower, layer, column,\
                                                         face)
                            subgroup = self.CAL_RANGE_DICT[readoutRange]
                            self.fillHistograms(subgroup, chan)
        elapsedTime = time.time() - startTime
        logger.info('Done in %.2f s.' % elapsedTime)
        self.writeOutputFile()
        self.closeFile()
        
    


if __name__ == '__main__':
    from optparse import OptionParser
    parser = OptionParser(usage = 'usage: %prog [options] filePath')
    parser.add_option('-o', '--output', dest = 'o',
                      default = None, type = str,
                      help = 'path to the output file')
    parser.add_option('-i', '--interactive', dest = 'i',
                      default = False, action = 'store_true',
                      help = 'run in interactive mode (show the plots)')
    parser.add_option('-d', '--debug', dest = 'd',
                      default = False, action = 'store_true',
                      help = 'run in debug mode (show the single chan. plots)')
    parser.add_option('-c', '--inspect-channel', dest = 'c',
                      default = -1, type = int,
                      help = 'inspect a single channel')
    (opts, args) = parser.parse_args()
    if len(args) != 1:
        parser.print_help()
        parser.error('Exactly one argument required.')
    inputFilePath = args[0]
    outputFilePath = opts.o
    analyzer = pCalPedsAnalyzer(inputFilePath, outputFilePath, opts.d)
    if opts.c >= 0:
        print 'About to inspect channel %d...' % opts.c
        analyzer.inspectChannel(opts.c)
    else:
        analyzer.run()
        if opts.i:
            analyzer.drawHistograms()
