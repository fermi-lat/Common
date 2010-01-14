# Facility for converting from MET to UTC and vice versa.
#
# From
# http://heasarc.gsfc.nasa.gov/cgi-bin/Tools/xTime/xTime.pl
# here are a few test conversions.
#
# 282855186: 2009Dec18 at 18:53:04.000 UTC
# 182255186: 2006Oct11 at 10:26:25.000 UTC
#  82255186: 2003Aug11 at 00:39:46.000 UTC
# 212855186: 2007Sep30 at 14:26:25.000 UTC
# 232855186: 2008May19 at 01:59:45.000 UTC
# 292855186: 2010Apr13 at 12:39:44.000 UTC 
#
# And here are the leap seconds starting from 2001 from
# http://en.wikipedia.org/wiki/Leap_second
#
# 2001 	0 	0
# 2002 	0 	0
# 2003 	0 	0
# 2004 	0 	0
# 2005 	0      +1
# 2006 	0 	0
# 2007 	0 	0
# 2008 	0      +1

import time
import calendar

BASE_MET_OFFSET = 978307200
LEAP_YEAR_DICT = {2005: 1,
                  2008: 1}

# Convert the dict with the leap seconds in a form that is more suitable
# for following use (i.e. with the keys in second rather than years).
LEAP_SEC_DICT = {}
LEAP_YEAR_LIST = LEAP_YEAR_DICT.keys()
LEAP_YEAR_LIST.sort()
totalLeap = 0
for year in LEAP_YEAR_LIST:
    leap = LEAP_YEAR_DICT[year]
    totalLeap += leap
    sec = calendar.timegm(time.strptime('31 Dec %d' % year, '%d %b %Y'))
    sec += totalLeap
    LEAP_SEC_DICT[sec] = leap

def met2utc(met, fmtstring = None):
    utc = met + BASE_MET_OFFSET
    for (sec, leap) in LEAP_SEC_DICT.items():
        if utc > sec:
            utc -= leap
    if fmtstring is not None:
        utc = time.strftime(fmtstring, time.gmtime(utc))
    return utc

def utc2met(utc):
    offset = BASE_MET_OFFSET
    for (sec, leap) in LEAP_SEC_DICT.items():
        if utc > sec:
            offset -= leap
    return utc - offset


if __name__ == '__main__':
    metList = [282855186, 182255186, 82255186, 212855186, 232855186, 292855186]
    utcList = [met2utc(met) for met in metList]
    print 'Testing met to utc conversion:'
    for met in metList:
        print met2utc(met, '%b %d, %Y %H:%M:%S')
    print '\nTesting utc to met conversion (all times should end with 86):'
    for utc in utcList:
        print utc2met(utc)
        
