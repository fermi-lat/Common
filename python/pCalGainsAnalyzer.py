#! /bin/env python

from pBaseAnalyzer import *



class pCalGainsAnalyzer(pBaseAnalyzer):

    HISTOGRAM_SUB_GROUPS = ['RPM', 'RPp', 'RMm']
    REBIN_FACTORS_DICT   = {'RPM': 2  , 'RPp': 10 , 'RMm': 10 }
    FIT_RANGE_LEFT_DICT  = {'RPM': 3.0, 'RPp': 2.0, 'RMm': 2.0}
    FIT_RANGE_RIGHT_DICT = {'RPM': 3.0, 'RPp': 1.0, 'RMm': 1.0}
    FIT_EXPONENT_DICT    = {'RPM': 8.0, 'RPp': 2.0, 'RMm': 2.0}
    HISTOGRAM_SETTINGS = {
        'MeanDist'            : (100, 0, 10, 'Ratio mean'),
        'RMSDist'             : (100, 0, 10  , 'Ratio RMS'),
        'ReducedChiSquareDist': (100, 0, 15  , 'Reduced chi square'),
        'Default'             : (1536, 0, 1536, 'Channel number')
        }

    def __init__(self, inputFilePath, outputFilePath, debug):
        pBaseAnalyzer.__init__(self, inputFilePath, outputFilePath, debug)
        self.FitFunction = HYPER_GAUSSIAN
        self.NumFitIterations = 2
        
    def createHistograms(self):
        for group in HISTOGRAM_GROUPS:
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
                                                                 xlabel, ylabel)

    def getBaseName(self, subgroup):
        return '%s_TH1_TowerCalLayerCalColumn' % subgroup

    def getHistogramName(self, group, subgroup):
        return '%s_%s_TH1' % (subgroup, group)

    def setupFitParameters(self, subgroup):
        self.RebinningFactor = self.REBIN_FACTORS_DICT[subgroup]
        self.FitRangeRight = self.FIT_RANGE_RIGHT_DICT[subgroup]
        self.FitRangeLeft = self.FIT_RANGE_LEFT_DICT[subgroup]
        self.fixFitExponent(self.FIT_EXPONENT_DICT[subgroup])

    def getChannelNumber(self, tower, layer, column):
        return tower*8*12 + layer*12 + column 

    def getChannelName(self, baseName, tower, layer, column):
        return '%s_%d_%d_%d' % (baseName, tower, layer, column)

    def fitChannel(self, baseName, tower, layer, column):
        channelName = self.getChannelName(baseName, tower, layer, column)
        if self.Debug:
            print '*************************************************'
            print 'Debug information for %s (%d, %s, %s)' %\
                  (baseName, tower, layer, column)
        self.fit(channelName)

    def inspectChannel(self, channel):
        self.openFile(self.InputFilePath)
        tower = channel/(8*12)
        layer = (channel - tower*8*12)/12
        column = channel -tower*8*12 - layer*12
        self.Debug = True
        for subgroup in self.HISTOGRAM_SUB_GROUPS:
            baseName = self.getBaseName(subgroup)
            self.setupFitParameters(subgroup)
            self.fitChannel(baseName, tower, layer, column)
        self.closeFile()
            
    def run(self):
        logger.info('Starting CAL gains analysis...')
        startTime = time.time()
        self.openFile(self.InputFilePath)
        for tower in range(16):
            logger.debug('Fitting gains for tower %d...' % tower)
            for layer in range(8):
                for column in range(12):
                    for subgroup in self.HISTOGRAM_SUB_GROUPS:
                        baseName = self.getBaseName(subgroup)
                        self.setupFitParameters(subgroup)
                        self.fitChannel(baseName, tower, layer, column)
                        chan = self.getChannelNumber(tower, layer, column)
                        self.fillHistograms(subgroup, chan)
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
    analyzer = pCalGainsAnalyzer(inputFilePath, outputFilePath, opts.d)
    if opts.c >= 0:
        print 'About to inspect channel %d...' % opts.c
        analyzer.inspectChannel(opts.c)
    else:
        analyzer.run()
        if opts.i:
            analyzer.drawHistograms()
