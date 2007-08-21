import pSafeLogger
logger = pSafeLogger.getLogger('pXmlBaseParser')

import sys
import os
import time

from xml.dom  import minidom

from pXmlBaseElement import pXmlBaseElement
from pXmlPlotList    import pXmlPlotList


class pXmlBaseParser:

    def __init__(self, configFilePath = None):
        self.XmlDoc = self.parseInputFile(configFilePath)

    def parseInputFile(self, filePath):
        if filePath is None:
            logger.error('Undefined configuration file. Returning None')
            return None
        logger.info('Parsing xml file %s...' % filePath)
        if os.path.exists(filePath):
            return minidom.parse(file(filePath))
        else:
            sys.exit('Configuration file %s not found. Abort.' % filePath)

    def getInputRootTreeName(self):
        tagName = 'inputRootTree'
        attName = 'name'
        try:
            element = pXmlBaseElement(self.XmlDoc)
            return element.getElementByTagName(tagName).getAttribute(attName)
        except:
            logger.error('Could not find the ROOT tree name.')
            return None
    
    def getEnabledPlotLists(self):
        lists = []
        for element in self.XmlDoc.getElementsByTagName('outputList'):
            list = pXmlPlotList(element)
            if list.Enabled:
                lists.append(list)
        return lists
    
