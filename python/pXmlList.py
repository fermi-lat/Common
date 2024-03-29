## @package pXmlList
## @brief Description of a xml list.

import sys

from pXmlElement import pXmlElement


## @brief Class describing a  xml list.
#
#  It is essentially a pXmlElement object with the additional Group
#  member. Subclassed in pXmlInputList, pXmlOutputList and
#  pXmlAlarmList.

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

    ## @brief Return a list containing all the enabled elements
    #  contained into the list.
    #
    #  Note that the list elements are dom elements, not pXmlElement
    #  objects.
    ## @param self
    #  The class instance.
    ## @param elementName
    #  The element name.
	
    def getEnabledElementsList(self, elementName):
        outputList = []
        for domElement in self.getElementsByTagName(elementName):
	    xmlElement = pXmlElement(domElement)
	    if xmlElement.Enabled:
	      outputList.append(domElement)
        return outputList

    ## @brief Return all the enabled dom elements corresponding to a given
    #  element name.
    ## @param self
    #  The class instance.
    ## @param elementName
    #  The element name.

    def getEnabledItems(self, elementName):
        return self.getEnabledElementsList(elementName)

    ## @brief Return a formatted text representation of the class instances.
    ## @param self
    #  The class instance.

    def getTextSummary(self):
        return pXmlElement.getTextSummary(self) +\
               'Group    : %s' % self.Group

    ## @brief Class representation.
    ## @param self
    #  The class instance.

    def __str__(self):
        return self.getTextSummary()



if __name__ == '__main__':
    from xml.dom  import minidom
    doc = minidom.parse(file('../xml/alarmconfig.xml'))
    for element in doc.getElementsByTagName('alarmList'):
        list = pXmlList(element)
        print list
        print list.getEnabledElementsDict('alarmSet')
