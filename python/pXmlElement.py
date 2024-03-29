## @package pXmlElement
## @brief Description of an xml element.

import sys

from pXmlBaseElement import pXmlBaseElement

## @brief Class describing a xml element.
#
#  This class encapsulates the features that are shared by most
#  pieces of the xml configuration files (which can describe lists,
#  variables, plots, etc.). In particular the methods for retrieving
#  the element name and the enable flag, along with those for
#  retrieving generic tag values, are provided.

class pXmlElement(pXmlBaseElement):

    ## @brief Constructor
    ## @param self
    #  The class instance.
    ## @param domElement
    #  A xml element, as returned by the getElementsByTagName()
    #  function of the xml.dom.minidom module.

    def __init__(self, domElement):

        ## @var Name
        ## @brief The value of the "name" attribute.
        #
        #  By default is an empty string.

        ## @var Enabled
        ## @brief The value of the "enabled" attribute.
        #
        #  By default is True.
        
        pXmlBaseElement.__init__(self, domElement)
        self.Name    = self.getAttribute('name', '')
        self.Enabled = self.evalAttribute('enabled', True)

    ## @brief Return the 'name' attribute of the element.
    #
    #  Note that the 'name' attribute sohould be defined for each
    #  element.
    ## @param self
    #  The class instance.

    def getName(self):
        return self.Name

    ## @brief Return a formatted text representation of the class instances.
    ## @param self
    #  The class instance.
        
    def getTextSummary(self):
        return '%s\n' % pXmlBaseElement.getTextSummary(self) +\
               'Name     : %s\n' % self.Name +\
               'Enabled  : %s' % self.Enabled

    ## @brief Class representation.
    ## @param self
    #  The class instance.

    def __str__(self):
        return self.getTextSummary()


if __name__ == '__main__':
    from xml.dom  import minidom
    doc = minidom.parse(file('../xml/alarmconfig.xml'))
    for element in doc.getElementsByTagName('alarmList'):
        print 'Printing pXmlElement object...'
        print pXmlElement(element)
