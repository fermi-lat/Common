import pSafeLogger
logger = pSafeLogger.getLogger('pSkyMapUtils')

import math
import numpy
import array

from pXmlPlotRep import pXmlTH2FRep

from pSafeROOT import ROOT

kPi       = math.pi
kRadToDeg = 180./kPi
kPiDeg    = kPi*kRadToDeg



def getCanvasCoordinates(l, b):
    if l > 180:
        l -= 360
    b /= kRadToDeg
    l /= 2*kRadToDeg
    d  = math.sqrt(1.0 + math.cos(b)*math.cos(l))
    x  = kPiDeg*math.sin(l)*math.cos(b)/d
    y  = kPiDeg*math.sin(b)/(2.0*d)
    return (x, y)


class pSkyMapGrid:

    def __init__(self, numDivisions = 20):
        self.NumDivisions = numDivisions
        self.PolyLineX  = {}
        self.PolyLineY  = {}
        self.__createPolyLines()

    def __createPolyLines(self):
        basePointsX = array.array('f', [0.0]*(self.NumDivisions - 1))
        basePointsY = array.array('f', [0.0]*(self.NumDivisions - 1))
        pointsX     = array.array('f', [0.0]*(self.NumDivisions - 1))
        pointsY     = array.array('f', [0.0]*(self.NumDivisions - 1))
        for i in range(self.NumDivisions - 1):
            basePointsX[i] = -180 + 360/(self.NumDivisions - 2)*i
            basePointsY[i] = -90  + 180/(self.NumDivisions - 2)*i
        for j in range(self.NumDivisions - 1):
            for i in range(self.NumDivisions - 1):
                (x, y) = getCanvasCoordinates(basePointsX[i], basePointsY[j])
                pointsX[i] = x
                pointsY[i] = y
            self.PolyLineX[j] = ROOT.TPolyLine(self.NumDivisions - 1,\
                                                 pointsX, pointsY)
        for j in range(self.NumDivisions - 1):
            for i in range(self.NumDivisions - 1):
                (x, y) = getCanvasCoordinates(basePointsX[j], basePointsY[i])
                pointsX[i] = x
                pointsY[i] = y
            self.PolyLineY[j] = ROOT.TPolyLine(self.NumDivisions - 1,\
                                                 pointsX, pointsY)

    def draw(self):
        for i in range(self.NumDivisions - 1):
            self.PolyLineX[i].SetLineStyle(2)
            self.PolyLineY[i].SetLineStyle(2)
            self.PolyLineX[i].SetLineColor(1)
            self.PolyLineY[i].SetLineColor(1)
            self.PolyLineX[i].Draw()
            self.PolyLineY[i].Draw()


class pXmlSkyMapRep(pXmlTH2FRep):

    def __init__(self, element):
        pXmlTH2FRep.__init__(self, element)
        self.SkyMapGrid = pSkyMapGrid()

    def createRootObject(self, rootTree, numEntries):
        logger.debug('Creating TH2F %s' % self.Name)
        self.RootObject = ROOT.TH2F(self.Name, self.Title, self.NumXBins,\
                                    self.XMin, self.XMax, self.NumYBins,\
                                    self.YMin, self.YMax)
        self.formatRootHistogram()
        (varX, varY) = self.Expression.split(':')
        if numEntries < 0:
            numEntries = rootTree.GetEntriesFast()
        for i in range(numEntries):
            rootTree.GetEntry(i)
            (x, y) = getCanvasCoordinates(eval('rootTree.%s' % varX),\
                                          eval('rootTree.%s' % varY))
            self.RootObject.Fill(x, y)

    def draw(self, rootObject):
        rootObject.GetXaxis().SetAxisColor(10)
        rootObject.GetYaxis().SetAxisColor(10)
        pXmlTH2FRep.draw(self, rootObject)
        self.SkyMapGrid.draw()



if __name__ == '__main__':
    canvas = ROOT.TCanvas()
    canvas.cd()
    h = ROOT.TH2D('test', 'test', 360, -180, 180, 180, -90, 90)
    h.Draw('col')
    grid = pSkyMapGrid()
    grid.draw()
    ROOT.gPad.Update()
