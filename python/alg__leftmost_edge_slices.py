
from pSafeROOT import ROOT

from pAlarmBaseAlgorithm import pAlarmBaseAlgorithm
from alg__leftmost_edge  import alg__leftmost_edge
from pGlobals            import MINUS_INFINITY


## @brief This is an attempt to generalize the ... 
#
#  <b>Valid parameters</b>:
#
#  @li <tt></tt>:
#  <br>
#
#  @li <tt>slice_width</tt>: the width of each slice (number of bins) of the
#  2-dimensional histogram.
#  <br>
#
#  <b>Output value</b>:
#
#  The ...

class alg__leftmost_edge_slices(pAlarmBaseAlgorithm):

    SUPPORTED_TYPES      = ['TH2F']
    SUPPORTED_PARAMETERS = ['window_half_width', 'threshold', 'slice_width']
    OUTPUT_LABEL         = 'Position of the leftmost edge of the worst slice'

    def getDetailedXLabel(self, index):
        return 'slice centered at %s = %s' %\
            (self.getAxisLabel('x'), self.getFormattedX(index))

    def getDetailedLabel(self, index, value, valueLabel = None, error = None):
        return '%s, edge position = %s' % (self.getDetailedXLabel(index), value)

    def getPosition(self, index):
        return index

    def run(self):
        windowHalfWidth = self.getParameter('window_half_width', 5)
        threshold = self.getParameter('threshold', 10)
        sliceWidth = self.getParameter('slice_width', 1)
	sliceParDict = {'window_half_width': windowHalfWidth,
                        'threshold': threshold}
        i = self.RootObject.GetXaxis().GetFirst()
        lastBin = self.RootObject.GetXaxis().GetLast() - sliceWidth
        maxBadness = MINUS_INFINITY
        while(i < lastBin):
            sliceCenter = i + sliceWidth/2
            sliceHisto = self.RootObject.ProjectionY('h_single_slice', i,\
                                                         i + sliceWidth)
            sliceAlarm = alg__leftmost_edge(self.Limits, sliceHisto,\
                                                sliceParDict)
            sliceAlarm.apply()
            value = sliceAlarm.Output.Value
            if value is None:
                self.Output.appendDictValue('edgeless_slices',\
                                                self.getDetailedXLabel(i))
            else:
                badness = self.checkStatus(i, value, 'edge_position')
                if badness > maxBadness:
                    maxBadness = badness
                    outputIndex = i
                    outputValue = value
            i += sliceWidth
            sliceHisto.Delete()
        try:
            self.Output.setValue(outputValue)
            label = self.getDetailedLabel(outputIndex, outputValue)
            self.Output.setDictValue('output_point', label)
        except:
            self.Output.setWarning()
            self.Output.setDictValue('WARNING status reason',\
                                         'Could not find any edge')



if __name__ == '__main__':
    from pAlarmLimits import pAlarmLimits
    limits = pAlarmLimits(120, 170, 100, 200)
    canvas = ROOT.TCanvas('Test canvas', 'Test canvas', 400, 400)
    
    histogram = ROOT.TH2F('h', 'h', 3072, 0, 3072, 100, 0, 300)
    for i in range(3072):
        for j in range(50, 100):
            histogram.SetBinContent(i,j, 100)
    histogram.SetBinContent(10, 10, 50)
    histogram.SetBinContent(10, 11, 20)
    histogram.SetBinContent(10, 12, 23)
    histogram.SetBinContent(100, 20, 50)
    histogram.SetBinContent(100, 21, 20)
    histogram.SetBinContent(100, 22, 23)
    histogram.SetBinContent(200, 30, 50)
    histogram.SetBinContent(200, 31, 20)
    histogram.SetBinContent(200, 32, 23)
    histogram.SetBinContent(300, 40, 50)
    histogram.SetBinContent(300, 41, 20)
    histogram.SetBinContent(300, 42, 23)
    histogram.GetXaxis().SetTitle('something')
    histogram.Draw("colz")
    canvas.Update()
    algorithm = alg__leftmost_edge_slices(limits, histogram,\
                                              {'slice_width': 12})
    algorithm.apply()
    print algorithm.Output
