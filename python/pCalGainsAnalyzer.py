#! /bin/env python

from pCalBaseAnalyzer import *



class pCalGainsAnalyzer(pCalBaseAnalyzer):

    HISTOGRAM_SUB_GROUPS = ['RPM', 'RPp', 'RMm']

    def __init__(self, inputFilePath, outputFilePath, debug):
        pCalBaseAnalyzer.__init__(self, inputFilePath, outputFilePath, debug)
        #self.Gaussian =\
        #     ROOT.TF1('Square', '[0]*(x>([1]-1.732*[2]))*(x<([1]+1.732*[2]))')
        self.RebinningFactor = 8
        self.FitRangeWidth = 3
        
    def createHistograms(self):
        for group in HISTOGRAM_GROUPS:
            for subgroup in self.HISTOGRAM_SUB_GROUPS:
                name = self.getHistogramName(group, subgroup)
                self.HistogramsDict[name] = self.getNewHistogram(name, 1536)

    def getBaseName(self, subgroup):
        return '%s_TH1_TowerCalLayerCalColumn' % subgroup

    def getHistogramName(self, group, subgroup):
        return '%s_%s_TH1' % (subgroup, group)

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
    (opts, args) = parser.parse_args()
    if len(args) != 1:
        parser.print_help()
        parser.error('Exactly one argument required.')
    inputFilePath = args[0]
    outputFilePath = opts.o
    if outputFilePath is None:
        outputFilePath = inputFilePath.replace('.root', '_output.root')
    analyzer = pCalGainsAnalyzer(inputFilePath, outputFilePath, opts.d)
    analyzer.run()
    if opts.i:
        analyzer.drawHistograms()
