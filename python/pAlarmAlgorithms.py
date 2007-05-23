
## @package pAlarmAlgorithms
## @brief Definition of the algorithms for the alarm implemetation.

import logging
import ROOT


## @brief Check a set of parameter names against the valid parameters
#  for a particular algorithms.
#
#  Return True if the check fails, False otherwise.
## @param parametersDict
#  The dictionary of parameters, as passed by the xml parser.
## @param validParams
#  The list of valid parameter names.
## @param functionName
#  The name of the caller function.
#
#  Used for debug in case the check fails.

def invalidParameters(parametersDict, validParams, functionName):
    for paramName in parametersDict.keys():
        if paramName not in validParams:
            logging.error('Invalid parameter (%s) in function %s found.' %\
                          (paramName, functionName))
	    return True
    return False

## @brief Print an error message and return None.
## @param functionName
#  The name of the caller function.
## @param plotName
#  The plot name.

def exitOnError(functionName, plotName):
    logging.error('Could not apply %s on %. Returning None...' %\
                  (functionName, plotName))
    return None

## @brief Set the x range of a ROOT plot according to a dictionary of
#  parameters.
#
#  If the dictionary of parameters has the 'min' ('max') key, then
#  the x min (max) of the plot is set the corresponding dictionary value.
#  The command is ignored otherwise.
## @param plot
#  The ROOT object.
## @param paramsDict
#  The parameters dictionary.

def setRangeX(plot, paramsDict):
    try:
        xMin = paramsDict['min']
    except KeyError:
        xMin = plot.GetXaxis().GetXmin()
    try:
        xMax = paramsDict['max']
    except KeyError:
        xMax = plot.GetXaxis().GetXmax()
    plot.GetXaxis().SetRangeUser(xMin, xMax)

## @brief Reset the x range of a ROOT plot.
## @param plot
#  The ROOT object.

def resetRangeX(plot):
    plot.GetXaxis().SetRange(1, 0)

## @brief Return the average of the histogram on the x axis.
#
#  The average value is retrieved through the ROOT TH1::GetMean() method.
#  In case the <tt>min</tt> or <tt>max</tt> parameters are specified,
#  the range is properly set, first. At the end the range is reset anyway.
#
#  Valid parameters:
#  @li <tt>min</tt>: the minimum x value for the average calculation.
#  @li <tt>max</tt>: the maximum x value for the average calculation.
#
## @param plot
#  The ROOT object.
## @param paramsDict
#  The (optional) dictionary of parameters.

def x_average(plot, paramsDict={}):
    functionName = 'x_average'
    if invalidParameters(paramsDict, ['min', 'max'], functionName):
        return None
    try:
        setRangeX(plot, paramsDict)
        outputValue = plot.GetMean()
        resetRangeX(plot)
        return outputValue
    except:
        return exitOnError(functionName, plot.GetName())

## @brief Return the RMS on the x axis.
#
#  The average value is retrieved through the ROOT TH1::GetRMS() method.
#  In case the <tt>min</tt> or <tt>max</tt> parameters are specified,
#  the range is properly set, first. At the end the range is reset anyway.
#
#  Valid parameters:
#  @li <tt>min</tt>: the minimum x value for the rms calculation.
#  @li <tt>max</tt>: the maximum x value for the rms calculation.
#
## @param plot
#  The ROOT object.
## @param paramsDict
#  The (optional) dictionary of parameters.

def x_rms(plot, paramsDict={}):
    functionName = 'x_rms'
    if invalidParameters(paramsDict, ['min', 'max'], functionName):
        return None
    try:
        setRangeX(plot, paramsDict)
        outputValue = plot.GetRMS()
        resetRangeX(plot)
        return outputValue
    except:
        return exitOnError(functionName, plot.GetName())

## @brief Return position of the center of the first populated bin of
#  the histogram on the x axis.
#
#  Valid parameters: None.
#
## @param plot
#  The ROOT object.
## @param paramsDict
#  The (optional) dictionary of parameters.

def x_min_bin(plot, paramsDict={}):
    functionName = 'x_min_bin'
    if invalidParameters(paramsDict, [], functionName):
        return None
    try:
        for bin in range(plot.GetXaxis().GetFirst(),\
                         plot.GetXaxis().GetLast()):
            if plot.GetBinContent(bin) > 0:
                return plot.GetBinCenter(bin)
    except:
        return exitOnError(functionName, plot.GetName())

## @brief Return position of the center of the last populated bin of
#  the histogram on the x axis.
#
#  Valid parameters: None.
#
## @param plot
#  The ROOT object.
## @param paramsDict
#  The (optional) dictionary of parameters.

def x_max_bin(plot, paramsDict={}):
    functionName = 'x_max_bin'
    if invalidParameters(paramsDict, [], functionName):
        return None
    try:
        for bin in range(plot.GetXaxis().GetLast(),\
                         plot.GetXaxis().GetFirst(), -1):
            if plot.GetBinContent(bin) > 0:
                return plot.GetBinCenter(bin)
    except:
        return exitOnError(functionName, plot.GetName())

## @brief Return the mean of a gaussian fit to the plot.
#
#  @todo Implement support for fitting in a subrange (min and max not
#  used, at the moment).
#
#  Valid parameters:
#  @li <tt>min</tt>: the minimum x value for the fit.
#  @li <tt>max</tt>: the maximum x value for the fit.
#
## @param plot
#  The ROOT object.
## @param paramsDict
#  The (optional) dictionary of parameters.

def gauss_mean(plot, paramsDict={}):
    functionName = 'gauss_mean'
    if invalidParameters(paramsDict, [], functionName):
        return None
    try:
        gaussian = ROOT.TF1('g', 'gaus')
        plot.Fit(gaussian, 'QN')
        outputValue = gaussian.GetParameter(1)
        return outputValue
    except:
        return exitOnError(functionName, plot.GetName())

## @brief Return the rms of a gaussian fit to the plot.
#
#  @todo Implement support for fitting in a subrange (min and max not
#  used, at the moment).
#
#  Valid parameters:
#  @li <tt>min</tt>: the minimum x value for the fit.
#  @li <tt>max</tt>: the maximum x value for the fit.
#
## @param plot
#  The ROOT object.
## @param paramsDict
#  The (optional) dictionary of parameters.

def gauss_rms(plot, paramsDict={}):
    functionName = 'gauss_rms'
    if invalidParameters(paramsDict, [], functionName):
        return None
    try:
        gaussian = ROOT.TF1('g', 'gaus')
        plot.Fit(gaussian, 'QN')
        outputValue = gaussian.GetParameter(2)
        return outputValue
    except:
        return exitOnError(functionName, plot.GetName())
