
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
    OUTPUT_LABEL         = ''

    def run(self):
        try:
            numAdjacentBins = self.ParamsDict['num_adjacent_bins']
        except KeyError:
            numAdjacentBins = 1

        try:
            sliceWidth = self.ParamsDict['slice_width']
        except KeyError:
            sliceWidth = 1
	singleSliceParamsDict = {'num_adjacent_bins': numAdjacentBins}
        currentbin = self.RootObject.GetXaxis().GetFirst()
        lastbin    = self.RootObject.GetXaxis().GetLast() - sliceWidth
	errorValues = []
	warningValues = []
	values = []
        while(currentbin < lastbin):
            hslice = self.RootObject.ProjectionY("hslice",currentbin,currentbin+sliceWidth)            
            singleSliceAlarm = alg__x_min_bin(self.Limits, hslice, singleSliceParamsDict)
            singleSliceAlarm.apply()
            sliceCenter = self.RootObject.GetXaxis().GetBinCenter(currentbin + sliceWidth/2)
	    values.append(singleSliceAlarm.Output.Value)
	    if singleSliceAlarm.Output.isError():
	        self.Output.incrementDictValue('num_error_slices')
                self.Output.appendDictValue('error_slices', 'slice centered @ %s (min = %s)' %\
                                            (sliceCenter, singleSliceAlarm.Output.Value))
		errorValues.append(singleSliceAlarm.Output.Value)
	    elif singleSliceAlarm.Output.isWarning():
	        self.Output.incrementDictValue('num_warning_slices')
                self.Output.appendDictValue('warning_slices', 'slice centered @ %s (min = %s)' %\
                                            (sliceCenter, singleSliceAlarm.Output.Value))
                warningValues.append(singleSliceAlarm.Output.Value)
            currentbin += sliceWidth
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
    histogram.SetBinContent(10,10, 50)
    histogram.SetBinContent(10,11, 20)
    histogram.SetBinContent(10,12, 23)
    histogram.Draw("colz")
    canvas.Update()
    algorithm = alg__x_min_bin_slices(limits, histogram, {'slice_width': 12})
    algorithm.apply()
    print algorithm.Output
