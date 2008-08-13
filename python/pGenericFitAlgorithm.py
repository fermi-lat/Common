from pSafeROOT           import ROOT
from pAlarmBaseAlgorithm import pAlarmBaseAlgorithm



## @brief Base "virtual" class for implementing alarms which involve fitting
#  and retrieving one of the fit parameters with associated error.
#
#  <b>Valid parameters</b>:
#
#  @li <tt>min</tt>: the minimum x value for the fit range.
#  <br>
#  @li <tt>max</tt>: the maximum x value for the fit range.
#  <br>
#  @li <tt>num_sigma</tt>: the number of sigma for the error bar.


class pGenericFitAlgorithm(pAlarmBaseAlgorithm):

    SUPPORTED_TYPES      = ['TH1F']
    SUPPORTED_PARAMETERS = ['min', 'max', 'num_sigma']
    
    def run(self, functionFormula, fitParameter):
        numSigma = self.getParameter('num_sigma', 2.0)
        fitFunction = ROOT.TF1('temp_fit_function', functionFormula)
        ([value], [error]) = self.getFitOutput(fitFunction, [fitParameter])
        error *= numSigma
        self.Output.setValue(value, error)
        fitFunction.Delete()
