
import os

from optparse import OptionParser


class pOptionParser:

    def __init__(self, options = '', minArgs = 1, maxArgs = 1, resolve = True):
        self.Parser = OptionParser(usage = 'usage: %prog [options] filename')
        for option in options:
            exec('self.add_%s()' % option)
        (self.Options, self.Arguments) = self.Parser.parse_args()
        if resolve:
            self.resolveOptionClashes()
        if len(self.Arguments) > maxArgs:
            self.error('too many arguments')
        elif len(self.Arguments) < minArgs:
            self.error('not enough arguments')
        self.Argument = self.Arguments[0]

    def error(self, message = ''):
        self.Parser.print_help()
        self.Parser.error(message)

    def resolveOptionClashes(self):
        if self.Options.V and not self.Options.r:
            self.error('cannot use the -V option without -r')
        if self.Options.L and not self.Options.r:
            self.error('-L option does not make any sense without -r')

    def add_c(self):
        self.Parser.add_option('-c', '--config-file', dest = 'c',
                               default = None, type = str,
                               help = 'path to the input xml config file')

    def add_o(self):
        self.Parser.add_option('-o', '--output-file', dest = 'o',
                               default = None, type = str,
                               help = 'path to the output file')

    def add_p(self):
        self.Parser.add_option('-p', '--process-tree', dest = 'p',
                               default = None, type = str,
                               help='path to the processed the ROOT tree')

    def add_n(self):
        self.Parser.add_option('-n', '--num-events', dest = 'n',
                               default = -1, type = int,
                               help = 'number of events to be processed')

    def add_d(self):
        self.Parser.add_option('-d', '--output-dir', dest = 'd',
                               default = None, type = str,
                               help = 'path to the output directory')

    def add_r(self):
        self.Parser.add_option('-r', '--create-report', dest = 'r',
                               default = False, action = 'store_true',
                               help='generate a report')

    def add_v(self):
        self.Parser.add_option('-v', '--verbose', dest = 'v',
                               default = False, action = 'store_true',
                               help='print (a lot of!) debug messages')
        
    def add_L(self):
        self.Parser.add_option('-L', '--compile-LaTeX', dest = 'L',
                               default = False, action = 'store_true',
                               help='compile the LaTeX report')

    def add_V(self):
        self.Parser.add_option('-V', '--view-report', dest = 'V',
                               default = False, action='store_true',
                               help='launch the html report at the end')

    def add_f(self):
        self.Parser.add_option('-f', '--force-overwrite', dest = 'f',
                               default = False, action = 'store_true',
                               help='not used anymore.')

    def add_i(self):
        self.Parser.add_option('-i', '--interactive', dest = 'i',
                               default = False, action = 'store_true',
                               help='run interactively.')
