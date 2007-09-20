#! /bin/env python

## @package pRootFileComparator
## @brief Module providing utilities for comparing ROOT files.

import sys
import os
import time

import pSafeLogger
logger = pSafeLogger.getLogger('pRootFileComparator')

from pSafeROOT        import ROOT
from pRootFileManager import pRootFileManager

ROOT.gStyle.SetOptStat(111111)
ROOT.gStyle.SetOptTitle(1)


COMPARISON_METHODS = {'TH1': [#'GetEntries()',\
                              'GetEffectiveEntries()',\
                              'GetNbinsX()',\
                              'GetXaxis().GetXmin()', 'GetXaxis().GetXmax()',\
                              'GetMean()', 'GetRMS()', 'GetBinContent(0)',\
                              'GetBinContent(_p_.GetNbinsX() + 1)'],\
                      'TH2': [#'GetEntries()',\
                              'GetEffectiveEntries()',\
                              'GetNbinsX()', 'GetNbinsY()',\
                              'GetXaxis().GetXmin()', 'GetXaxis().GetXmax()',\
                              'GetYaxis().GetXmin()', 'GetYaxis().GetXmax()',\
                              'GetMean()', 'GetMean(2)', 'GetRMS()',\
                              'GetRMS(2)']
                      }
DRAW_OPTIONS = {'TH1': '', 'TH2': 'colz'}


## @brief Class for ROOT file comparison.

class pRootFileComparator:

    def __init__(self, filePath1, filePath2, debug = False,\
                 interactive = False):
        self.FilePath1 = filePath1
        self.FilePath2 = filePath2
        self.FileManager1 = pRootFileManager(self.FilePath1)
        self.FileManager2 = pRootFileManager(self.FilePath2)
        self.PlotsDict1 = self.FileManager1.getPlotsDict()
        self.PlotsDict2 = self.FileManager2.getPlotsDict()
        self.Debug = debug
        self.Interactive = interactive
        self.InteractiveCanvas = None
        self.CommonPlotsList = []
        self.__fillCommonPlotsList()

    def __fillCommonPlotsList(self):
        logger.info('Filling the list of plots in common...')
        for key in self.PlotsDict1.keys():
            if key in self.PlotsDict2.keys():
                self.CommonPlotsList.append(key)
        for key in self.PlotsDict2.keys():
            if key in self.PlotsDict1.keys()\
                   and key not in self.CommonPlotsList:
                self.CommonPlotsList.append(key)
        logger.info('Done. %d plots found.' % len(self.CommonPlotsList))
        surplus1 = []
        for key in self.PlotsDict1.keys():
            if key not in self.CommonPlotsList:
                surplus1.append(key)
        surplus2 = []
        for key in self.PlotsDict2.keys():
            if key not in self.CommonPlotsList:
                surplus2.append(key)
        if surplus1 != []:
            self.error('Plots which are in %s but not in %s: %s' %\
                       (self.FilePath1, self.FilePath2, surplus1))
        if surplus2 != []:
            self.error('Plots which are in %s but not in %s: %s' %\
                       (self.FilePath2, self.FilePath1, surplus2))
        
    def getType(self, plot):
        return plot.__class__.__name__[:-1]

    def error(self, message):
        print '** ERROR **: %s' % message

    def debug(self, message):
        if self.Debug:
            print message

    def __createInteractiveCanvas(self):
        if self.InteractiveCanvas == None:
            self.InteractiveCanvas = ROOT.TCanvas('Interactive canvas',\
                                                  'Interactive canvas',\
                                                  900, 700)
            self.InteractiveCanvas.Divide(1,2)

    def basicCompare(self, method, plot1, plot2):
        value1 = eval('plot1.%s' % method.replace('_p_', 'plot1'))
        value2 = eval('plot2.%s' % method.replace('_p_', 'plot2'))
        self.debug('%s, v1 = %s, v2 = %s.' % (method, value1, value2))
        if value1 != value2:
            self.error('Mismatch in %s for %s (v1 = %s, v2 = %s)' %\
                       (method, plot1.GetName(), value1, value2))
            return 1
        return 0

    def compare(self, plotName):
        self.debug('Comparing %s...' % plotName)
        out = 0
        plot1 = self.PlotsDict1[plotName]
        plot2 = self.PlotsDict2[plotName]
        errorCode = 0
        for method in COMPARISON_METHODS[self.getType(plot1)]:
            errorCode += self.basicCompare(method, plot1, plot2)
        if errorCode and self.Interactive:
            self.__createInteractiveCanvas()
            self.InteractiveCanvas.cd(1)
            plot1.SetTitle(self.FilePath1)
            plot1.Draw(DRAW_OPTIONS[self.getType(plot1)])
            self.InteractiveCanvas.cd(2)
            plot2.SetTitle(self.FilePath2)
            plot2.Draw(DRAW_OPTIONS[self.getType(plot2)])
            self.InteractiveCanvas.Update()
            answer = raw_input("Press any key to continue, q to quit ...")
            if answer == 'q':
                sys.exit('Application quit.')
        self.debug('Done.')

    def run(self):
        for plotName in self.CommonPlotsList:
            self.compare(plotName)
                

if __name__ == '__main__':
    from pOptionParser import pOptionParser
    optparser = pOptionParser('vi', 2, 2, False)
    comp = pRootFileComparator(optparser.Arguments[0],\
                               optparser.Arguments[1],\
                               optparser.Options.v, optparser.Options.i)
    comp.run()

