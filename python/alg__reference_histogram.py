

import math

from pSafeROOT           import ROOT
from pAlarmBaseAlgorithm import pAlarmBaseAlgorithm, logger
from pUtils              import formatNumber
from pGlobals            import MINUS_INFINITY


## @brief Comparison against a reference histogram.
#
#  It's a variant of the chisquare test in which the comparison is made
#  bin per bin, after the histogram under study has been scaled (in terms
#  of the number of entries) to the reference histogram---we are assuming here
#  that the reference histogram does not have less entries that the object
#  the alarm is set on (so that the scaling factor is typically greater
#  than 1).
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
#  is compared with the scaled number of entries in the corresponding bin of
#  the histogram under test:
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
#  <b>Valid parameters</b>:
#
#  @li <tt>ref_folder_path</tt>: the path to the directory containing the ROOT
#  files in which the reference histograms are stored. If not set the path
#  set via the -R command line switch of aPalarmHandler is used instead
#  (typical case).
#  <br>
#  @li <tt>ref_file_name</tt>: the name of the ROOT file containing the
#  reference histogram (mandatory).
#  <br>
#  @li <tt>ref_plot_name</tt>: the name of the plot in the ROOT file to
#  compare with. If not set, the same name of the root object the alarm is
#  set on is used (typical case).
#  <br>
#
#  <b>Output value</b>:
#
#  The significance of the <em>worst</em> bin (the one with the most
#  significance difference).
#
#  <b>Output details</b>:
#
#  @li <tt>num_warning_entries</tt>: the number of bins for which the
#  statistical significance of the difference produces a warning.
#  <br>
#  @li <tt>num_error_entries</tt>: the number of bins for which the statistical
#  significance of the difference produces an error.
#  <br>
#  @li <tt>warning_entries</tt>: a list of all the bins producing a warning.
#  Each element of the list is a string which should be self-explaining.
#  <br>
#  @li <tt>error_entries</tt>: a list of all the bins producing a warning. Each
#  element of the list is a string which should be self-explaining.
#  <br>
#  @li <tt>chisquare</tt>: the chisquare of the fit to the residuals with 
#  a constant (null) function.
#  <br>
#  @li <tt>reduced_chisquare</tt>: the reduced chisquare of the fit to the
#  residuals with a constant (null) function. 
#  <br>
# 
## @todo Update documentations.



