
## @package pSafeROOT
## @brief Package for a safe ROOT import.
#
#  This module is intended to fool ROOT...
#  In fact if a valid folder path is passed as one of the arguments to the
#  python script, ROOT cd into it the first time ROOT itself is called
#  (not sure why but that's the way it is).
#
#  Do not:
#  > import ROOT
#  explicitely in the code. Instead:
#  > from pSafeROOT import ROOT
#  That should do it.

import pSafeLogger
logger = pSafeLogger.getLogger('pSafeROOT')

ROOT_PALETTE = 1

import sys
import os

def applyGlastStyle():
    logger.info('Applying GLAST ROOT style conventions...')
    ROOT.gROOT.SetStyle('Plain')
    ROOT.gStyle.SetPalette(1)
    ROOT.gStyle.SetFillColor(0)
    ROOT.gStyle.SetCanvasColor(10)
    ROOT.gStyle.SetFrameBorderMode(0)
    ROOT.gStyle.SetFrameFillColor(0)
    ROOT.gStyle.SetPadBorderMode(0)
    ROOT.gStyle.SetPadColor(0)
    ROOT.gStyle.SetPadTopMargin(0.07)
    ROOT.gStyle.SetPadLeftMargin(0.13)
    ROOT.gStyle.SetPadRightMargin(0.11)
    ROOT.gStyle.SetPadBottomMargin(0.1)
    ROOT.gStyle.SetPadTickX(1)
    ROOT.gStyle.SetPadTickY(1)
    ROOT.gStyle.SetHistFillStyle(0)
    ROOT.gStyle.SetOptTitle(0)
    ROOT.gStyle.SetTitleSize(0.22)
    ROOT.gStyle.SetTitleFontSize(2)
    ROOT.gStyle.SetTitleFont(42)
    ROOT.gStyle.SetTitleFont(62, 'xyz')
    ROOT.gStyle.SetTitleYOffset(1.0)
    ROOT.gStyle.SetTitleXOffset(1.0)
    ROOT.gStyle.SetTitleXSize(0.04)
    ROOT.gStyle.SetTitleYSize(0.04)
    ROOT.gStyle.SetTitleX(0.15)
    ROOT.gStyle.SetTitleY(0.98)
    ROOT.gStyle.SetTitleW(0.70)
    ROOT.gStyle.SetTitleH(0.05)
    ROOT.gStyle.SetStatFont(42)
    ROOT.gStyle.SetStatX(0.91)
    ROOT.gStyle.SetStatY(0.90)
    ROOT.gStyle.SetStatW(0.15)
    ROOT.gStyle.SetStatH(0.15)
    ROOT.gStyle.SetLabelFont(42, 'xyz')
    ROOT.gStyle.SetLabelSize(0.035, 'xyz')
    ROOT.gStyle.SetGridColor(16)
    ROOT.gStyle.SetLegendBorderSize(0)

if 'ROOT' not in sys.modules:
    import ROOT
    logger.info('First ROOT import, setting palette and fooling ROOT...')
    currentDirPath = os.path.abspath(os.curdir)
    logger.info('Current dir: %s.' % currentDirPath)
    ROOT.gStyle.SetPalette(ROOT_PALETTE)
    os.chdir(currentDirPath)
    applyGlastStyle()

