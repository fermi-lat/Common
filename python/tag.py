#! /usr/bin/env python

import os

DATA_MONITORING_DIR = os.path.abspath('../../')
DOXYGEN_CFG_FILE_NAME = 'doxygen.cfg'


def findLastTag(module):
    print 'Searchin for last tag for %s...' % module
    os.system('grep -A 2 TAG %s/%s/ChangeLog | head -n 4' %\
              (DATA_MONITORING_DIR, module))

def updateDoxygenCfgFile(module, tag):
    print 'Updating doxygen configuration file for %s to version %s...' %\
          (module, tag)
    doxygenCfgFilePath = os.path.join(DATA_MONITORING_DIR, module,\
                                      'python', DOXYGEN_CFG_FILE_NAME)
    cfgFile = file(doxygenCfgFilePath)
    cfgFileContent = cfgFile.readlines()
    cfgFile.close()
    cfgFile = file(doxygenCfgFilePath, 'w')
    for line in cfgFileContent:
        if 'PROJECT_NUMBER' in line:
            line = 'PROJECT_NUMBER       = %s\n' % tag
        cfgFile.writelines(line)
    cfgFile.close()
    print 'Done.'

def tag(module, tag):
    modulePath = os.path.join(DATA_MONITORING_DIR, module)
    updateDoxygenCfgFile(module, tag)
    print 'Committing the doxygen config file to cvs...'
    os.system('cvs commit -m "updated version number" %s/python/doxygen.cfg' %\
              modulePath)
    print 'Done.'
    print 'Tagging version %s...' % tag
    os.system('cvs tag %s %s' % (tag, modulePath))
    print 'Done'


if __name__ == '__main__':
    from optparse import OptionParser
    parser = OptionParser()
    parser.add_option('-i', '--info', dest = 'i',
                      default = False, action = 'store_true',
                      help='show the last tag for a specific module')
    parser.add_option('-d', '--update-doxygen', dest = 'u',
                      default = False, action = 'store_true',
                      help='update the dosygen configuration file')
    parser.add_option('-t', '--tag', dest = 'u',
                      default = False, action = 'store_true',
                      help='tag the module')
    parser.add_option('-v', '--version', dest = 't',
                      default = None, type = str,
                      help = 'new version number')
    (opts, args) = parser.parse_args()
    if len(args) != 1:
        parser.print_help()
        parser.error('Exactly one argument required.')
    arg = args[0]
    if opts.i:
        findLastTag(arg)
    elif opts.d:
        if opts.v is None:
            parser.print_help()
            parser.error('Please specify a tag number.')
        updateDoxygenCfgFile(arg, opts.t)
    elif opts.t:
        if opts.v is None:
            parser.print_help()
            parser.error('Please specify a tag number.')
        tag(arg, opts.t)
    
