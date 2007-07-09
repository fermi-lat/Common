## @package pRootFileManager
## @brief Module providing utilities for managing ROOT files.

import pSafeLogger
logger = pSafeLogger.getLogger('pRootFileManager')

import sys
import os
import time

from pSafeROOT import ROOT

## @brief Class for ROOT file handling.

class pRootFileManager:

    ## @brief Basic constructor.
    ## @param self
    #  The class instance.
    ## @param rootFilePath
    #  The path to the input ROOT file.

    def __init__(self, rootFilePath = None):

        ## @var RootFile
        ## @brief The underlying ROOT file.
        
        self.RootFile = None
        if rootFilePath is not None:
            self.openFile(rootFilePath)

    ## @brief Open a ROOT file.
    ## @param self
    #  The class instance.
    ## @param rootFilePath
    #  The path to the input ROOT file.

    def openFile(self, rootFilePath):
        logger.info('Opening file %s...' % rootFilePath)
        if not os.path.exists(rootFilePath):
            sys.exit('File %s does not exist.' % rootFilePath)
        self.RootFile = ROOT.TFile(rootFilePath)
        if self.RootFile.GetFd() == -1:
            sys.exit('Could not open file %s.' % rootFilePath)
        logger.info('Done. %s objects found.\n' %\
                    self.RootFile.GetListOfKeys().LastIndex())

    ## @brief Close the ROOT file.
    ## @param self
    #  The class instance.

    def closeFile(self):
        if self.RootFile is not None:
            self.RootFile.Close()
            self.RootFile = None

    ## @brief Get a ROOT object from the ROOT File (by object name).
    ## @param self
    #  The class instance.
    ## @param name
    #  The object name.

    def get(self, name):
        try:
            return self.RootFile.Get(name)
        except:
            logger.error('Could not find %s in the ROOT file.' % name)

    ## @brief Function implementing the pattern match.
    #
    #  Return True if the name (after the * has been stripped off) differs
    #  from the pattern by numbers only (i.e. wildcards stand for numbers
    #  only).

    def __match(self, name, pattern):
        return name.replace(pattern.replace('*', ''), '').isdigit()

    ## @brief Find ROOT objects whose name matches a certain pattern in a
    #  ROOT file.
    #
    #  If the pattern contains a slash (/) it is assumed that the method is
    #  intended to return a TBranch of a TTree in the form "branch/tree".
    #  Otherwise the objects are searched directly.
    ## @param self
    #  The class instance
    ## @param
    #  The name pattern.

    def find(self, pattern):
        if '/' in pattern:
            return self.findTreeBranches(pattern)
        else:
            return self.findObjects(pattern)

    ## @brief Find ROOT objects whose name matches a certain pattern in a
    #  ROOT file.
    ## @param self
    #  The class instance
    ## @param
    #  The name pattern.

    def findObjects(self, pattern):
        objects = []
        for i in range(self.RootFile.GetListOfKeys().LastIndex()):
	    key    = self.RootFile.GetListOfKeys().At(i).GetName()
            if key == pattern or self.__match(key, pattern):
                objects.append(self.RootFile.FindObjectAny(key))
        return objects

    ## @brief Find ROOT branches whose name matches a certain pattern in a
    #  ROOT file.
    #
    #  @todo Much work needed, here, to improve the object access.
    #  In this case the pattern must be of the form tree_name/branch_name
    #  (slash-separated).
    ## @param self
    #  The class instance
    ## @param
    #  The name pattern.

    def findTreeBranches(self, pattern):
        (treeName, branchName) = pattern.split('/')
        try:
            tree = self.RootFile.FindObjectAny(treeName)
        except:
            logger.error('Could not find %s TTree in the ROOT file' % treeName)
            return []
        try:
            branch = tree.GetBranch(branchName)
        except:
            logger.error('%s TTree does not have a TBranch named %s.' %
                         (treeName, branchName))
            return []
        return [branch]


if __name__ == '__main__':
    manager = pRootFileManager()