#! /bin/env python

from pBaseAnalyzer import *


class pAcdPedsAnalyzer(pBaseAnalyzer):

    HISTOGRAM_SUB_GROUPS = ['PMTA', 'PMTB']

    def __init__(self, inputFilePath, outputFilePath, debug):
        pBaseAnalyzer.__init__(self, inputFilePath, outputFilePath, debug)
        self.FitFunction = GAUSSIAN
        self.RebinningFactor = 1
        self.FitRangeWidth = 2.5
        self.NumFitIterations = 1

    def createHistograms(self):
        for group in HISTOGRAM_GROUPS:
            for subgroup in self.HISTOGRAM_SUB_GROUPS:
                name = self.getHistogramName(group, subgroup)
                self.HistogramsDict[name] =\
                     self.getNewHistogram(name, 128, 'Tile number', subgroup)

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

    def run(self):
        logger.info('Starting ACD peds analysis...')
        startTime = time.time()
        self.openFile(self.InputFilePath)
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
    if outputFilePath is None:
        outputFilePath = inputFilePath.replace('.root', '_output.root')
    analyzer = pAcdPedsAnalyzer(inputFilePath, outputFilePath, opts.d)
    if opts.c >= 0:
        print 'About to inspect channel %d...' % opts.c
        analyzer.inspectChannel(opts.c)
    else:
        analyzer.run()
        if opts.i:
            analyzer.drawHistograms()
