#! /bin/env python

import os
import sys

import pSafeLogger
logger = pSafeLogger.getLogger('pBadTimeIntervalLogger')

from pXmlWriter import pXmlWriter


## @brief Function for fitting a strip chart with a polinomial of degree
#  2 and excluding a given interval.
#
#  The interval to be excluded is defined by the parameters [3] and [4].
#  The x variable is always referred to the center of the interval
#  excluded from the fit.

def brokenQuadratic(x, par):
    x = x[0]
    if x > par[3] and x < par[4]:
        ROOT.TF1.RejectPoint()
        return 0
    x = x - 0.5*(par[3] + par[4])
    return par[0] + par[1]*x + par[2]*(x**2)


## @package pBadTimeIntervalLogger
## @brief Module flagging bad time intervals during solar flares.


## @brief Base class describing a time interval.
#

class pBaseTimeInterval:

    MIN_DURATION = 5.0

    ## @brief Basic constructor.
    #

    def __init__(self, startTime, endTime, source):
        self.StartTime = startTime
        self.EndTime   = endTime
        self.Source    = source

    ## @brief Draw the time interval.
    #
    def draw(self, ymax, color = None, style = 7, width = 2):
        color = color or ROOT.kBlue
        self.StartLine = ROOT.TLine(self.StartTime, 0, self.StartTime, ymax)
        self.EndLine = ROOT.TLine(self.EndTime, 0, self.EndTime, ymax)
        for line in [self.StartLine, self.EndLine]:
            line.SetLineColor(color)
            line.SetLineStyle(style)
            line.SetLineWidth(width)
            line.Draw()
        self.StartLabel = ROOT.TLatex(self.StartTime, 1.05*ymax,
                                      'MET = %s' % self.StartTime)
        self.EndLabel = ROOT.TLatex(self.EndTime, 1.05*ymax,
                                      'MET = %s' % self.EndTime)
        for label in [self.StartLabel, self.EndLabel]:
            label.SetTextColor(color)
            label.SetTextAngle(30)
            label.SetTextAlign(22)
            label.Draw()
            
    ## @brief Return the length of the interval
    #
    def getLength(self):
        return (self.EndTime - self.StartTime)

    ## @brief Trim the interval according to the specified boundaries.
    #
    def trim(self, minTime, maxTime):
        if self.EndTime < minTime or self.StartTime > maxTime:
            logger.error('Problems trimming the time interval %s' % self)
            logger.error('Requested trim interval: %f--%f' % (minTime, maxTime))
            logger.info('Trimming skipped.')
            return
        logger.info('Trimming interval %s...' % self)
        if self.StartTime < minTime:
            logger.info('Moving start time from %f to %f...' %\
                            (self.StartTime, minTime))
            self.StartTime = minTime
        if self.EndTime > maxTime:
            logger.info('Moving end time from %f to %f...' %\
                            (self.EndTime, maxTime))
            self.EndTime = maxTime
        
    ## @brief Checck whether the BTI is longer than the minimum duration.
    #
    def isValid(self):
        return (self.getLength() > self.MIN_DURATION)

    def getXmlDict(self):
        return {'start_met': '%f' % self.StartTime,
                'end_met'  : '%f' % self.EndTime,
                'duration' : '%f' % self.getLength(),
                'source'   : self.Source
                }

    ## @brief Subtraction
    #
    #  Return the time separation between two intervals (i.e. the time between
    #  the end of the first and the start of the second). 
    
    def __sub__(self, other):
        return self.StartTime - other.EndTime

    ## @Brief sum
    #
    
    def __add__(self, other):
        startTime = min(self.StartTime, other.StartTime)
        endTime = max(self.EndTime, other.EndTime)
        return pBaseTimeInterval(startTime, endTime, self.Source)

    ## @brief Comparison operator.
    #

    def __cmp__(self, other):
        if self.StartTime > other.StartTime:
            return 1
        elif self.StartTime < other.StartTime:
            return -1
        else:
            return 0

    ## @brief Terminal formatting.
    #

    def __str__(self):
        return 'MET %f--%f (%f s)' %\
            (self.StartTime, self.EndTime, self.getLength())



## @brief Derived class specialized for a bad time interval.
#

