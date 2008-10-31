from pGenericFitAlgorithm import pGenericFitAlgorithm

## @brief Mean value of a gaussian fit.
#
#  <b>Valid parameters</b>:
#
#  All those inherited by the base class pGenericFitAlgorithm.
#
#  <b>Output value</b>:
#
#  The lambda returned by a fit with an exponential function in the
#  user-defined sub-range.


class alg__exponential_lambda(pGenericFitAlgorithm):

    OUTPUT_LABEL = 'Lambda of the exponential fit'

    def run(self):
        pGenericFitAlgorithm.run(self, 'expo', 1)


if __name__ == '__main__':
    from pSafeROOT    import ROOT
    from pAlarmLimits import pAlarmLimits
    limits = pAlarmLimits(1, 2, 0, 3)
    canvas = ROOT.TCanvas('Test canvas', 'Test canvas', 400, 400)
    print
    print 'Testing on a 1-dimensional histogram...'
    histogram = ROOT.TH1F('h', 'h', 100, 0, 5)
    function = ROOT.TF1('f', '[0]*exp(-x/[1])')
    function.SetParameter(0, 1)
    function.SetParameter(1, 2)
    histogram.FillRandom('f', 10000)
    histogram.Draw()
    canvas.Update()
    pardict = {'min': 0, 'max': 4}
    algorithm = alg__exponential_lambda(limits, histogram, pardict)
    algorithm.apply()
    print 'Parameters: %s\n' % algorithm.ParamsDict
    print algorithm.Output
