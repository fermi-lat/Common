
from pSafeROOT import ROOT
from copy import deepcopy
from alg__x_min_bin import alg__x_min_bin


class alg__x_min_bin_slices(alg__x_min_bin):

    SUPPORTED_TYPES      = ['TH2F']
    SUPPORTED_PARAMETERS = ['num_adjacent_bins', 'slice_width']
    OUTPUT_DICTIONARY    = {'num_warning_slices': 0,
                            'num_error_slices'  : 0,
                            'warning_slices'    : [],
                            'error_slices'      : []}
    OUTPUT_LABEL         = ''


    def __init__(self, limits, object, paramsDict, conditionsDict = {}):
        alg__x_min_bin.__init__(self, limits, object, paramsDict,\
                                conditionsDict = {})
        self.Output.DetailedDict = deepcopy(self.OUTPUT_DICTIONARY)

    def run(self):
        try:
            sliceWidth = self.ParamsDict['slice_width']
        except KeyError:
            sliceWidth = 1

        th2 =   self.RootObject
        currentbin = th2.GetXaxis().GetFirst()
        lastbin    = th2.GetXaxis().GetLast() - sliceWidth
        while(currentbin < lastbin):   
            self.RootObject = th2.ProjectionY("hslice",currentbin,currentbin+sliceWidth)            
            alg__x_min_bin.run(self)
            if self.Output.Status['level'] == 2:
                self.Output.incrementDictValue('num_warning_slices')
                sliceCenter = th2.GetXaxis().GetBinCenter(currentbin + sliceWidth/2)
                self.Output.appendDictValue('warning_slices', 'slice centered @ %s' % sliceCenter)
            elif self.Output.Status['level'] == 3:
                self.Output.incrementDictValue('num_error_slices')
                sliceCenter = th2.GetXaxis().GetBinCenter(currentbin + sliceWidth/2)
                self.Output.appendDictValue('error_slices', 'slice centered @ %s' % sliceCenter)
            currentbin += sliceWidth
        self.RootObject = th2
        if self.Output.getDictValue('num_error_slices'):
            self.Output.setStatusError()
            self.Output.setValue(self.Output.getDictValue('error_slices')[0])
        elif self.Output.getDictValue('num_warning_slices'):
            self.Output.setStatusWarning()
            self.Output.setValue(self.Output.getDictValue('warning_slices')[0])


if __name__ == '__main__':
    from pAlarmLimits import pAlarmLimits
    limits = pAlarmLimits(120, 170, 100, 200)
    canvas = ROOT.TCanvas('Test canvas', 'Test canvas', 400, 400)
    
    histogram = ROOT.TH2F('h', 'h', 3072, 0, 3072, 100, 0, 300)
    for i in range(3072):
        for j in range(50, 100):
            histogram.SetBinContent(i,j, 100)
    histogram.SetBinContent(10,10, 50)
    histogram.SetBinContent(10,11, 20)
    histogram.SetBinContent(10,12, 23)
    histogram.Draw("colz")
    canvas.Update()
    algorithm = alg__x_min_bin_slices(limits, histogram, {})
    algorithm.apply()
    print algorithm.Output
