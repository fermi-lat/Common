
from pSafeROOT import ROOT

from alg__values import alg__values

import pUtils
import numpy



class alg__smart_values(alg__values):

    def __createArrays(self, timestampBranchName = 'TimeStampFirstEvt'):
        self.RootTree = self.RootObject.GetTree()
        self.RootLeaf = self.RootTree.GetLeaf(self.RootObject.GetName())
        self.TimestampArray = numpy.zeros((1), 'd')
        self.RootTree.SetBranchAddress(timestampBranchName,\
                                       self.TimestampArray)
        (name, type) = self.RootObject.GetTitle().split('/')
        if '[' not in name:
            shape = (1)
        else:
            shape = name.replace(self.RootObject.GetName(), '')
            shape = shape.replace('][', ',')
            shape = shape.replace('[', '(').replace(']', ')')
            shape = eval(shape)
        self.BranchArray = numpy.zeros(shape, type.lower())
        self.RootTree.SetBranchAddress(self.RootObject.GetName(),\
                                       self.BranchArray)

    def run(self):
        deltaDict = {}
        self.__createArrays()
        for i in range(self.RootObject.GetEntries()):
            self.RootTree.GetEntry(i)
            j = 0
            for value in self.BranchArray.flat:
                if value < self.Limits.ErrorMin:
                    label = self.getOutputDictLabel(value, j)
                    self.Output.incrementDictValue('num_error_entries')
                    self.Output.appendDictValue('error_entries', label)
                    delta = (self.Limits.ErrorMin - value)*10000
                elif value > self.Limits.ErrorMax:
                    label = self.getOutputDictLabel(value, j)
                    self.Output.incrementDictValue('num_error_entries')
                    self.Output.appendDictValue('error_entries', label)
                    delta = (value - self.Limits.ErrorMax)*10000
                elif value < self.Limits.WarningMin:
                    label = self.getOutputDictLabel(value, j)
                    self.Output.incrementDictValue('num_warning_entries')
                    self.Output.appendDictValue('warning_entries', label)
                    delta = (self.Limits.WarningMin - value)*100
                elif value > self.Limits.WarningMax:
                    label = self.getOutputDictLabel(value, j)
                    self.Output.incrementDictValue('num_warning_entries')
                    self.Output.appendDictValue('warning_entries', label)
                    delta = (value - self.Limits.WarningMax)*100
                else:
                    delta = max((self.Limits.WarningMax - value),\
                                (value - self.Limits.WarningMin))
                deltaDict[delta] = value
                j += 1
        deltas = deltaDict.keys()
        deltas.sort()
        self.Output.setValue(deltaDict[deltas[-1]])