class pBadTimeInterval(pBaseTimeInterval):

    ## @brief Constructor.
    #

    def __init__(self, startTime, endTime, intLoss, source):
        pBaseTimeInterval.__init__(self, startTime, endTime, source)
        self.IntegralLoss = intLoss

    ## @brief Superimpose the interval to the integral curve.
    #

    def drawIntegral(self, g, color = None):
        color = color or ROOT.kRed
        ystart = g.Eval(self.StartTime)
        ystop = g.Eval(self.EndTime)
        self.StartMarker = ROOT.TMarker(self.StartTime, ystart, 20)
        self.EndMarker = ROOT.TMarker(self.EndTime, ystop, 20)
        for marker in [self.StartMarker, self.EndMarker]:
            marker.SetMarkerColor(color)
            marker.Draw()
        self.StartIntLabel = ROOT.TLatex(self.StartTime, ystart,
                                         'IL = %.2f s' % ystart)
        self.EndIntLabel = ROOT.TLatex(self.EndTime, ystop,
                                       'IL = %.2f s' % ystop)
        for label in [self.StartIntLabel, self.EndIntLabel]:
            label.SetTextColor(color)
            label.SetTextAngle(30)
            label.SetTextAlign(11)
            label.Draw()

    def getXmlDict(self):
        xmlDict = pBaseTimeInterval.getXmlDict(self)
        xmlDict['integral_loss'] = '%f' % self.IntegralLoss
        return xmlDict



## @brief Class doing the actual plots.
#

