
from pSafeROOT import ROOT

from pAlarmBaseAlgorithm import pAlarmBaseAlgorithm
from alg__x_min_bin import alg__x_min_bin


## @brief This is an attempt to generalize the @ref alg__x_min_bin algorithm
#  to a 2-dimensional histogram. The histogram itself is first sliced
#  along the y axis (the width of the slice can be optionally set) and
#  the base alg__x_min_bin algorithm is then applied on each slice.
#
#  <b>Valid parameters</b>:
#
#  @li <tt>num_adjacent_bins</tt>: number of required bins adjacent to the
#  leftmost one (knob to make the algorithm roboust against isolated bins).
#  <br>
#
#  @li <tt>slice_width</tt>: the width of each slice (number of bins) of the
#  2-dimensional histogram.
#  <br>
#
#  <b>Output value</b>:
#
#  The center of the leftmost populated bin for the worst (i.e. the most "out
#  of limits" slice).

class alg__x_min_bin_slices(pAlarmBaseAlgorithm):

    SUPPORTED_TYPES      = ['TH2F']
    SUPPORTED_PARAMETERS = ['num_adjacent_bins', 'slice_width']
    OUTPUT_LABEL         = 'Bin center of the leftmost bin for the worst slice'

    def getDetailedLabel(self, i, value):
        return 'slice centered at %s = %s, minimum bin center = %s' %\
            (self.getAxisLabel('x'), self.getFormattedX(i), value)

    def run(self):
        numAdjBins = self.getParameter('num_adjacent_bins', 1)
        sliceWidth = self.getParameter('slice_width', 1)
	sliceParDict = {'num_adjacent_bins': numAdjBins}
        i = self.RootObject.GetXaxis().GetFirst()
        lastBin = self.RootObject.GetXaxis().GetLast() - sliceWidth
        values = []
	errorValues = []
	warningValues = []
        while(i < lastBin):
            sliceCenter = i + sliceWidth/2
            sliceHisto = self.RootObject.ProjectionY("h_single_slice", i,\
                                                         i + sliceWidth)
            sliceAlarm = alg__x_min_bin(self.Limits, sliceHisto, sliceParDict)
            sliceAlarm.apply()
	    values.append(sliceAlarm.Output.Value)
	    if sliceAlarm.Output.isError():
	        self.Output.incrementDictValue('num_error_entries')
                self.Output.appendDictValue('error_entries',\
                    self.getDetailedLabel(sliceCenter, sliceAlarm.Output.Value))
		errorValues.append(sliceAlarm.Output.Value)
	    elif sliceAlarm.Output.isWarning():
	        self.Output.incrementDictValue('num_warning_entries')
                self.Output.appendDictValue('warning_entries',\
                    self.getDetailedLabel(sliceCenter, sliceAlarm.Output.Value))
                warningValues.append(sliceAlarm.Output.Value)
            i += sliceWidth
            sliceHisto.Delete()
	if self.Output.getDictValue('num_error_entries'):
	    self.Output.setValue(min(errorValues))
	elif self.Output.getDictValue('num_warning_entries'):
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
    histogram.GetXaxis().SetTitle('something')
    histogram.Draw("colz")
    canvas.Update()
    algorithm = alg__x_min_bin_slices(limits, histogram, {'slice_width': 12})
    algorithm.apply()
    print algorithm.Output
