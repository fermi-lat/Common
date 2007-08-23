
from pSafeROOT import ROOT

from pAlarmBaseAlgorithm import pAlarmBaseAlgorithm


## @brief Make sure all the entries are within limits
#
#  The algorithm loops over the entry of the branch and that
#  all the values are within the limits.
#  In case of an error/warning the content of the FIRST entry out of limits
#  is returned.
#  The detailed output dictionary contains the value and the entry number of
#  all the entrie the are out of the limits. 
#
#  Valid parameters:
#  @li None

class alg__values(pAlarmBaseAlgorithm):

    SUPPORTED_TYPES      = ['TBranch']
    SUPPORTED_PARAMETERS = []

    def __init__(self, limits, object, paramsDict = {}):
        pAlarmBaseAlgorithm.__init__(self, limits, object, paramsDict)
        self.RootTree = self.RootObject.GetTree()

    def getBranchContent(self, entry):
        self.RootObject.GetEntry(entry)
        return eval('self.RootTree.%s' % self.RootObject.GetName())

    def run(self):
        self.Output.setDictValue('num_warning_points', 0)
        self.Output.setDictValue('num_error_points'  , 0)
        self.Output.setDictValue('warning_points', [])
        self.Output.setDictValue('error_points'  , [])
        for entry in range(self.RootObject.GetEntries()):
            value = self.getBranchContent(entry)
            if value < self.Limits.ErrorMin or value > self.Limits.ErrorMax:
                point = (entry, value)
                self.Output.incrementDictValue('num_error_points')
                self.Output.appendDictValue('error_points', point)
            elif value < self.Limits.WarningMin or value > self.Limits.WarningMax:
                point = (entry, value)
                self.Output.incrementDictValue('num_warning_points')
                self.Output.appendDictValue('warning_points', point)
            if self.Output.getDictValue('num_error_points'):
                self.Output.setValue(self.Output.getDictValue('error_points')[0][1])
            elif self.Output.getDictValue('num_warning_points'):
                self.Output.setValue(self.Output.getDictValue('warning_points')[0][1])
            else:
                entry = self.RootObject.GetEntries()/2
                self.Output.setValue(self.RootObject.GetBranchContent(entry))


                

if __name__ == '__main__':
    pass

