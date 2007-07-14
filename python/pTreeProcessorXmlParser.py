import pSafeLogger
logger = pSafeLogger.getLogger('pXmlParser')

import sys
import os
import time

from pXmlBaseParser import pXmlBaseParser


class pTreeProcessorXmlParser(pXmlBaseParser):

    def __init__(self, configFilePath = None):
        pXmlBaseParser.__init__(self, configFilePath)
        logger.info('Reading the output lists...')
        self.InputRootTreeName   = self.getInputRootTreeName()
        self.EnabledPlotRepsDict = {}
        for list in self.getEnabledPlotLists():
            for (key, value) in list.EnabledPlotRepsDict.items():
                self.EnabledPlotRepsDict[key] = value
        logger.info('%d enabled plots found in the output lists.' %\
                    len(self.EnabledPlotRepsDict))
