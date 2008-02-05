
import pUtils

from pSafeROOT           import ROOT
from pAlarmBaseAlgorithm import pAlarmBaseAlgorithm
from math                import sqrt


## @brief Comparison against a reference histogram.
#
#  It's a variant of the chisquare test in which the comparison is made
#  bin per bin, after the histogram under study has been scaled (in terms
#  of the number of entries) to the reference histogram---we are assuming here
#  that the reference histogram does not have less entries that the object
#  the alarm is set on (so that the scaling factor is typically greater than 1).
#
#  More precisely the scaling factor f is given, in terms of the total number
#  of entries in the histograms, by:
#  @f[
#  f = \frac{N_{\rm ref}}{N_{\rm test}}
#  @f]
#  The, for a fixed bin, the number of entries for the reference histogram:
#  @f[
#  n_{\rm ref} \pm \Delta n_{\rm ref}
#  @f]
#  is compared with the scaled number of entries in the corresponding bin of the
#  histogram under test:
#  @f[
#  f \cdot n_{\rm test} \pm f \cdot \Delta n_{\rm test}
#  @f]
#  and the significance s of the difference is given by:
#  @f[ 
#  s = \frac{\left| n_{\rm ref} - f \cdot n_{\rm test} \right|}
#  {\sqrt{ (\Delta n_{\rm ref})^2 +  (f \cdot \Delta n_{\rm test})^2 }}
#  @f]
#  In both cases the bin error is retrieved through the ROOT
#  TH1::GetBinError(binNumber) function so that each time the bin error is
#  properly set at creation time, the algorithm should in principle work.
#
#  <b>Output value</b>:
#
#  The significance of the <em>worst</em> bin (the one with the most
#  significance difference).
#
#  <b>Output details</b>:
#
#  @li <tt>num_warning_bins</tt>: the number of bins for which the statistical
#  significance of the difference produces a warning.
#  <br/>
#  @li <tt>num_error_bins</tt>: the number of bins for which the statistical
#  significance of the difference produces an error.
#  <br/>
#  @li <tt>warning_bins</tt>: a list of all the bins producing a warning. Each
#  element of the list is a string which should be self-explaining.
#  <br/>
#  @li <tt>error_bins</tt>: a list of all the bins producing a warning. Each
#  element of the list is a string which should be self-explaining.
#  <br/>



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
        deltas = [0.0]
        for i in range(numBins + 2):
            numExp = referenceObject.GetBinContent(i)
            errExp = referenceObject.GetBinError(i)
            numObs = self.RootObject.GetBinContent(i)*scaleFactor
            errObs = self.RootObject.GetBinError(i)*scaleFactor
            try:
                delta = abs(numExp - numObs)/sqrt(errExp**2 + errObs**2)
            except ZeroDivisionError:
                delta = 0
            deltas.append(delta)
            x = self.RootObject.GetBinCenter(i)
            binString = 'bin @ %s, significance = %s' %\
                (pUtils.formatNumber(x), pUtils.formatNumber(delta))
            if delta > self.Limits.ErrorMax:
                self.Output.incrementDictValue('num_error_bins')
                self.Output.appendDictValue('error_bins', binString)
            elif delta > self.Limits.WarningMax:
                self.Output.incrementDictValue('num_warning_bins')
                self.Output.appendDictValue('warning_bins', binString)
        self.Output.setValue(max(deltas))
        referenceFile.Close()
        



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

