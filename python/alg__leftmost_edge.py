import pUtils

from pSafeROOT           import ROOT
from math                import sqrt
from pAlarmBaseAlgorithm import pAlarmBaseAlgorithm

## @brief Search for the leftmost (statistically significant) edge into a
## 1D histogram.
#
#  There's essentially a loop over the histogram bins, here, with a
#  sliding window of adjustable width. For each bin the average values of the
#  bins on the left part of the window and on the right part of the window
#  are evaluated:
#  @f[
#  m_l = \sum_{i \in {\rm left \; half \; window}} n_i
#  @f]
#  @f[
#  m_r = \sum_{i \in {\rm right \; half \; window}} n_i
#  @f]
#  
#  The two values are then compared and, as soon as a statistically significant
#  difference is found (i.e. when the significance exceeds an adjustable
#  threshold), the search is refined in the neighbour bin to
#  identify the bin that maximises the difference itself.
#  The procedure can be seen as a double least squares fit in which the
#  error on the points is assumed to be constant and equal to the
#  square root of the average over the two half windows---this is clearly
#  an oversimplification but, provided that the width of the window and the
#  threshold are set correctly.
#  
#  The formula for the significance of the edge reads like:
#  @f[
#  s = {\rm whw} \cdot \frac{\| (m_l - m_r) \|}{(m_l + m_r)} 
#  @f]
#  where whw is the window half width.
#
#  <b>Valid parameters</b>:
#
#  @li <tt>window_half_width</tt>: the half width of the sliding window.
#  <br>
#  @li <tt>threshold</tt>: the threshold (number of sigma) over which an
#  edge is reported.
#  <br>
#  @li <tt>start_x</tt>: the x value of the bin the algorithm starts
#  looping from.
#
#  <b>Output value</b>:
#
#  The position (center of the bin) of the leftmost detected edge.
#
#  <b>Output details</b>:
#
#  @li <tt>significance</tt>: the significance of the detected edge.
#  <br>



class alg__leftmost_edge(pAlarmBaseAlgorithm):

    SUPPORTED_TYPES      = ['TH1F', 'TH1D']
    SUPPORTED_PARAMETERS = ['window_half_width', 'threshold', 'start_x']
    OUTPUT_LABEL          = 'Position of the leftmost rising edge'


    def run(self):
        self.WindowHalfWidth = int(self.getParameter('window_half_width', 5))
        self.NumBins = self.RootObject.GetNbinsX()
        threshold = self.getParameter('threshold', 7)
        startX = self.getParameter('start_x', None)
        startBin = self.__getStartBin(startX)
        for i in range(startBin + self.WindowHalfWidth,\
                           self.NumBins + 1 - self.WindowHalfWidth):
	    significance = self.getEdgeSignificance(i)
	    if significance > threshold:
                self.refineEdge(i, significance)
                return
            
    def __getStartBin(self, startX):
        if startX == None:
            return 1
        else:
            for i in range(self.NumBins):
                if self.RootObject.GetBinCenter(i) > startX:
                    return i
        return 1

    def getEdgeSignificance(self, bin):
        leftSum = 0
        rightSum = 0
        for j in range(bin - self.WindowHalfWidth, bin):
            leftSum += self.RootObject.GetBinContent(j)
        for j in range(bin + 1, bin + self.WindowHalfWidth + 1):
            rightSum += self.RootObject.GetBinContent(j)
	if leftSum > rightSum:
	    return 0
        try:
	    return sqrt(self.WindowHalfWidth)*abs(rightSum - leftSum)/\
              		   sqrt(rightSum + leftSum)
        except ZeroDivisionError:
	    return 0

    def refineEdge(self, startBin, startSignificance):
        maxSignificance = startSignificance
        outputValue = self.RootObject.GetBinCenter(startBin)
        for k in range(startBin + 1, startBin + self.WindowHalfWidth + 1):
            significance = self.getEdgeSignificance(k)
            if significance > maxSignificance:
                maxSignificance = significance
                outputValue = self.RootObject.GetBinCenter(k)
        self.Output.setDictValue('significance', maxSignificance)
        self.Output.setValue(outputValue)


if __name__ == '__main__':
    import random
    from pAlarmLimits import pAlarmLimits
    canvas = ROOT.TCanvas('Test canvas', 'Test canvas', 600, 300)
    limits = pAlarmLimits(30, 40, 20, 60)

    histogram = ROOT.TH1F('h1', 'h1', 100, 0, 100)
    for i in range(1, 43):
        histogram.SetBinContent(i, random.gauss(5, sqrt(5)))
    for i in range(43, 101):
        histogram.SetBinContent(i, random.gauss(50, sqrt(50)))
    histogram.Draw()
    canvas.Update()
    pardict = {'threshold': 20}
    algorithm = alg__leftmost_edge(limits, histogram, pardict)
    algorithm.apply()
    print 'Parameters: %s\n' % pardict
    print algorithm.Output
