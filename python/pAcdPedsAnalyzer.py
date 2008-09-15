#! /bin/env python

from pBaseAnalyzer import *
from copy          import copy



class pAcdPedsAnalyzer(pBaseAnalyzer):

    HISTOGRAM_GROUPS = copy(BASE_HISTOGRAM_GROUPS)
    HISTOGRAM_GROUPS += ['PedMeanDeviation', 'PedMeanDifference',
                         'PedRMSDifference']
    HISTOGRAM_SUB_GROUPS = ['PMTA', 'PMTB']
    HISTOGRAM_SETTINGS = {
        'MeanDist'            : (100, 0, 1000, 'Pedestal mean'),
        'RMSDist'             : (100, 0, 10  , 'Pedestal RMS'),
        'ReducedChiSquareDist': (100, 0, 80  , 'Reduced chi square'),
        'Default'             : (128, 0, 128 , 'Tile number')
        }

    def __init__(self, inputFilePath, outputFilePath, debug):
        pBaseAnalyzer.__init__(self, inputFilePath, outputFilePath, debug)
        self.FitFunction = GAUSSIAN
        self.RebinningFactor = 1
        self.FitRangeLeft = 1.5
        self.FitRangeRight = 2.0
        self.NumFitIterations = 2

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
        return 'AcdPed%s_%s_TH1' % (group, subgroup)

    def getBaseName(self, subgroup):
        return 'ACD_Ped_%s_LowRange_TH1_AcdTile' % subgroup

    def getChannelName(self, tile, subgroup):
        return '%s_%d' % (self.getBaseName(subgroup), tile)

    def fitChannel(self, tile, subgroup):
        baseName = self.getBaseName(subgroup)
        channelName = self.getChannelName(tile, subgroup)
        if self.Debug:
            print '*************************************************'
            print 'Debug information for %s (%d, %s)' % (baseName, tile,\
                                                         subgroup)
        self.fit(channelName)

    def inspectChannel(self, channel):
        self.openFile(self.InputFilePath)
        self.Debug = True
        for subgroup in self.HISTOGRAM_SUB_GROUPS:
            self.fitChannel(channel, subgroup)
        self.closeFile()

    def getTruncAvePedMean(self, subgroup, channel):
        return self.TruncPedMeanHistDict[subgroup].GetBinContent(channel + 1)

    def getTruncAvePedRMS(self, subgroup, channel):
        return self.TruncPedRMSHistDict[subgroup].GetBinContent(channel + 1)

    def getPedMeanReference(self, subgroup, channel):
        try:
            bin = channel + 1
            firstRef =\
                     self.PedMeanFirstRefHistDict[subgroup].GetBinContent(bin)
            lastRef = self.PedMeanLastRefHistDict[subgroup].GetBinContent(bin)
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
        histName = self.getHistogramName('PedMeanDifference', subgroup)
        valueDiff = self.Mean - self.getTruncAvePedMean(subgroup, channel)
        errorDiff = self.MeanError
        self.fillHistogram(histName, channel, valueDiff, errorDiff)
        histName = self.getHistogramName('PedRMSDifference', subgroup)
        valueDiff = self.RMS - self.getTruncAvePedRMS(subgroup, channel)
        errorDiff = self.RMSError
        self.fillHistogram(histName, channel, valueDiff, errorDiff)

    def run(self):
        logger.info('Starting ACD peds analysis...')
        startTime = time.time()
        self.TruncPedMeanHistDict = {}
        self.TruncPedRMSHistDict = {}
        self.PedMeanFirstRefHistDict = {}
        self.PedMeanLastRefHistDict = {}
        self.openFile(self.InputFilePath)
        for subgroup in self.HISTOGRAM_SUB_GROUPS:
            self.TruncPedMeanHistDict[subgroup] =\
                 self.get('ACD_PedMean_%s_LowRange_TH1' % subgroup)
            self.TruncPedRMSHistDict[subgroup] =\
                 self.get('ACD_PedRMS_%s_LowRange_TH1' % subgroup)
            self.PedMeanFirstRefHistDict[subgroup] =\
                 self.get('AcdPedDB_%s_FirstVal_TH1' % subgroup)
            self.PedMeanLastRefHistDict[subgroup] =\
                 self.get('AcdPedDB_%s_LastVal_TH1' % subgroup)
        for tile in range(128):
            for subgroup in self.HISTOGRAM_SUB_GROUPS:
                self.fitChannel(tile, subgroup)
                self.fillHistograms(subgroup, tile)
        self.closeFile()
        elapsedTime = time.time() - startTime
        logger.info('Done in %.2f s.' % elapsedTime)
        self.writeOutputFile()



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
    analyzer = pAcdPedsAnalyzer(inputFilePath, outputFilePath, opts.d)
    if opts.c >= 0:
        print 'About to inspect channel %d...' % opts.c
        analyzer.inspectChannel(opts.c)
    else:
        analyzer.run()
        if opts.i:
            analyzer.drawHistograms()
