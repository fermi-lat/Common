
from pSafeROOT import ROOT

from pAlarmBaseAlgorithm import pAlarmBaseAlgorithm


## @brief Check the number of entries---within specified limits on the
#  x-axis---for a 1-dimensional histogram.
#
#  At the moment only one dimensional histograms are supported. 2-dimensional
#  histogram can be added, if usefull, paying attention to the fact that
#  the machinery for being able to set the range on the x and y axes
#  separately must be added, as well.
#
#  <b>Valid parameters</b>:
#
#  @li <tt>min</tt>: the minimum value on the x-axis when setting the range.
#  <br/>
#  @li <tt>max</tt>: the minimum value on the x-axis when setting the range.
#
#  Note that in case only <tt>min</tt> or <tt>max</tt> is passed, the other
#  limit stays unchanged.
#
#  <b>Output value</b>:
#
#  The number of entries lying within the specified limits (if any).


class alg__num_entries(pAlarmBaseAlgorithm):

    SUPPORTED_TYPES      = ['TH1F']
    SUPPORTED_PARAMETERS = ['min', 'max']
    OUTPUT_DICTIONARY    = {}
    OUTPUT_LABEL         = 'Number of entries in the specified range'

    def run(self):
        self.adjustXRange()
        self.Output.setValue(self.RootObject.GetEffectiveEntries())
        self.resetXRange()



if __name__ == '__main__':
    from pAlarmLimits import pAlarmLimits
    canvas = ROOT.TCanvas('Test canvas', 'Test canvas', 400, 400)
    limits = pAlarmLimits(0, 100, 0, 500)

    print
    print 'Testing on a 1-dimensional histogram...'
    histogram1d = ROOT.TH1F('h1d', 'h1d', 10, -5, 5)
    histogram1d.FillRandom('pol0', 200)
    histogram1d.Draw()
    canvas.Update()
    pardict1d = {'min': -2, 'max': 2}
    algorithm1d = alg__num_entries(limits, histogram1d, pardict1d)
    algorithm1d.apply()
    print 'Parameters: %s\n' % pardict1d
    print algorithm1d.Output
