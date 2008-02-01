
from pSafeROOT import ROOT

from pAlarmBaseAlgorithm import pAlarmBaseAlgorithm
from math                import sqrt


## @brief 
#
#  <b>Output value</b>:
#
#  
#
#  <b>Output details</b>:
#
#  @li <tt></tt>:



class alg__reference_histogram(pAlarmBaseAlgorithm):

    SUPPORTED_TYPES      = ['TH1F']
    SUPPORTED_PARAMETERS = ['reference_path', 'reference_name']
    OUTPUT_DICTIONARY    = {'num_warning_bins': 0,
                            'num_error_bins'  : 0,
                            'warning_bins'    : [],
                            'error_bins'      : []
                            }
    OUTPUT_LABEL         = 'Significance of the maximum bin difference'

    def run(self):
        referenceFilePath = self.ParamsDict['reference_path']
        referenceName = self.ParamsDict['reference_name']
        referenceFile = ROOT.TFile(referenceFilePath)
        referenceObject = referenceFile.Get(referenceName)
        numBins = referenceObject.GetNbinsX()
        if self.RootObject.GetNbinsX() != numBins:
            logging.error('Mismatch in bins while comparing histograms.')
            return
        numEntriesRef = referenceObject.GetEntries()
        numEntriesObj = self.RootObject.GetEntries()
        scaleFactor = float(numEntriesRef)/numEntriesObj
        binsContentRef = []
        binsContentObj = []
        for i in range(numBins + 2):
            binsContentRef.append(referenceObject.GetBinContent(i))
            binsContentObj.append(self.RootObject.GetBinContent(i))
        referenceFile.Close()
        deltas = [0.0]
        for i in range(numBins + 2):
            expected = binsContentRef[i]
            observed = binsContentObj[i]
            delta = abs(expected - observed*scaleFactor)
            try:
                delta /= sqrt(expected + observed*scaleFactor*scaleFactor)
            except ZeroDivisionError:
                pass
            deltas.append(delta)
            x = self.RootObject.GetBinCenter(i)
            binString = 'bin @ %.2f, significance = %.2f' %\
                        (x, delta)
            if delta > self.Limits.ErrorMax:
                self.Output.incrementDictValue('num_error_bins')
                self.Output.appendDictValue('error_bins', binString)
            elif delta > self.Limits.WarningMax:
                self.Output.incrementDictValue('num_warning_bins')
                self.Output.appendDictValue('warning_bins', binString)
        self.Output.setValue(max(deltas))

        



if __name__ == '__main__':
    from pAlarmLimits import pAlarmLimits
    canvas = ROOT.TCanvas('Test canvas', 'Test canvas', 600, 300)
    canvas.Divide(2, 1)
    limits = pAlarmLimits(-1, 3, -1, 6)

    referenceFilePath = './reference.root'
    referenceName = 'reference'
    referenceFile = ROOT.TFile(referenceFilePath, 'RECREATE')
    referenceHistogram = ROOT.TH1F(referenceName, referenceName, 10, -5, 5)
    referenceHistogram.FillRandom('pol0', 100000)
    referenceHistogram.SetMinimum(0)
    referenceHistogram.Write()
    canvas.cd(1)
    referenceHistogram.DrawCopy()
    canvas.Update()
    referenceFile.Close()
    del referenceHistogram

    canvas.cd(2)
    histogram = ROOT.TH1F('h', 'h', 10, -5, 5)
    histogram.FillRandom('pol1', 10000)
    histogram.SetMinimum(0)
    histogram.Draw()
    canvas.Update()

    pardict = {'reference_path': referenceFilePath,\
               'reference_name': referenceName}
    algorithm = alg__reference_histogram(limits, histogram, pardict)
    algorithm.apply()
    print algorithm.Output
    import os
    os.system('rm -f %s' % referenceFilePath)

