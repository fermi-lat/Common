from pSafeROOT           import ROOT
from pAlarmBaseAlgorithm import pAlarmBaseAlgorithm

import pUtils


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

    SUPPORTED_TYPES      = ['TH1F', 'TH1D']
    SUPPORTED_PARAMETERS = ['min', 'max', 'num_sigma']
    
    def run(self, functionFormula, fitParameter):
        self.setNumSigma()
        fitFunction = ROOT.TF1('temp_fit_function', functionFormula)
        ([value], [error]) = self.getFitOutput(fitFunction, [fitParameter])
        error *= self.NumSigma
        self.Output.setValue(value, error)
        chiSquare = fitFunction.GetChisquare()
        dof = fitFunction.GetNDF()
        try:
            reducedChiSquare = chiSquare/dof
        except ZeroDivisionError:
            reducedChiSquare = 0
        self.Output.setDictValue('Reduced chi square',
                                 pUtils.formatNumber(reducedChiSquare))
        self.Output.setDictValue('Degrees of freedom', dof)
        fitFunction.Delete()
