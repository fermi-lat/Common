import pUtils

from pSafeROOT           import ROOT
from pAlarmBaseAlgorithm import pAlarmBaseAlgorithm
from math                import sqrt
from pGlobals            import PLUS_INFINITY


## @brief Calculate the ratio between the number of entries below and above
#  a certain pivot point in a 1-dimensional histogram.
#
#  The algorithms loops over the bins of the histograms and evaluate the
#  number of entries below the and above the pivot point (possibly limiting
#  the overall range between a minimum and a maximum value) and returns the
#  ratio between those two numbers. It is handy for those histograms that look
#  like power laws, in which the average and the rms do not convey enough
#  information.
#
#  The pivot point (as well as xmin and xmax, if defined), does not generally
#  coincide with one of the bin edges. In those cases the content of the bin
#  is splot assuming that the enetries are uniformily distributed within the
#  bin itself (which, depending on the case, might be a crude appoximation).
#
#  In case the denominator of the ratio is zero, both the output value and the
#  output error are set to \ref PLUS_INFINITE. Alarms should be configured
#  in such a way that this is not often the case in order to be effective.
#
#  <b>Valid parameters</b>:
#
#  @li <tt>pivot</tt>: the pivot point.
#  <br>
#  @li <tt>min</tt>: the minimum x value used for the calculation.
#  <br>
#  @li <tt>max</tt>: the maximum x value used for the calculation.
#
#  <b>Output value</b>:
#
#  The ratio between the number of entries in [xmin, pivot] and [pivot, xmax]
#  intervals.


class alg__low_high_ratio(pAlarmBaseAlgorithm):

    SUPPORTED_TYPES      = ['TH1D', 'TH1F']
    SUPPORTED_PARAMETERS = ['pivot', 'min', 'max']
    OUTPUT_LABEL         = 'The ratio of entries below and above the pivot'

    def getLowFraction(self, lowEdge, highEdge):
        if lowEdge >= self.Min and highEdge <= self.Pivot:
            return 1.0
        elif lowEdge <= self.Min and highEdge >= self.Min:
            return highEdge - self.Min
        elif lowEdge <= self.Pivot and highEdge >= self.Pivot:
            return self.Pivot - lowEdge
        else:
            return 0

    def getHighFraction(self, lowEdge, highEdge):
        if lowEdge >= self.Pivot and highEdge <= self.Max:
            return 1.0
        elif lowEdge <= self.Pivot and highEdge >= self.Pivot:
            return highEdge - self.Pivot
        elif lowEdge <= self.Max and highEdge >= self.Max:
            return self.Max - lowEdge
        else:
            return 0

    def run(self):
        self.Pivot = self.getParameter('pivot', None)
        if self.Pivot is None:
            self.Output.setError('Pivot point not defined')
            return
        self.Min = self.getParameter('min',
                                     self.RootObject.GetXaxis().GetXmin())
        self.Max = self.getParameter('max',
                                     self.RootObject.GetXaxis().GetXmax())
        minBinFound = False
        maxBinFound = False
        numBins = self.RootObject.GetNbinsX()
        lowSum = 0.0
        lowError = 0.0
        highSum = 0.0
        highError = 0.0
        for i in range(1, numBins + 1):
            binCenter = self.RootObject.GetBinCenter(i)
            binWidth = self.RootObject.GetBinWidth(i)
            binLowEdge = binCenter - binWidth/2.
            binHighEdge = binCenter + binWidth/2.
            binContent = self.RootObject.GetBinContent(i)
            if not minBinFound and binHighEdge > self.Min:
                minBinFound = True
            if not maxBinFound and binLowEdge > self.Max:
                maxBinFound = True
            if minBinFound and not maxBinFound:
                lowFraction = self.getLowFraction(binLowEdge, binHighEdge)
                highFraction = self.getHighFraction(binLowEdge, binHighEdge)
                lowSum += binContent*lowFraction
                lowError += binContent*lowFraction*lowFraction
                highSum += binContent*highFraction
                highError += binContent*highFraction*highFraction
        try:
            ratioValue = lowSum/highSum
            ratioError = ratioValue*sqrt(lowError/(lowSum*lowSum) +\
                                             highError/(highSum*highSum))
        except ZeroDivisionError:
            ratioValue = PLUS_INFINITY
            ratioError = PLUS_INFINITY
        self.Output.setDictValue('Integral between %s and %s' %\
                                 (pUtils.formatNumber(self.Min),
                                  pUtils.formatNumber(self.Pivot)),
                                 pUtils.formatNumber(lowSum))
        self.Output.setDictValue('Integral between %s and %s' %\
                                 (pUtils.formatNumber(self.Pivot),
                                  pUtils.formatNumber(self.Max)),
                                 pUtils.formatNumber(highSum))
        self.Output.setValue(ratioValue, ratioError)



if __name__ == '__main__':
    from pAlarmLimits import pAlarmLimits
    canvas = ROOT.TCanvas('Test canvas', 'Test canvas', 600, 300)
    limits = pAlarmLimits(1, 5, 0, 10)

    histogram = ROOT.TH1F('h1', 'h1', 100, 0, 100)
    powerLaw = ROOT.TF1('powerLaw', '[0]*x**(-[1])', 0, 100)
    powerLaw.SetParameter(0, 1.0)
    powerLaw.SetParameter(1, 1.0)
    histogram.FillRandom('powerLaw', 100000)
    histogram.Draw()
    canvas.SetLogy(True)
    canvas.Update()

    pardict = {'pivot': 50, 'min': 10.5, 'max': 85.5}
    #pardict = {'min': 10.5, 'max': 85.5}
    algorithm = alg__low_high_ratio(limits, histogram, pardict)
    algorithm.apply()
    print 'Parameters: %s\n' % algorithm.ParamsDict
    print algorithm.Output
