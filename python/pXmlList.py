
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

    ## @brief Return a disctionary containing all the enabled elements
    #  contained into the list.
    #
    #  Note that the dictionary elements are dom elements, not pXmlElement
    #  objects. The dictionary is indexed by element name.
	
    def getEnabledElementsDict(self, elementName):
        outputDict = {}
        for domElement in self.getElementsByTagName(elementName):
	    xmlElement = pXmlElement(domElement)
	    if xmlElement.Enabled:
	      outputDict[xmlElement.Name] = domElement
        return outputDict

    def getEnabledItems(self, elementName):
        return self.getEnabledElementsDict(elementName).items()

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
    doc = minidom.parse(file('../xml/config.xml'))
    for element in doc.getElementsByTagName('alarmList'):
        list = pXmlList(element)
        print list
        print list.getEnabledElementsDict('alarmSet')
