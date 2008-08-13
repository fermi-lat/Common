from pGenericFitAlgorithm import pGenericFitAlgorithm

## @brief RMS of a gaussian fit.
#
#  <b>Valid parameters</b>:
#
#  All those inherited by the base class pGenericFitAlgorithm.
#
#  <b>Output value</b>:
#
#  The rms value of the gaussian fit in the user-defined sub-range.


class alg__gauss_rms(pGenericFitAlgorithm):

    OUTPUT_LABEL = 'RMS of the gaussian fit'

    def run(self):
        pGenericFitAlgorithm.run(self, 'gaus', 2)
        


if __name__ == '__main__':
    from pSafeROOT    import ROOT
    from pAlarmLimits import pAlarmLimits
    limits = pAlarmLimits(0.5, 1.5, 0.1, 3)
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
    algorithm = alg__gauss_rms(limits, histogram, pardict)
    algorithm.apply()
    print 'Parameters: %s\n' % pardict
    print algorithm.Output