class pTrendingPlotter:

    ## @brief Basic constructor.
    #

    ALIAS_DICT  = {
        'TimeFirstEvent': 'Digi.TimeStampFirstEvt',
        'TimeLastEvent': 'Digi.TimeStampLastEvt',
        'Time': '0.5*(Digi.Bin_Start + Digi.Bin_End)',
        'TileNormRate63': 'Digi.OutF_Normalized_AcdHit_AcdTile[63]',
        'TileNormRate63_err': 'Digi.OutF_Normalized_AcdHit_AcdTile_err[63]',
        'NormTransientRate': 'Merit.OutF_NormRateTransientEvts',
        'NormTransientRate_err': 'Merit.OutF_NormRateTransientEvts_err',
        'TransientRate': 'Merit.Rate_TransientEvts',
        'TransientRate_err': 'Merit.Rate_TransientEvts_err',
        'RockingAngle': 'Merit.Mean_PtSCzenith',
        'RockingAngle_err': 'Merit.Mean_PtSCzenith_err',
        'NormAcdTileCount': 'Merit.Mean_AcdTileCount/(8.73 - 0.283466*Digi.Rate_TriggerEngine[10] + 0.00615361*Digi.Rate_TriggerEngine[10]**2)',
        'NormAcdTileCount_err': 'Merit.Mean_AcdTileCount_err/(8.73 - 0.283466*Digi.Rate_TriggerEngine[10] + 0.00615361*Digi.Rate_TriggerEngine[10]**2)'
        }
    TIME_FORMAT = '%b/%d/%y %H:%M'
    TIME_BIN_WIDTH = 15.0
    NORM_RATE_ERR  = 0.25

    def __init__(self, digiTrendFilePath, meritTrendFilePath):
        # Setting the time offset for the x-axis of the strip charts.
        # We first create the a ROOT.TDatetime object (January 1, 2001)
        # and then convert it to a float---setting the 'gmt' conversion
        # option to True. 
        # It's not entirely clear to me why we have to do this and we can't
        # just set the time offset directly with the 'gmt' option set to
        # True in the TAxis::SetTimeOffset() method, but it doesn't work
        # that way.
        # It looks like this is not clear to the ROOT folks either:
        # http://root.cern.ch/phpBB3/viewtopic.php?f=3&t=10002
        self.DateOffset = ROOT.TDatime(2001,01,01,00,00,00)
        self.TimeOffset = self.DateOffset.Convert(True)
        # Now go on with the real stuff.
        logger.info('Opening input files...')
        self.DigiFile    = self.openFile(digiTrendFilePath)
        self.MeritFile   = self.openFile(meritTrendFilePath)
        logger.info('Retrieving the root trees...')
        self.DigiTree    = self.DigiFile.Get('Time')
        self.MeritTree   = self.MeritFile.Get('Time')
        if self.DigiTree.GetEntries() != self.MeritTree.GetEntries():
            sys.exit('Digi and Merit tree have different # entries. Abort.')
        logger.info('Making the three trees friends...')
        self.Tree = ROOT.TTree('Time', 'Time')
        self.Tree.AddFriend(self.DigiTree , 'Digi')
        self.Tree.AddFriend(self.MeritTree, 'Merit')
        logger.info('Setting aliases and creating TTreeFormulas...')
        self.TreeFormulaDict = {}
        for (key, value) in self.ALIAS_DICT.items():
            logger.debug('%s -> %s' % (key, value))
            self.Tree.SetAlias(key, value)
            self.TreeFormulaDict[key] = ROOT.TTreeFormula(key, value, self.Tree)
        self.RootPool = {}
        self.getEntry(0)
        self.StartTime = self.value('TimeFirstEvent')
        self.getLastEntry()
        self.StopTime = self.value('TimeLastEvent')
        self.RunTimeSpan = pBaseTimeInterval(self.StartTime, self.StopTime,
                                             None)
        logger.info('Time span for the run: %s' % self.RunTimeSpan)

    ## @brief Call the GetEntry() method for all the trees.
    #

    def getEntry(self, entry):
        self.Tree.GetEntry(entry)
        self.DigiTree.GetEntry(entry)
        self.MeritTree.GetEntry(entry)

    ## @brief Get the last entry in the trees.
    #
    def getLastEntry(self):
        self.getEntry(self.DigiTree.GetEntries() - 1)

    ## @brief Return the value of an expression.
    #
    def value(self, expr):
        try: 
            return self.TreeFormulaDict[expr].EvalInstance()
        except KeyError:
            return 0.0

    ## @brief Utility function to store a reference to objects that the
    #  garbage collector should not grab yet.

    def store(self, rootObject):
        key = rootObject.GetName()
        if key in ['TLine']:
            key = '%s_%d' % (key, len(self.RootPool))
        self.RootPool[key] = rootObject

    ## @brief Common interface for opening root files.
    #

    def openFile(self, rootFilePath):
        logger.info('Opening file %s...' % rootFilePath)
        if not os.path.exists(rootFilePath):
            sys.exit('File %s does not exist.' % rootFilePath)
        rootFile = ROOT.TFile(rootFilePath)
        if rootFile.GetFd() == -1:
            sys.exit('Could not open file %s.' % rootFilePath)
        logger.info('Done. %s objects found.\n' %\
                        (rootFile.GetListOfKeys().LastIndex() + 1))
        return rootFile

    ## @brief Setup the time display on a strip chart.
    #
    def setupTimeAxis(self, graph):
        graph.GetXaxis().SetTitle('Time UTC')
        graph.GetXaxis().SetNdivisions(506)
        graph.GetXaxis().SetTimeDisplay(True)
        graph.GetXaxis().SetTimeFormat(self.TIME_FORMAT)
        graph.GetXaxis().SetTimeOffset(self.TimeOffset)

    ## @brief Create the strip chart for a given quantity.
    #

    def createStripChart(self, expr, ytitle = None, ymin = None, ymax = None):
        ytitle = ytitle or expr
        gname  = 'g%s' % expr
        g = ROOT.TGraphErrors()
        g.SetName(gname)
        for i in xrange(self.DigiTree.GetEntries()):
            self.getEntry(i)
            g.SetPoint(i, self.value('Time'), self.value(expr))
            g.SetPointError(i, 0, self.value('%s_err' % expr))
        g.SetMarkerStyle(26)
        g.SetMarkerSize(0.5)
        self.setupTimeAxis(g)
        g.GetYaxis().SetTitle(ytitle)
        if ymin is not None and ymax is not None:
            g.GetYaxis().SetRangeUser(ymin, ymax)
        g.Draw('ap')
        g.GetXaxis().SetRangeUser(self.RunTimeSpan.StartTime,
                                  self.RunTimeSpan.EndTime)
        ROOT.gPad.Update()
        self.store(g)
        return g

    ## @brief Return the strip chart for a given expression.
    #
    
    def getStripChart(self, expr):
        try:
            return self.RootPool['g%s' % expr]
        except KeyError:
            return None

    ## @brief Return a line.
    #
    def getHorLine(self, y, color = None, style = 7, width = 2):
        color = color or ROOT.kBlue
        l = ROOT.TLine(self.RunTimeSpan.StartTime, y,
                       self.RunTimeSpan.EndTime, y)
        l.SetLineColor(color)
        l.SetLineStyle(style)
        l.SetLineWidth(width)
        self.store(l)
        return l

    ## @brief Draw all the necessary stuff.
    #
    
    def plot(self):
        self.Canvas = ROOT.TCanvas('cBTI', 'Bad time intervals', 1200, 800)
        self.Canvas.Divide(2, 3)
        self.Canvas.cd(1)
        g1 = self.createStripChart('TileNormRate63',
                                   'Normalized hit rate in tile 63', 0.0, 1.0)
        self.Canvas.cd(3)
        g3 = self.createStripChart('TransientRate', 'Transient Rate')
        self.Canvas.cd(5)
        g5 = self.createStripChart('RockingAngle', 'Rocking Angle', 0.0, 90.0)
        self.Canvas.cd(2)
        g2 = self.createStripChart('NormAcdTileCount',
                                   'Normalized ACD tile count', 0.0, 8.0)
        self.Canvas.cd(4)
        g4 = self.createStripChart('NormTransientRate',
                                   'Normalized transient rate', 0, 1.75)
        self.Canvas.cd()

    ## @brief Loop over a strip chart and return the list of the time intervals
    #  for which the y values are above a given threshold.
    #
    #  Time intervals which are closer than an adjustable padding are merged
    #  together.

    def __applyThreshold(self, graph, threshold, source = None, padding = 60):
        # First find the intervals...
        intervals = []
        x = ROOT.Double()
        y = ROOT.Double()
        aboveThreshold = False
        for i in xrange(graph.GetN()):
            graph.GetPoint(i, x, y)
            if y >= threshold and not aboveThreshold:
                start = float(x) - self.TIME_BIN_WIDTH/2.
                aboveThreshold = True
            if (y < threshold or i == graph.GetN() - 1) and aboveThreshold:
                stop = float(x) + self.TIME_BIN_WIDTH/2.
                aboveThreshold = False
                intervals.append(pBaseTimeInterval(start, stop, source))
        # ... then merge the intervals which are too close to each other.
        mergedIntervals = []
        for (i, interval) in enumerate(intervals):
            if (i == 0) or (interval - mergedIntervals[-1] > padding):
                mergedIntervals.append(interval)
            else:
                mergedIntervals[-1] += interval
        for interval in mergedIntervals:
            interval.trim(self.StartTime, self.StopTime)
        return mergedIntervals

    ## @brief Loop over the strip chart for the normalized hit rate in the
    #  ACD tile 63 and find the list of solar flare time intervals.

    def findFlareIntervals(self, threshold):
        self.Canvas.cd(1)
        l = self.getHorLine(threshold)
        l.Draw()
        logger.info('Searching for flare intervals...')
        g = self.getStripChart('TileNormRate63')
        self.FlareIntervals = self.__applyThreshold(g, threshold,
                                                    'NormAcdTileRate63')
        logger.info('Done.')
        for (i, interval) in enumerate(self.FlareIntervals):
            logger.info('Flare interval #%s: %s' % (i, interval))
            interval.draw(3*threshold)
        self.Canvas.cd()
        self.Canvas.Update()

    ## @brief Define the bad time intervals based on the normalized ACD
    #  tile count.

    def analyzeNormTileCount(self, threshold):
        self.Canvas.cd(2)
        l = self.getHorLine(threshold, ROOT.kRed)
        l.Draw()
        logger.info('Analyzing normalized ACD tile count...')
        g = self.getStripChart('NormAcdTileCount')
        tmpBTIList = self.__applyThreshold(g, threshold, 'NormAcdTileCount')
        self.BadTileCountIntervals = []
        for interval in tmpBTIList:
            if interval.isValid():
                self.BadTileCountIntervals.append(interval)
        logger.info('Done.')
        for (i, interval) in enumerate(self.BadTileCountIntervals):
            logger.info('Bad tile count interval #%s: %s' % (i, interval))
            interval.draw(3*threshold, ROOT.kRed)
        self.Canvas.cd()
        self.Canvas.Update()
        
    ## @brief Analyze the normalized transient rate and define the
    #  bad time intervals.
    #
    #  This is where most of the work is actually done.
    #
    # @param minPadding
    # This is the minimum time padding that is required (both on the left and
    # on the right of any flare interval) to fit the normalized transient
    # rate and define the integral loss. If there are not enough data points
    # on both sides of the flare intervals (i.e. the flare happens to be
    # too close to the beginning or the end of the run), then they're just
    # artificially added (value = 1, error = NORM_RATE_ERR) in order to
    # constrain the fit.
    #
    # @param intLossStart
    # The integral loss (in seconds) defining the start of  a bad time interval.
    #
    # @param fracLossEnd
    # The fractional total loss defining the end of of a bad time interval.
    #

    def analyzeNormTransientRate(self, minTimePadding = 1000, minIntLoss = 60,
                                 minDiffLoss = 0.15, intLossStart = 5,
                                 fracLossEnd = 0.95, numPlateauPoints = 10):
        # These will be used to loop over the strip charts.
        _x = ROOT.Double()
        _y = ROOT.Double()
        # Change to the right pad and grab the strip chart.
        self.Canvas.cd(4)
        g = self.getStripChart('NormTransientRate')
        ftemp = ROOT.TF1('ftemp', brokenQuadratic, self.RunTimeSpan.StartTime,
                         self.RunTimeSpan.EndTime, 5)
        self.NormTransRateFitFunctions = []
        # Begin the loop over the flare intervals defined based on the
        # normalized rate in tile 63.
        maxIntLoss = -1.
        self.BadNormTransIntervals = []
        for (i, interval) in enumerate(self.FlareIntervals):
            logger.info('Analyzing the transient rate for interval %s...' %\
                            interval)
            # Fix the parameter of the "broken quadratic" in order to
            # exclude the interval from the fit.
            ftemp.FixParameter(3, interval.StartTime)
            ftemp.FixParameter(4, interval.EndTime)
            # Check whether we need to pad the strip chart of the normalized
            # transient rate.
            gtemp = g.Clone()
            timeFromStart = interval.StartTime - self.RunTimeSpan.StartTime
            # First on the left...
            if timeFromStart < minTimePadding:
                numPad = int((minTimePadding - timeFromStart)/\
                                 self.TIME_BIN_WIDTH)
                logger.info('Padding on the left with %d points...' % numPad)
                for j in xrange(numPad):
                    x = self.RunTimeSpan.StartTime - minTimePadding -\
                        i*self.TIME_BIN_WIDTH
                    n = gtemp.GetN()
                    gtemp.SetPoint(n, x, 1.0)
                    gtemp.SetPointError(n, 0.0, self.NORM_RATE_ERR)
            # ...then on the right
            timeToEnd = self.RunTimeSpan.EndTime - interval.EndTime
            if timeToEnd < minTimePadding:
                numPad = int((minTimePadding - timeToEnd)/self.TIME_BIN_WIDTH)
                logger.info('Padding on the right with %d points...' % numPad)
                for j in xrange(numPad):
                    x = self.RunTimeSpan.EndTime + minTimePadding +\
                        i*self.TIME_BIN_WIDTH
                    n = gtemp.GetN()
                    gtemp.SetPoint(n, x, 1.0)
                    gtemp.SetPointError(n, 0.0, self.NORM_RATE_ERR)
            # Fit the normalized transient rate.
            gtemp.Fit(ftemp, 'N')
            # Copy the parameters over to a real quadratic (to be used for
            # drawing and for the construction of the integral loss).
            f = ROOT.TF1('fFit_%d' % i, '[0] + [1]*(x-[3]) + [2]*(x-[3])**2',
                         self.RunTimeSpan.StartTime, self.RunTimeSpan.EndTime)
            f.SetParameter(0, ftemp.GetParameter(0))
            f.SetParameter(1, ftemp.GetParameter(1))
            f.SetParameter(2, ftemp.GetParameter(2))
            f.SetParameter(3, 0.5*(interval.StartTime + interval.EndTime))
            f.SetLineColor(ROOT.kBlue)
            f.SetLineStyle(7)
            self.store(f)
            f.Draw('same')
            # Delete the temp strip chart.
            gtemp.Delete()
            # Construct the integral curve.
            gIntLoss = ROOT.TGraph()
            gIntLoss.SetName('gIntLoss_%d' % i)
            # We set the first (and, eventually, the last) point to zero
            # in such a way we can set the x-range to be the same as all the
            # other strip charts.
            gIntLoss.SetPoint(0, self.RunTimeSpan.StartTime, -1)
            gIntLoss.SetMarkerStyle(26)
            gIntLoss.SetMarkerSize(0.5)
            intLoss = 0.0
            n = 1
            for j in range(g.GetN()):
                g.GetPoint(j, _x, _y)
                if _x > interval.StartTime and (_x - interval.EndTime) < \
                        numPlateauPoints*self.TIME_BIN_WIDTH:
                    delta = -15.*(_y - f.Eval(_x))
                    if intLoss <= 0 and delta < 0:
                        pass
                    else:
                        intLoss += delta
                    gIntLoss.SetPoint(n, _x, intLoss)
                    n += 1
            if intLoss > maxIntLoss:
                maxIntLoss = intLoss
            gIntLoss.SetPoint(n, self.RunTimeSpan.EndTime, -1)
            self.setupTimeAxis(gIntLoss)
            gIntLoss.GetYaxis().SetTitle('Integrated loss (s)')
            self.store(gIntLoss)
            self.Canvas.cd(6)
            if i == 0:
                gIntLoss.Draw('ap')
            else:
                gIntLoss.Draw('p,same')
            gIntLoss.GetXaxis().SetRangeUser(self.RunTimeSpan.StartTime,
                                             self.RunTimeSpan.EndTime)
            # Define the bad time interval, if it's the case.
            # Calculate the plateau (and remember that the first and last
            # points are artificially set to -1).
            totalIntLoss = 0
            jmin = max(1, gIntLoss.GetN() - numPlateauPoints - 1)
            jmax = gIntLoss.GetN() - 1
            for j in xrange(jmin, jmax):
                gIntLoss.GetPoint(j, _x, _y)
                totalIntLoss += _y
            totalIntLoss /= numPlateauPoints
            # Make sure the integral loss exceeds the threshold for defining a
            # bad time interval.
            if totalIntLoss > minIntLoss:
                startBad = None
                endBad = None
                # Go and search for the interval boundaries.
                for j in xrange(1, gIntLoss.GetN() - 1):
                    gIntLoss.GetPoint(j, _x, _y)
                    if startBad is None and _y > intLossStart:
                        startBad = float(_x) - self.TIME_BIN_WIDTH/2.
                    if endBad is None and _y > totalIntLoss*fracLossEnd:
                        endBad = float(_x) + self.TIME_BIN_WIDTH/2.
                if startBad is not None and endBad is not None:
                    # At this point we can construct the interval.
                    badInterval = pBadTimeInterval(startBad, endBad,
                                                   totalIntLoss,
                                                   'NormTransientRate')
                    # Trim the interval.
                    badInterval.trim(self.StartTime, self.StopTime)
                    # If it's non zero and the fractional loss is large
                    # enough, than it's good to be reported.
                    if badInterval.isValid() and \
                            totalIntLoss/badInterval.getLength() > minDiffLoss:
                        self.BadNormTransIntervals.append(badInterval)
        # Set the scale on the y-axis for the first graph (the one the axis)
        # belongs to, based on the interval with the lasrgest integral loss.
        try:
            g = self.RootPool['gIntLoss_0']
            g.GetYaxis().SetRangeUser(0, 1.2*maxIntLoss)
        except KeyError:
            # No bad time intervals, no integral loss plots, just go ahead.
            pass
        for (i, interval) in enumerate(self.BadNormTransIntervals):
            logger.info('Bad normal transient interval #%s: %s' % (i, interval))
            self.Canvas.cd(4)
            interval.draw(1.25, ROOT.kRed)
            self.Canvas.cd(6)
            g = self.RootPool['gIntLoss_%d' % i]
            interval.drawIntegral(g, ROOT.kRed)
        self.Canvas.cd()
        self.Canvas.Update()

    def saveAsRoot(self, filePath):
        logger.info('Saving all the ROOT objects to %s...' % filePath)
        outputFile = ROOT.TFile(filePath, 'RECREATE')
        for rootObject in self.RootPool.values():
            logger.debug('Saving %s...' % rootObject.GetName())
            rootObject.Write()
        outputFile.Close()
        logger.info('Done.')
    
    def saveAsImage(self, filePath):
        logger.info('Saving the main canvas as image to %s...' % filePath)
        self.Canvas.SaveAs(filePath)
        logger.info('Done.')
    
    def writeXml(self, filePath):
        logger.info('Writing xml output file %s...' % filePath)
        writer = pXmlWriter(filePath)
        writer.openTag('solarFlareSummary')
        writer.indent()
        writer.openTag('flareIntervals')
        writer.indent()
        for interval in self.FlareIntervals:
            writer.writeTag('interval', interval.getXmlDict())
        writer.backup()
        writer.closeTag('flareIntervals')
        writer.openTag('badIntervals')
        writer.indent()
        for interval in self.BadTileCountIntervals:
            writer.writeTag('interval', interval.getXmlDict())
        for interval in self.BadNormTransIntervals:
            writer.writeTag('interval', interval.getXmlDict())
        writer.backup()
        writer.closeTag('badIntervals')
        writer.backup()
        writer.closeTag('solarFlareSummary')
        writer.closeFile()
        logger.info('Done.')




