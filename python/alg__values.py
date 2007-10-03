
from pSafeROOT import ROOT

from pAlarmBaseAlgorithm import pAlarmBaseAlgorithm


## @brief Make sure all the entries are within limits
#
#  The algorithm loops over the entries of the branch and makes sure that
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
    SUPPORTED_PARAMETERS = ['Exclude','Only']

    def __init__(self, limits, object, paramsDict = {}):
        pAlarmBaseAlgorithm.__init__(self, limits, object, paramsDict)
        self.RootTree = self.RootObject.GetTree()
        self.RootLeaf = self.RootTree.GetLeaf(self.RootObject.GetName())

    def getBranchContent(self, entry,index):
        self.RootObject.GetEntry(entry)
        return self.RootLeaf.GetValue(index)

    def run(self):
        self.Output.setDictValue('num_warning_points', 0)
        self.Output.setDictValue('num_error_points'  , 0)
        self.Output.setDictValue('warning_points', [])
        self.Output.setDictValue('error_points'  , [])
        for entry in range(self.RootObject.GetEntries()):
            for index in range (self.RootLeaf.GetLen()):
                indices=self.indexlist(index)
                if(indices!=[]):
                    if "Only" in self.ParamsDict:
                        if not indices in self.ParamsDict["Only"]:
                            continue
                    if "Exclude" in self.ParamsDict:
                        if indices in self.ParamsDict["Exclude"]:
                            continue
                value = self.getBranchContent(entry,index)
                if value < self.Limits.ErrorMin or value > self.Limits.ErrorMax:
                    if indices==[]:
                        point = (entry, value)
                    else:
                        point = (entry,indices,value)
                    self.Output.incrementDictValue('num_error_points')
                    self.Output.appendDictValue('error_points', point)
                elif value < self.Limits.WarningMin or value > self.Limits.WarningMax:
                    if indices==[]:
                        point = (entry, value)
                    else:
                        point = (entry,indices,value)
                    self.Output.incrementDictValue('num_warning_points')
                    self.Output.appendDictValue('warning_points', point)
                if self.Output.getDictValue('num_error_points'):
                    self.Output.setValue(self.Output.getDictValue('error_points')[0][-1])
                elif self.Output.getDictValue('num_warning_points'):
                    self.Output.setValue(self.Output.getDictValue('warning_points')[0][-1])
                else:
                    self.Output.setValue(value)
                
    def indexlist(self,index):
        name=self.RootLeaf.GetTitle()
        if name.find('[')==-1:
            return [];
        name=name[name.find('['):-1]
        dims=name.split('][')
        retlist=[]
        ind=index
        for i in range(len(dims)):
            fact=1
            for j in range(i+1,len(dims)):
                fact*=int(dims[j])
            retlist.append(ind/fact)
            ind-=ind/fact*fact
        return retlist
        
        

if __name__ == '__main__':
    pass

