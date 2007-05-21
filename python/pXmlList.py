
## @package pXmlList
## @brief Description of a xml list.

import logging
import sys

from pXmlElement import pXmlElement


## @brief Class describing a  xml list.
#
#  It is essentially a pXmlElement object with the additional Group
#  member. Subclassed in pXmlInputList and pXmlOutputList.

class pXmlList(pXmlElement):

    ## @brief Constructor
    ## @param self
    #  The class instance.
    ## @param element
    #  The xml element object representing the list. 

    def __init__(self, element):

        ## @var Group
        ## @brief The group which the list belongs to.
        
        pXmlElement.__init__(self, element)
        self.Group = self.getAttribute('group')

    ## @brief Return a disctionary containing all the enabled elements
    #  contained into the list.
    #
    #  Note that the dictionary elements are dom elements, not pXmlElement
    #  objects. The dictionary is indexed by element name.
	
    def getEnabledElementsDict(self, elementName):
        outputDict = {}
        for domElement in self.getElementsByTagName(elementName):
	    xmlElement = pXmlElement(domElement)
	    if xmlElement.isEnabled():
	      outputDict[xmlElement.getName()] = domElement
        return outputDict 

    ## @brief Class representation.
    ## @param self
    #  The class instance.

    def __str__(self):
        return pXmlElement.__str__(self)       +\
               'Group   : %s\n' % self.Group


if __name__ == '__main__':
    from xml.dom  import minidom
    doc = minidom.parse(file('../xml/config.xml'))
    for element in doc.getElementsByTagName('alarmList'):
        list = pXmlList(element)
        print list
        print list.getEnabledElementsDict('alarmSet')
