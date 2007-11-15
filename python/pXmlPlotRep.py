
import pSafeLogger
logger = pSafeLogger.getLogger('pXmlPlotRep')

import array

from pXmlElement  import pXmlElement
from pXmlList     import pXmlList
from pSafeROOT    import ROOT


class pXmlBasePlotRep(pXmlElement):

    def __init__(self, element):        
        pXmlElement.__init__(self, element)
        self.Title        = self.getTagValue('title', self.Name)
        self.Expression   = self.getTagValue('expression')
        self.Cut          = self.getTagValue('cut'   , '')
        self.XLabel       = self.getTagValue('xlabel', '')
        self.YLabel       = self.getTagValue('ylabel', '')
        self.ZLabel       = self.getTagValue('zlabel', '')
        self.XLog         = self.evalTagValue('xlog', False)
        self.YLog         = self.evalTagValue('ylog', False)
        self.ZLog         = self.evalTagValue('zlog', False)
        self.DrawOptions  = self.getTagValue('drawoptions', '')
        self.Caption      = self.getTagValue('caption', '')
        self.Caption     += '- <b>Plotted expression</b>: "%s"<br/>' %\
                            self.Expression
        self.Caption     += '- <b>Applied cut</b>: "%s"' % self.Cut
        self.RootObject   = None

    def draw(self, rootObject):
        rootObject.Draw(self.DrawOptions)

    def processLabels(self):
        pass

    def formatAxes(self):
        self.processLabels()
        self.RootObject.GetXaxis().SetTitle(self.XLabel)
        self.RootObject.GetYaxis().SetTitle(self.YLabel)
        self.RootObject.GetZaxis().SetTitle(self.ZLabel)

    def getBranchType(self, rootTree, branchName):
        try:
            return rootTree.GetBranch(branchName).GetTitle()[-1].lower()
        except:
            logger.error('Could not determine type for TBranch %s.' %\
                         branchName)
            return None

    def projectTree(self, rootTree, numEntries):
        if numEntries < 0:
            numEntries = 1000000000
        rootTree.Project(self.Name, self.Expression, self.Cut, '', numEntries)


class pXmlTH1FRep(pXmlBasePlotRep):

    def __init__(self, element):
        pXmlBasePlotRep.__init__(self, element)
        self.NumXBins = self.evalTagValue('xbins', 100)
        self.XMin     = self.evalTagValue('xmin', None, True)
        self.XMax     = self.evalTagValue('xmax', None, True)

    def processLabels(self):
        if self.XLabel == '':
            self.XLabel = self.Expression
        if self.YLabel == '':
            self.YLabel = 'entries/bin'

    def createRootObject(self, rootTree, numEntries):
        logger.debug('Creating TH1F %s' % self.Name)
        self.RootObject = ROOT.TH1F(self.Name, self.Title, self.NumXBins,\
                                    self.XMin, self.XMax)
        self.formatAxes()
        self.projectTree(rootTree, numEntries)


class pXmlTGraphRep(pXmlBasePlotRep):

    def __init__(self, element):
        pXmlBasePlotRep.__init__(self, element)

    def processLabels(self):
        (yExpression, xExpression) = self.Expression.split(':')
        if self.XLabel == '':
            self.XLabel = xExpression
        if self.YLabel == '':
            self.YLabel = yExpression

    def addPoint(self, i):
        self.RootObject.SetPoint(i, self.ArrayX[0], self.ArrayY[0])

    def createRootObject(self, rootTree, numEntries):
        logger.debug('Creating TGraph %s' % self.Name)
        (xBranchName, yBranchName) = self.Expression.split(':')
        xBranchType = self.getBranchType(rootTree, xBranchName)
        yBranchType = self.getBranchType(rootTree, yBranchName)
        if (xBranchType is None) or (yBranchType is None):
            logger.error('Cannot create %s.' % self.Name)
            return None
        self.ArrayX = array.array(xBranchType, [0])
        self.ArrayY = array.array(yBranchType, [0])
        rootTree.SetBranchAddress(xBranchName, self.ArrayX)
        rootTree.SetBranchAddress(yBranchName, self.ArrayY)
        rootTree.GetEntry(0)
        self.FirstValueX = self.ArrayX[0]
        if numEntries < 0:
            numEntries = rootTree.GetEntriesFast()
        self.RootObject = ROOT.TGraph(numEntries)
        self.RootObject.SetNameTitle(self.Name, self.Title)
        for i in xrange(numEntries):
            rootTree.GetEntry(i)
            self.addPoint(i)
        self.formatAxes()
        ROOT.gDirectory.Add(self.RootObject)


class pXmlTH2FRep(pXmlTH1FRep):

    def __init__(self, element):
        pXmlTH1FRep.__init__(self, element)
        self.NumYBins = self.evalTagValue('ybins', 100)
        self.YMin     = self.evalTagValue('ymin', None, True)
        self.YMax     = self.evalTagValue('ymax', None, True)
        self.ZLog     = self.evalTagValue('zlog', False)
        self.MarkerStyle = self.evalTagValue('markerstyle', None)
        self.MarkerColor = self.evalTagValue('markercolor', None)

    def processLabels(self):
        (yExpression, xExpression) = self.Expression.split(':')
        if self.XLabel == '':
            self.XLabel = xExpression
        if self.YLabel == '':
            self.YLabel = yExpression

    def createRootObject(self, rootTree, numEntries):
        logger.debug('Creating TH2F %s' % self.Name)
        self.RootObject = ROOT.TH2F(self.Name, self.Title, self.NumXBins,\
                                    self.XMin, self.XMax, self.NumYBins,\
                                    self.YMin, self.YMax)
        self.formatAxes()
        self.formatMarker()
        self.projectTree(rootTree, numEntries)

    def formatMarker(self):
        if self.MarkerColor is not None:
            self.RootObject.SetMarkerColor(self.MarkerColor)
        if self.MarkerStyle is not None:
            self.RootObject.SetMarkerStyle(self.MarkerStyle)


class pXmlTH3FRep(pXmlTH2FRep):

    def __init__(self, element):
        pXmlTH2FRep.__init__(self, element)
        self.NumZBins = self.evalTagValue('zbins', 100)
        self.ZMin     = self.evalTagValue('zmin', None, True)
        self.ZMax     = self.evalTagValue('zmax', None, True)
        

    def processLabels(self):
        (zExpression, yExpression, xExpression) = self.Expression.split(':')
        if self.XLabel == '':
            self.XLabel = xExpression
        if self.YLabel == '':
            self.YLabel = yExpression
        if self.ZLabel == '':
            self.ZLabel = zExpression

    def createRootObject(self, rootTree, numEntries):
        logger.debug('Creating TH3F %s' % self.Name)
        self.RootObject = ROOT.TH3F(self.Name, self.Title, self.NumXBins,\
                                    self.XMin, self.XMax, self.NumYBins,\
                                    self.YMin, self.YMax, self.NumZBins,\
                                    self.ZMin, self.ZMax)
        self.formatAxes()
        self.formatMarker()
        self.projectTree(rootTree, numEntries)
