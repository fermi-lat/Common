
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
#  > from pSafeROOT import *
#  That should do it.

ROOT_PALETTE = 1

import sys
import os
import logging

if 'ROOT' not in sys.modules:
    import ROOT
    logging.info('First ROOT import, setting palette and fucking ROOT...')
    currentDirPath = os.path.abspath(os.curdir)
    logging.info('Current directory is %s.' % currentDirPath)
    ROOT.gStyle.SetPalette(ROOT_PALETTE)
    os.chdir(currentDirPath)
    logging.info('Done.')
