
from pSafeROOT import ROOT

from pAlarmBaseAlgorithm import pAlarmBaseAlgorithm
from alg__x_min_bin import alg__x_min_bin



class alg__x_min_bin_slices(pAlarmBaseAlgorithm):

    SUPPORTED_TYPES      = ['TH2F']
    SUPPORTED_PARAMETERS = ['num_adjacent_bins', 'slice_width']
    OUTPUT_DICTIONARY    = {'num_warning_slices': 0,
                            'num_error_slices'  : 0,
                            'warning_slices'    : [],
                            'error_slices'      : []}
    OUTPUT_LABEL         = 'Bin center of the leftmost bin for the worst slice'

    def run(self):
        try:
            numAdjacentBins = self.ParamsDict['num_adjacent_bins']
        except KeyError:
            numAdjacentBins = 1
        try:
            sliceWidth = self.ParamsDict['slice_width']
        except KeyError:
            sliceWidth = 1
	sliceParamsDict = {'num_adjacent_bins': numAdjacentBins}
        currentBin = self.RootObject.GetXaxis().GetFirst()
        lastBin = self.RootObject.GetXaxis().GetLast() - sliceWidth
        values = []
	errorValues = []
	warningValues = []
        while(currentBin < lastBin):
            sliceHisto = self.RootObject.ProjectionY("h_single_slice",\
                                                     currentBin,\
                                                     currentBin + sliceWidth)
            sliceAlarm = alg__x_min_bin(self.Limits, sliceHisto,\
                                        sliceParamsDict)
            sliceAlarm.apply()
            sliceCenter = self.RootObject.GetXaxis().GetBinCenter(currentBin +\
                                                                  sliceWidth/2)
            sliceLabel = 'slice centered @ %s (min bin center = %s)' %\
                         (sliceCenter, sliceAlarm.Output.Value)
	    values.append(sliceAlarm.Output.Value)
	    if sliceAlarm.Output.isError():
	        self.Output.incrementDictValue('num_error_slices')
                self.Output.appendDictValue('error_slices', sliceLabel)
		errorValues.append(sliceAlarm.Output.Value)
	    elif sliceAlarm.Output.isWarning():
	        self.Output.incrementDictValue('num_warning_slices')
                self.Output.appendDictValue('warning_slices', sliceLabel)
                warningValues.append(sliceAlarm.Output.Value)
            currentBin += sliceWidth
            sliceHisto.Delete()
	if self.Output.getDictValue('num_error_slices'):
	    self.Output.setValue(min(errorValues))
	elif self.Output.getDictValue('num_warning_slices'):
	    self.Output.setValue(min(warningValues))
	else:
	    self.Output.setValue(min(values))
	    


if __name__ == '__main__':
    from pAlarmLimits import pAlarmLimits
    limits = pAlarmLimits(120, 170, 100, 200)
    canvas = ROOT.TCanvas('Test canvas', 'Test canvas', 400, 400)
    
    histogram = ROOT.TH2F('h', 'h', 3072, 0, 3072, 100, 0, 300)
    for i in range(3072):
        for j in range(50, 100):
            histogram.SetBinContent(i,j, 100)
    histogram.SetBinContent(10, 10, 50)
    histogram.SetBinContent(10, 11, 20)
    histogram.SetBinContent(10, 12, 23)
    histogram.SetBinContent(100, 20, 50)
    histogram.SetBinContent(100, 21, 20)
    histogram.SetBinContent(100, 22, 23)
    histogram.SetBinContent(200, 30, 50)
    histogram.SetBinContent(200, 31, 20)
    histogram.SetBinContent(200, 32, 23)
    histogram.SetBinContent(300, 40, 50)
    histogram.SetBinContent(300, 41, 20)
    histogram.SetBinContent(300, 42, 23)
    histogram.Draw("colz")
    canvas.Update()
    algorithm = alg__x_min_bin_slices(limits, histogram, {'slice_width': 12})
    algorithm.apply()
    print algorithm.Output
