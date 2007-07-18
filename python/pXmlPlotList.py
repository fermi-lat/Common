from pXmlList     import pXmlList
from pXmlPlotRep  import pXmlTH1FRep
from pXmlPlotRep  import pXmlTH2FRep
from pXmlPlotRep  import pXmlTGraphRep
from pSkyMapUtils import pXmlSkyMapRep


SUPPORTED_PLOT_TYPES = ['TH1F', 'TGraph', 'TH2F', 'SkyMap']

class pXmlPlotList(pXmlList):   

    def __init__(self, element):        
        pXmlList.__init__(self, element)
        self.EnabledPlotRepsDict = {}
        for plotType in SUPPORTED_PLOT_TYPES:
            for element in self.getElementsByTagName(plotType):
                plotRep = eval('pXml%sRep(element)' % plotType)
                if plotRep.Enabled:
                    self.EnabledPlotRepsDict[plotRep.Name] = plotRep
