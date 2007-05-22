import logging
import ROOT


def invalidParameters(parametersDict, validParams, functionName):
    for paramName in parametersDict.keys():
        if paramName not in validParams:
            logging.error('Invalid parameter (%s) in function %s found.' %\
                          (paramName, functionName))
	    return True
    return False

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

def resetRangeX(plot):
    plot.GetXaxis().SetRange(1, 0)

def x_average(plot, paramsDict={}):
    if invalidParameters(paramsDict, ['min', 'max'], 'x_average'):
        return None
    setRangeX(plot, paramsDict)
    outputValue = plot.GetMean()
    resetRangeX(plot)
    return outputValue

def x_rms(plot, paramsDict={}):
    if invalidParameters(paramsDict, ['min', 'max'], 'x_rms'):
        return None
    setRangeX(plot, paramsDict)
    outputValue = plot.GetRMS()
    resetRangeX(plot)
    return outputValue

def x_min_bin(plot, paramsDict={}):
    if invalidParameters(paramsDict, [], 'x_min_bin'):
        return None
    for bin in range(plot.GetXaxis().GetFirst(),\
                     plot.GetXaxis().GetLast()):
        if plot.GetBinContent(bin) > 0:
            return plot.GetBinCenter(bin)

def x_max_bin(plot, paramsDict={}):
    if invalidParameters(paramsDict, [], 'x_max_bin'):
        return None
    for bin in range(plot.GetXaxis().GetLast(),\
                     plot.GetXaxis().GetFirst(), -1):
        if plot.GetBinContent(bin) > 0:
            return plot.GetBinCenter(bin)

def gauss_mean(plot, paramsDict={}):
    gaussian = ROOT.TF1('g', 'gaus')
    plot.Fit(gaussian, 'QN')
    outputValue = gaussian.GetParameter(1)
    return outputValue

def gauss_rms(plot, paramsDict={}):
    gaussian = ROOT.TF1('g', 'gaus')
    plot.Fit(gaussian, 'QN')
    outputValue = gaussian.GetParameter(2)
    return outputValue
