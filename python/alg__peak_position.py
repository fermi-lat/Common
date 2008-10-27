
from pSafeROOT           import ROOT
from pAlarmBaseAlgorithm import pAlarmBaseAlgorithm


class alg__peak_position(pAlarmBaseAlgorithm):

    SUPPORTED_TYPES      = ['TH1F', 'TH1D']
    SUPPORTED_PARAMETERS = ['num_iterations', 'fit_range_width', 'min', 'max',\
                            'num_sigma']
    OUTPUT_LABEL         = 'Position (mean) of the main peak'

    def run(self):
        numIterations = self.getParameter('num_iterations', 2)
        fitRangeWidth = self.getParameter('fit_range_width', 2.0)
        self.setNumSigma()
        meanValue = self.RootObject.GetMean()
        rmsValue = self.RootObject.GetRMS()
        gaussian = ROOT.TF1('alg__gaussian', 'gaus')
        for i in range(numIterations):
            self.ParamsDict['min'] = meanValue - fitRangeWidth*rmsValue
            self.ParamsDict['max'] = meanValue + fitRangeWidth*rmsValue
            ([meanValue, rmsValue], [meanError, rmsError]) =\
                         self.getFitOutput(gaussian, [1, 2])
        meanError *= self.NumSigma
        self.Output.setValue(meanValue, meanError)



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
    pardict = {'min': 0, 'max': 4, 'fit_range_width': 1.5, 'num_iterations': 3}
    algorithm = alg__peak_position(limits, histogram, pardict)
    algorithm.apply()
    print 'Parameters: %s\n' % algorithm.ParamsDict
    print algorithm.Output
