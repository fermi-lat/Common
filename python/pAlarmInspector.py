#! /bin/env python

import os
import sys

import pSafeLogger
logger = pSafeLogger.getLogger('pXmlAlarmInspector')

from pXmlBaseElement import pXmlBaseElement
from xml.dom         import minidom


BASE_ALARMS_XML_DIR  = '../../AlarmsCfg/xml/'
BASE_FASTMON_XML_DIR = '../../FastMonCfg/xml/'
BASE_OTHERS_XML_DIR  = '../../DigiReconCalMeritCfg/'


class pAlarmInspector:

    def __init__(self):
        pass

    def inspect(self, application, productType):
        logger.info('Inspecting %s %s...' % (application, productType))
        plotsFilePath = self.getPlotsXmlFilePath(application, productType)
        alarmsFilePath = self.getAlarmsXmlFilePath(application, productType)
        plotsXmlDoc = self.getXmlDoc(plotsFilePath)
        alarmsXmlDoc = self.getXmlDoc(alarmsFilePath)
        plotsDict = {}
        for list in plotsXmlDoc.getElementsByTagName('outputList'):
            for object in list.getElementsByTagName('object'):
                element  = pXmlBaseElement(object)
                objectName = element.getTagValue('name')
                plotsDict[objectName] = []
        for list in alarmsXmlDoc.getElementsByTagName('alarmList'):
            for set in list.getElementsByTagName('alarmSet'):
                element  = pXmlBaseElement(set)
                alarmName = element.getAttribute('name')
                for objectName in plotsDict.keys():
                    if self.match(objectName, alarmName):
                        break
                for alarm in set.getElementsByTagName('alarm'):
                    algorithm = pXmlBaseElement(alarm).getAttribute('function')
                    plotsDict[objectName].append(algorithm)
        keys = plotsDict.keys()
        keys.sort()
        for key in keys:
            print '%s: %s' % (key, plotsDict[key])

    def match(self, objectName, alarmName):
        return objectName.split('[')[0] == alarmName.replace('_*', '') 
        
    def getXmlDoc(self, filePath):
        logger.debug('Parsing %s...' % filePath)
        if os.path.exists(filePath):
            return minidom.parse(file(filePath))
        else:
            sys.exit('%s not found. Abort.' % filePath)

    def getPlotsXmlFilePath(self, application, productType):
        if application == 'fastmon' and productType == 'eor':
            return os.path.join(BASE_FASTMON_XML_DIR, 'config.xml')
        else:
            if productType == 'eor':
                fileName = 'monconfig_%s_histos.xml' % application
            elif productType == 'trend':
                fileName = 'monconfig_%s_trending.xml' % application
            else:
                sys.exit('Invalid product type (%s). Abort.' % productType)
            return os.path.join(BASE_OTHERS_XML_DIR, fileName)

    def getAlarmsXmlFilePath(self, application, productType):
        fileName = '%s_%s_alarms.xml' % (application, productType)
        return os.path.join(BASE_ALARMS_XML_DIR, fileName)


if __name__ == '__main__':
    inspector = pAlarmInspector()
    for application in ['digi', 'recon', 'merit']:
        for productType in ['eor', 'trend']:
            inspector.inspect(application, productType)
