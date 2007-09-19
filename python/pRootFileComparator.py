#! /bin/env python

## @package pRootFileComparator
## @brief Module providing utilities for comparing ROOT files.

import sys
import os
import time

from pSafeROOT        import ROOT
from pRootFileManager import pRootFileManager

## @brief Class for ROOT file comparison.

class pRootFileComparator:

    def __init__(self, filePath1, filePath2, debug = False):
        self.FileManager1 = pRootFileManager(filePath1)
        self.FileManager2 = pRootFileManager(filePath2)
        self.PlotsDict1 = self.FileManager1.getPlotsDict()
        self.PlotsDict2 = self.FileManager2.getPlotsDict()
        self.Debug = debug

    def getType(self, plot):
        return plot.__class__.__name__[:-1]

    def error(self, message):
        print '** ERROR **: %s' % message

    def debug(self, message):
        if self.Debug:
            print message

    def basicCompare(self, method, plot1, plot2):
        value1 = eval('plot1.%s' % method)
        value2 = eval('plot2.%s' % method)
        self.debug('%s, v1 = %s, v2 = %s.' % (method, value1, value2))
        if value1 != value2:
            self.error('Mismatch in %s for %s (v1 = %s, v2 = %s)' %\
                       (method, plot1.GetName(), value1, value2))
            
    def compareTH1(self, plot1, plot2):
        self.basicCompare('GetNbinsX()', plot1, plot2)
        self.basicCompare('GetXaxis().GetXmin()', plot1, plot2)
        self.basicCompare('GetXaxis().GetXmax()', plot1, plot2)
        self.basicCompare('GetMean()', plot1, plot2)
        self.basicCompare('GetRMS()', plot1, plot2)

    def compareTH2(self, plot1, plot2):
        self.compareTH1(plot1, plot2)
        self.basicCompare('GetNbinsY()', plot1, plot2)
        self.basicCompare('GetYaxis().GetXmin()', plot1, plot2)
        self.basicCompare('GetYaxis().GetXmax()', plot1, plot2)
        self.basicCompare('GetMean(2)', plot1, plot2)
        self.basicCompare('GetRMS(2)', plot1, plot2)        

    def compare(self, plotName):
        self.debug('Comparing %s...' % plotName)
        plot1 = self.PlotsDict1[plotName]
        plot2 = self.PlotsDict2[plotName]
        exec('self.compare%s(plot1, plot2)' % self.getType(plot1))
        self.debug('Done.')

    def run(self):
        for key in self.PlotsDict1.keys():
            try:
                self.compare(key)
            except:
                self.error('Could not compare %s.' % key)

                

if __name__ == '__main__':
    from pOptionParser import pOptionParser
    optparser = pOptionParser('v', 2, 2, False)
    comp = pRootFileComparator(optparser.Arguments[0],\
                               optparser.Arguments[1], optparser.Options.v)
    comp.run()

