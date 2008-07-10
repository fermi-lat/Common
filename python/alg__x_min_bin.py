
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
#  <b>Valid parameters</b>:
#
#  @li <tt>num_adjacent_bins</tt>: number of required bins adjacent to the
#  leftmost one (knob to make the algorithm roboust against isolated bins).
#  <br>
#
#  <b>Output value</b>:
#
#  The center of the leftmost populated bin.

class alg__x_min_bin(pAlarmBaseAlgorithm):

    SUPPORTED_TYPES      = ['TH1F', 'TH1D']
    SUPPORTED_PARAMETERS = ['num_adjacent_bins']
    OUTPUT_LABEL         = 'Center of the leftmost populated bin'

    def run(self):
        numAdjacentBins = self.getParameter('num_adjacent_bins', 1)
        currentBin = self.RootObject.GetXaxis().GetFirst()        
        while(currentBin < (self.RootObject.GetXaxis().GetLast() -\
                            numAdjacentBins)):   
            binList = []
	    for bin in range(currentBin, currentBin + numAdjacentBins):
                if self.RootObject.GetBinContent(bin):
		    binList.append(bin)
		
            if len(binList) ==  numAdjacentBins:
		self.Output.setValue(self.RootObject.GetBinCenter(binList[0]))
                return None
            currentBin += numAdjacentBins
        lastBin = self.RootObject.GetXaxis().GetLast() + 1
        lastBinCenter = self.RootObject.GetBinCenter(lastBin)
	self.Output.setValue(lastBinCenter)



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