class alg__reference_histogram(pAlarmBaseAlgorithm):

    SUPPORTED_TYPES      = ['TH1F', 'TH1D']
    SUPPORTED_PARAMETERS = ['ref_folder_path', 'ref_file_name',
                            'ref_plot_name']
    OUTPUT_LABEL         = 'Significance of the maximum bin difference'

    def __init__(self, limits, object, paramsDict, conditionsDict = {}):
        pAlarmBaseAlgorithm.__init__(self, limits, object, paramsDict,\
                                         conditionsDict)
        self.ReferenceFolderPath = self.getParameter('ref_folder_path', None)
        self.ReferenceFileName = self.getParameter('ref_file_name', None)
        self.ReferencePlotName = self.getParameter('ref_plot_name', None)
        self.ReferenceHistogramsDict = None
        self.ReferenceFile = None

    def setReferenceDict(self, referenceDict):
        self.ReferenceHistogramsDict = referenceDict
        
    def getExpectedValue(self, bin):
        return self.ReferenceObject.GetBinContent(bin)*self.ScaleFactor

    def getExpectedError(self, bin):
        return self.ReferenceObject.GetBinError(bin)*self.ScaleFactor

    def getObservedValue(self, bin):
        return self.RootObject.GetBinContent(bin)

    def getObservedError(self, bin):
        return self.RootObject.GetBinError(bin)

    def setupReference(self):
        if self.ReferenceFileName is None:
            logger.error('Reference file name undefined, skipping.')
            self.Output.setError('Reference file name undefined.')
            return 1
        if self.ReferencePlotName is None:
            self.ReferencePlotName = self.RootObject.GetName()
        if self.ReferenceFolderPath is not None:
            referenceFilePath = os.path.join(self.ReferenceFolderPath,\
                                             self.ReferenceFileName)
            self.ReferenceFile = ROOT.TFile(referenceFilePath)
        else:
            try:
                self.ReferenceFile =\
                     self.ReferenceHistogramsDict[self.ReferenceFileName]
            except KeyError:
                logger.error('Reference histogram dict has no key "%s".' %
                             self.ReferenceFileName)
            except:
                pass
        if self.ReferenceFile is None or self.ReferenceFile.IsZombie():
            logger.error('Could not get reference file, skipping.')
            self.Output.setError('Could not get reference file.')
            return 1
        self.ReferenceObject = self.ReferenceFile.Get(self.ReferencePlotName)
        if self.ReferenceObject is None:
            logger.error('Could not get reference plot "%s", skipping.' %\
                         self.ReferencePlotName)
            self.Output.setError('Could not get reference plot.')
            return 1
        return 0

    def run(self):
        if self.setupReference():
            return
        self.ScaleFactor = self.RootObject.GetEntries()/\
            float(self.ReferenceObject.GetEntries())
        numBins = self.ReferenceObject.GetNbinsX()
        if self.RootObject.GetNbinsX() != numBins:
            logger.error('Mismatch in bins while comparing histograms.')
            self.Output.setError('Histogram bins mismatch.')
            return
        chiSquare = 0
        numDof = 0
        maxBadness = MINUS_INFINITY
        outputDelta = 0
        outputBin = 0
        worstDelta = 0
        worstBin = 0
        for i in range(numBins + 2):
            expValue = self.getExpectedValue(i)
            expErr = self.getExpectedError(i)
            obsValue = self.getObservedValue(i)
            obsErr = self.getObservedError(i)
            try:
                delta = ((expValue - obsValue)**2.0)/(expErr**2 + obsErr**2)
                numDof += 1
                chiSquare += delta
            except ZeroDivisionError:
                delta = 0
            delta = math.sqrt(delta)
            badness = self.checkStatus(i, delta, 'difference significance')
            if badness > maxBadness:
                maxBadness = badness
                outputDelta = delta
                outputBin = i
            if delta > worstDelta:
                worstDelta = delta
                worstBin = i
        try:
            redChiSquare = chiSquare/float(numDof)
        except ZeroDivisionError:
            redChiSquare = 0
        self.Output.setDictValue('chisquare', formatNumber(chiSquare))
        self.Output.setDictValue('red_chisquare', formatNumber(redChiSquare))
        self.Output.setDictValue('dof', formatNumber(numDof))
        label = self.getDetailedLabel(outputBin, outputDelta, 'delta')
        label += ' (exp. %s +- %s, obs. %s +- %s)' %\
            (formatNumber(self.getExpectedValue(outputBin)),
             formatNumber(self.getExpectedError(outputBin)),
             formatNumber(self.getObservedValue(outputBin)),
             formatNumber(self.getObservedError(outputBin)))
        self.Output.setDictValue('output_bin', label)
        label = self.getDetailedLabel(worstBin, worstDelta, 'delta')
        label += ' (exp. %s +- %s, obs. %s +- %s)' %\
            (formatNumber(self.getExpectedValue(worstBin)),
             formatNumber(self.getExpectedError(worstBin)),
             formatNumber(self.getObservedValue(worstBin)),
             formatNumber(self.getObservedError(worstBin)))
        self.Output.setDictValue('worst_bin', label)
        self.Output.setValue(outputDelta, None, maxBadness)
        if self.ReferenceFolderPath is not None:
            try:
                self.ReferenceFile.Close()
            except:
                pass



if __name__ == '__main__':
    import os
    from pAlarmLimits import pAlarmLimits
    canvas = ROOT.TCanvas('Test canvas', 'Test canvas', 600, 300)
    canvas.Divide(2, 1)
    limits = pAlarmLimits(-100000, 3, -100000, 6)

    referenceFolderPath = './'
    referenceFileName = 'reference.root'
    referenceFilePath = os.path.join(referenceFolderPath, referenceFileName)
    referenceName = 'reference'
    referenceFile = ROOT.TFile(referenceFilePath, 'RECREATE')
    referenceHistogram = ROOT.TH1F(referenceName, referenceName, 10, -5, 5)
    referenceHistogram.FillRandom('pol0', 1000000)
    referenceHistogram.SetMinimum(0)
    referenceHistogram.Write()
    canvas.cd(1)
    referenceHistogram.DrawCopy()
    canvas.Update()
    referenceFile.Close()
    del referenceHistogram

    canvas.cd(2)
    histogram = ROOT.TH1F('h', 'h', 10, -5, 5)
    histogram.FillRandom('pol0', 10000)
    histogram.SetMinimum(0)
    histogram.Draw()
    canvas.Update()

    pardict = {'ref_folder_path': referenceFolderPath,
               'ref_file_name': referenceFileName,
               'ref_plot_name': referenceName}
    algorithm = alg__reference_histogram(limits, histogram, pardict)
    algorithm.apply()
    print 'Parameters: %s\n' % algorithm.ParamsDict
    print algorithm.Output
    import os
    os.system('rm -f %s' % referenceFilePath)

