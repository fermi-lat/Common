
from pSafeROOT import ROOT

from pAlarmBaseAlgorithm import pAlarmBaseAlgorithm



## @brief Return position of the center of the last populated bin of
#  the histogram on the x axis minus the center of the first populated bin of
#  the histogram on the x.
#
#  <b>Output value</b>:
#
#  Distance between the first and last populated bins.



class alg__x_max_minus_min_bin(pAlarmBaseAlgorithm):

    SUPPORTED_TYPES      = ['TH1F', 'TH1D']
    SUPPORTED_PARAMETERS = []
    OUTPUT_LABEL         = 'Distance between first and last populated bin'

    def run(self):
        lastBin  = -1
        firstBin = -1
        for bin in range(self.RootObject.GetXaxis().GetLast(),\
                         self.RootObject.GetXaxis().GetFirst() - 1, - 1):
            if self.RootObject.GetBinContent(bin) > 0:
                lastBin = bin
                break
        for bin in range(self.RootObject.GetXaxis().GetFirst(),\
                         self.RootObject.GetXaxis().GetLast() + 1):
            if self.RootObject.GetBinContent(bin) > 0:
                firstBin = bin
                break
        if(lastBin == - 1 or firstBin == - 1):
            delta = -1
        else:
            delta = self.RootObject.GetBinCenter(lastBin) -\
                    self.RootObject.GetBinCenter(firstBin)
        self.Output.setValue(delta)


if __name__ == '__main__':
    from pAlarmLimits import pAlarmLimits
    limits = pAlarmLimits(-4, 4, -5, 5)
    canvas = ROOT.TCanvas('Test canvas', 'Test canvas', 400, 400)

    histogram = ROOT.TH1F('h', 'h', 100, -5, 5)
    histogram.FillRandom('gaus', 1000)
    histogram.Draw()
    canvas.Update()
    algorithm = alg__x_max_minus_min_bin(limits, histogram, {})
    algorithm.apply()
    print 'Parameters: %s\n' % algorithm.ParamsDict
    print algorithm.Output
