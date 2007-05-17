
## @package pXmlElement
## @brief Description of an xml element.

import logging
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
    ## @param element
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
        self.__Name    = self.getAttribute('name', '')
        self.__Enabled = self.evalAttribute('enabled', True)

    ## @brief Retrieve the "name" attribute of the element.
    ## @param self
    #  The class instance.

    def getName(self):
        return self.__Name

    ## @brief Return the 'enabled' attribute of the element.
    #
    #  Note that the 'enabled' attribute sohould be defined for each
    #  element.
    ## @param self
    #  The class instance.

    def isEnabled(self):
        return self.__Enabled

    ## @brief Class representation.
    ## @param self
    #  The class instance. 

    def __str__(self):
        return '%s\n' % pXmlBaseElement.__str__(self) +\
               'Name    : %s\n' % self.__Name         +\
               'Enabled : %s\n' % self.__Enabled


if __name__ == '__main__':
    from xml.dom  import minidom
    logging.basicConfig(level=logging.DEBUG)
    doc = minidom.parse(file('../xml/config.xml'))
    for element in doc.getElementsByTagName('alarmList'):
        print pXmlElement(element)
