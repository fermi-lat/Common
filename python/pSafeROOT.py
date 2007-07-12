
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

if 'ROOT' not in sys.modules:
    import ROOT
    logger.info('First ROOT import, setting palette and fooling ROOT...')
    currentDirPath = os.path.abspath(os.curdir)
    logger.info('Current dir: %s.' % currentDirPath)
    ROOT.gStyle.SetPalette(ROOT_PALETTE)
    os.chdir(currentDirPath)
    logger.info('Done.\n')
