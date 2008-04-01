#! /bin/env python

from pCalBaseAnalyzer import *



class pCalPedsAnalyzer(pCalBaseAnalyzer):

    HISTOGRAM_SUB_GROUPS = ['LEX8', 'LEX1', 'HEX8', 'HEX1']
    CAL_RANGE_DICT = {0: 'LEX8', 1: 'LEX1', 2: 'HEX8', 3: 'HEX1'}
    BASE_NAME = 'CalXAdcPed_TH1_TowerCalLayerCalColumnFR'

    def createHistograms(self):
        for group in HISTOGRAM_GROUPS:
            for subgroup in self.HISTOGRAM_SUB_GROUPS:
                name = self.getHistogramName(group, subgroup)
                self.HistogramsDict[name] = self.getNewHistogram(name, 3072)

    def getHistogramName(self, group, subgroup):
        return 'CalXAdcPed%s_%s_TH1' % (group, subgroup)

    def run(self):
        logger.info('Starting CAL peds analysis...')
        startTime = time.time()
        self.openFile(self.InputFilePath)
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
    (opts, args) = parser.parse_args()
    if len(args) != 1:
        parser.print_help()
        parser.error('Exactly one argument required.')
    inputFilePath = args[0]
    outputFilePath = opts.o
    if outputFilePath is None:
        outputFilePath = inputFilePath.replace('.root', '_output.root')
    analyzer = pCalPedsAnalyzer(inputFilePath, outputFilePath)
    analyzer.run()
    if opts.i:
        analyzer.drawHistograms()
