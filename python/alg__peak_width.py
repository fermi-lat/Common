
from pSafeROOT import ROOT

from pAlarmBaseAlgorithm import pAlarmBaseAlgorithm


class alg__peak_width(pAlarmBaseAlgorithm):

    SUPPORTED_TYPES      = ['TH1F']
    SUPPORTED_PARAMETERS = ['num_iterations', 'fit_range_width', 'min', 'max']
    OUTPUT_DICTIONARY    = {}
    OUTPUT_LABEL         = 'Width (rms) of the main peak'

    def run(self):
        numIterations = self.getParameter('num_iterations', 2)
        fitRangeWidth = self.getParameter('fit_range_width', 1.5)
        mean = self.RootObject.GetMean()
        rms = self.RootObject.GetRMS()
        self.ParamsDict['min'] = mean - fitRangeWidth*rms
        self.ParamsDict['max'] = mean + fitRangeWidth*rms
        gaussian = ROOT.TF1('alg__gaussian', 'gaus')
        (norm, mean, rms) = self.getFitParameters(gaussian)
        for i in range(numIterations):
            self.ParamsDict['min'] = mean - fitRangeWidth*rms
            self.ParamsDict['max'] = mean + fitRangeWidth*rms
            gaussian = ROOT.TF1('alg__gaussian', 'gaus')
            (norm, mean, rms) = self.getFitParameters(gaussian)
        self.Output.setValue(rms)



if __name__ == '__main__':
    from pAlarmLimits import pAlarmLimits
    limits = pAlarmLimits(1, 2, 0, 3)
    canvas = ROOT.TCanvas('Test canvas', 'Test canvas', 400, 400)

    print
    print 'Testing on a 1-dimensional histogram...'
    histogram = ROOT.TH1F('h', 'h', 100, -5, 5)
    function = ROOT.TF1('f', 'gaus')
    function.SetParameter(0, 1)
    function.SetParameter(1, -1)
    function.SetParameter(2, 1)
    histogram.FillRandom('f', 1000)
    function.SetParameter(1, 2)
    histogram.FillRandom('f', 300)
    histogram.Draw()
    canvas.Update()
    pardict = {'min': 0, 'max': 4}
    algorithm = alg__peak_width(limits, histogram, pardict)
    algorithm.apply()
    print 'Parameters: %s\n' % pardict
    print algorithm.Output