if __name__ == '__main__':
    from optparse import OptionParser
    parser = OptionParser(usage = 'usage: %prog [options] digitrend merittrend')
    parser.add_option('-r', '--root-output', dest = 'r',
                      default = None, type = str,
                      help = 'path to the output root file')
    parser.add_option('-i', '--interactive', dest = 'i',
                      default = False, action = 'store_true',
                      help = 'run in interactive mode (show the plots)')
    parser.add_option('-p', '--png-output', dest = 'p',
                      default = None, type = str,
                      help = 'path to the output png file')
    parser.add_option('-x', '--xml-output', dest = 'x',
                      default = None, type = str,
                      help = 'path to the output xml file')
    parser.add_option('-f', '--flare-threshold', dest = 'f',
                      default = 0.22, type = float,
                      help = 'threshold on the normalized ACD hit rate for the flare intervals')
    parser.add_option('-c', '--count-threshold', dest = 'c',
                      default = 1.6, type = float,
                      help = 'threshold on the normalized ACD tile count for the bad time intervals')
    parser.add_option('-t', '--min-time-padding', dest = 't',
                      default = 1000.0, type = float,
                      help = 'minimum time padding (in s) for fitting the normalized transient rate outside any flare interval')
    parser.add_option('-M', '--min-int-loss', dest = 'M',
                      default = 35.0, type = float,
                      help = 'minimum integral loss (in s) for defining a bad time interval')
    parser.add_option('-m', '--min-diff-loss', dest = 'm',
                      default = 0.18, type = float,
                      help = 'minimum differential loss for defining a bad time interval')
    parser.add_option('-s', '--int-loss-start', dest = 's',
                      default = 5.0, type = float,
                      help = 'integrated loss (in s) defining the start of a bad time interval')
    parser.add_option('-e', '--frac-loss-end', dest = 'e',
                      default = 0.95, type = float,
                      help = 'fraction of the total integrated loss defining the end of a bad time interval')
    parser.add_option('-n', '--num-plateau-points', dest = 'n',
                      default = 10, type = int,
                      help = 'number of points for the evaluation of the total integrated loss')

    (opts, args) = parser.parse_args()
    if len(args) != 2:
        parser.print_help()
        parser.error('Provide the paths to the digi and merit trending files!')
    (digiTrendFilePath, meritTrendFilePath) = args

    # Import the ROOT stuff.
    import ROOT
    ROOT.gROOT.SetStyle('Plain')
    ROOT.gStyle.SetOptTitle(0)
    ROOT.gStyle.SetPadGridX(True)
    ROOT.gStyle.SetPadGridY(True)

    if not opts.i:
        ROOT.gROOT.SetBatch()
    else:
        # This forces the interactive mode after the last command has been
        # executed.
        os.environ['PYTHONINSPECT'] = 'True'

    plotter = pTrendingPlotter(digiTrendFilePath, meritTrendFilePath)
    plotter.plot()
    plotter.findFlareIntervals(opts.f)
    plotter.analyzeNormTileCount(opts.c)
    plotter.analyzeNormTransientRate(opts.t, opts.M, opts.m, opts.s, opts.e,
                                     opts.n)
    if opts.r is not None:
        plotter.saveAsRoot(opts.r)
    if opts.p is not None:
        plotter.saveAsImage(opts.p)
    if opts.x is not None:
        plotter.writeXml(opts.x)


