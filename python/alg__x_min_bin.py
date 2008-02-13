
from pSafeROOT import ROOT

from pAlarmBaseAlgorithm import pAlarmBaseAlgorithm


## @brief Position of the center of the first populated bin of
#  the histogram on the x axis, requiring at least "num_adjacent_bins"
#  consecutive populated bins, in order to remove outliers.
#  If "num_adjacent_bins" is not specified, the default value is 1
#  and the algorithm really looks for the first non-empty bin.
#
#  If the histogram is empty, then the alarm output is an error and the value
#  returned is the histogram overflow bin (last bin + 1).
#
#  <b>Output value</b>:
#
#  The center of the leftmost populated bin.

class alg__x_min_bin(pAlarmBaseAlgorithm):

    SUPPORTED_TYPES      = ['TH1F']
    SUPPORTED_PARAMETERS = ['num_adjacent_bins']
    OUTPUT_DICTIONARY    = {}
    OUTPUT_LABEL         = 'Center of the leftmost populated bin'

    ## @brief Basic algorithm evaluation for 1-dimensional histograms.
    ## @param self
    #  The class instance.

    def run(self):
        try:
            numAdjacentBins = self.ParamsDict['num_adjacent_bins']
        except KeyError:
            numAdjacentBins = 1

        currentbin = self.RootObject.GetXaxis().GetFirst()        
        while(currentbin < (self.RootObject.GetXaxis().GetLast() - numAdjacentBins)):   
            binList = []
	    for bin in range(currentbin, currentbin+numAdjacentBins):                
		if self.RootObject.GetBinContent(bin) > 0:
		    binList.append(bin)
	    if len(binList) ==  numAdjacentBins:
	        self.Output.setValue(self.RootObject.GetBinCenter(binList[0]))
                return None
            currentbin += numAdjacentBins
	self.Output.setValue(self.RootObject.GetBinCenter(self.RootObject.GetXaxis().GetLast()+1))



if __name__ == '__main__':
    from pAlarmLimits import pAlarmLimits
    limits = pAlarmLimits(-4, 4, -5, 5)
    canvas = ROOT.TCanvas('Test canvas', 'Test canvas', 400, 400)
    
    histogram = ROOT.TH1F('h', 'h', 100, -5, 5)
    histogram.FillRandom('gaus', 1000)
    histogram.Draw()
    canvas.Update()
    algorithm = alg__x_min_bin(limits, histogram, {})
    algorithm.apply()
    print algorithm.Output
