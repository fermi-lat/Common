import logging


def invalidParameters(parametersDict, validParams, functionName):
    for paramName in parametersDict.keys():
        if paramName not in validParams:
            logging.error('Invalid parameter (%s) in function %s found.' %\
                          (paramName, functionName))
	    return True
    return False

def x_average(plot, paramsDict={}):
    if invalidParameters(paramsDict, ['min', 'max'], 'x_average'):
        return None
    outputValue = plot.GetMean()
    return outputValue


def x_rms(plot, paramsDict={}):
    if invalidParameters(paramsDict, ['min', 'max'], 'x_average'):
        return None
    outputValue = plot.GetRMS()
    return outputValue
