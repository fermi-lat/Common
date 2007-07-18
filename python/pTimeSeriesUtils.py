
import pSafeLogger
logger = pSafeLogger.getLogger('pTimeSeriesUtils')

from pXmlPlotRep import pXmlTGraphRep

from pSafeROOT import ROOT


class pXmlTimeSeriesRep(pXmlTGraphRep):

    def __init__(self, element):
        pXmlTGraphRep.__init__(self, element)

    def addPoint(self, i):
        x = (self.ArrayX[0] - self.FirstValueX)/86400.
        self.RootObject.SetPoint(i, x, self.ArrayY[0])

        


