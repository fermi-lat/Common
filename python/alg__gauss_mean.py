from pGenericFitAlgorithm import pGenericFitAlgorithm

## @brief Mean value of a gaussian fit.
#
#  <b>Valid parameters</b>:
#
#  All those inherited by the base class pGenericFitAlgorithm.
#
#  <b>Output value</b>:
#
#  The mean value of the gaussian fit in the user-defined sub-range.


class alg__gauss_mean(pGenericFitAlgorithm):

    OUTPUT_LABEL = 'Mean of the gaussian fit'

    def run(self):
        pGenericFitAlgorithm.run(self, 'gaus', 1)



if __name__ == '__main__':
    from pSafeROOT    import ROOT
    from pAlarmLimits import pAlarmLimits
    limits = pAlarmLimits(1, 2, 0, 3)
    canvas = ROOT.TCanvas('Test canvas', 'Test canvas', 400, 400)
    print
    print 'Testing on a 1-dimensional histogram...'
    histogram = ROOT.TH1F('h', 'h', 100, -5, 5)
    function = ROOT.TF1('f', 'gaus')
    function.SetParameter(0, 1)
    function.SetParameter(1, 2)
    function.SetParameter(2, 1)
    histogram.FillRandom('f', 1000)
    function.SetParameter(1, -2)
    histogram.FillRandom('f', 1000)
    histogram.Draw()
    canvas.Update()
    pardict = {'min': 0, 'max': 4}
    algorithm = alg__gauss_mean(limits, histogram, pardict)
    algorithm.apply()
    print 'Parameters: %s\n' % algorithm.ParamsDict
    print algorithm.Output
