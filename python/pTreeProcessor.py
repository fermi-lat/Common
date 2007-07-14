#!/bin/env python

import pSafeLogger
logger = pSafeLogger.getLogger('pTreeProcessor')

from pBaseTreeProcessor import pBaseTreeProcessor


class pTreeProcessor(pBaseTreeProcessor):

    def __init__(self, xmlParser, inputFilePath, outputFilePath = None):
        rootTreeName = xmlParser.InputRootTreeName
        pBaseTreeProcessor.__init__(self, xmlParser, inputFilePath,\
                                    rootTreeName, outputFilePath)


if __name__ == '__main__':
    from pTreeProcessorXmlParser import pTreeProcessorXmlParser
    parser    = pTreeProcessorXmlParser('sctest.xml')
    processor = pTreeProcessor(parser, 'SkimmedData_merit.root')
    processor.run()
