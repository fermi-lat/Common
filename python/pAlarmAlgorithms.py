import logging

def parametersOk(validList, actualList):
    for name in actualList:
        if name not in validList:
	    logging.error('Invalid parameter %s' % name)
	    return False
    return True

def x_average(plot, parameters={}):
    if not parametersOk(['min', 'max'], parameters.keys()):
        return None
    return plot.GetMean()


def x_rms(plot, parameters={}):
    if not parametersOk(['min', 'max'], parameters.keys()):
        return None
    return plot.GetRMS()

