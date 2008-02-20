
from pSafeROOT import ROOT

from pAlarmBaseAlgorithm import pAlarmBaseAlgorithm


## @brief Make sure all the entries of a branch are within limits.
#
#  The algorithm loops over the entries of the branch and makes sure that
#  all the values are within the limits.



class alg__values(pAlarmBaseAlgorithm):

    SUPPORTED_TYPES      = ['TBranch']
    SUPPORTED_PARAMETERS = ['Exclude','Only']
    OUTPUT_DICTIONARY    = {'num_warning_entries': 0,
                            'num_error_entries'  : 0,
                            'warning_entries'    : [],
                            'error_entries'      : []
                            }
    OUTPUT_LABEL          = ''

    def __init__(self, limits, object, paramsDict, conditionsDict):
        pAlarmBaseAlgorithm.__init__(self, limits, object, paramsDict, conditionsDict)
        self.RootTree = self.RootObject.GetTree()
        self.RootLeaf = self.RootTree.GetLeaf(self.RootObject.GetName())

    def getBranchContent(self, entry, index):
        self.RootObject.GetEntry(entry)
        return self.RootLeaf.GetValue(index)

    def run(self):
        for entry in range(self.RootObject.GetEntries()):
            for index in range (self.RootLeaf.GetLen()):
                indices = self.indexlist(index)
                if(indices!=[]):
                    if "Only" in self.ParamsDict:
                        if not self.matchindex(indices,self.ParamsDict["Only"]):
                            continue
                    if "Exclude" in self.ParamsDict:
                        if self.matchindex(indices , self.ParamsDict["Exclude"]):
                            continue
                value = self.getBranchContent(entry,index)
                if value < self.Limits.ErrorMin or value > self.Limits.ErrorMax:
                    if indices==[]:
                        point = (entry, value)
                    else:
                        point = (entry,indices,value)
                    self.Output.incrementDictValue('num_error_entries')
                    self.Output.appendDictValue('error_entries', point)
                elif value < self.Limits.WarningMin or value > self.Limits.WarningMax:
                    if indices==[]:
                        point = (entry, value)
                    else:
                        point = (entry,indices,value)
                    self.Output.incrementDictValue('num_warning_entries')
                    self.Output.appendDictValue('warning_entries', point)
                if self.Output.getDictValue('num_error_entries'):
                    self.Output.setValue(self.Output.getDictValue('error_entries')[0][-1])
                elif self.Output.getDictValue('num_warning_entries'):
                    self.Output.setValue(self.Output.getDictValue('warning_entries')[0][-1])
                else:
                    self.Output.setValue(value)
                
    def indexlist(self, index):
        name = self.RootLeaf.GetTitle()
        if name.find('[') == -1:
            return []
        name = name[name.find('['):-1]
        dims = name.split('][')
        retlist = []
        ind = index
        for i in range(len(dims)):
            fact = 1
            for j in range(i + 1, len(dims)):
                fact *= int(dims[j])
            retlist.append(ind/fact)
            ind -= ind/fact*fact
        return retlist
        
    def matchindex(self, indices, matchlist):    
        if indices in matchlist:
            return True
        for ix in matchlist:
            match=True
            if not '*' in ix:
                continue
            for i in range(len(indices)):
                if ix[i]=='*':
                    continue
                if indices[i]==ix[i]:
                    continue
                match=False
                break
            if match==True:
                return True
        return False
        
            

if __name__ == '__main__':
    pass

