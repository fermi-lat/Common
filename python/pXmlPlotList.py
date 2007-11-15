
from pXmlList         import pXmlList
from pXmlPlotRep      import pXmlTH1FRep
from pXmlPlotRep      import pXmlTH2FRep
from pXmlPlotRep      import pXmlTH3FRep
from pXmlPlotRep      import pXmlTGraphRep
from pSkyMapUtils     import pXmlSkyMapRep
from pTimeSeriesUtils import pXmlTimeSeriesRep


SUPPORTED_PLOT_TYPES = ['TH3F', 'TH2F', 'TH1F', 'TGraph', 'SkyMap',\
                        'TimeSeries']

class pXmlPlotList(pXmlList):   

    def __init__(self, element):        
        pXmlList.__init__(self, element)
        self.EnabledPlotRepsList = []
        for plotType in SUPPORTED_PLOT_TYPES:
            for element in self.getElementsByTagName(plotType):
                plotRep = eval('pXml%sRep(element)' % plotType)
                if plotRep.Enabled:
                    self.EnabledPlotRepsList.append(plotRep)
