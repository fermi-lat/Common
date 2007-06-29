
## @package pXmlBaseElement
## @brief Description of a minimal xml element.

import logging
import sys

from pGlobals import *

## @brief Class describing a minimal xml element.
#
#  At the lowest level, the class describe a piece of xml looking like:
#  @code
#  <node_name attribute1="..." ... attributeN="...">
#  ...
#  </node_name>
#  @endcode
#  and provides convenience functions for accessing sub-elements, attributes
#  and convert them to non-string objects.

class pXmlBaseElement:

    ## @brief Base constructor.
    ## @param self
    #  The class instance.
    ## @param domElement
    #  A xml element, as returned by the getElementsByTagName()
    #  function of the xml.dom.minidom module.

    def __init__(self, domElement):

        ## @var DomElement
        #  @brief The underlying xml.dom.minidom element.

        ## @var NodeName
        #  The node name of the element.

        self.DomElement = domElement
        self.NodeName   = self.DomElement.nodeName

    ## @brief Return the attribute corresponing to a given attribute name.
    #
    #  The attribute is converted from unicode to standard string,
    #  as needed by numpy.
    #  An optional default value can be provided, in case the attribute does
    #  not exist.
    ## @param self
    #  The class instance.
    ## @param attributeName
    #  The attribute name.
    ## @param default
    #  The default value (returned if the attribute does not exist).

    def getAttribute(self, attributeName, default=None):
        attribute = str(self.DomElement.getAttribute(attributeName))
        if attribute == '':
            logging.debug('Could not find attribute %s for node %s. ' %\
                          (attributeName, self.NodeName)              +\
                          'Returning "%s"...' % default)
            attribute = default
        return attribute

    ## @brief Eval the attribute corresponing to a given attribute name.
    #
    #  An optional default value can be provided, in case the attribute does
    #  not exist, or the eval statement fails.
    ## @param self
    #  The class instance.
    ## @param attributeName
    #  The attribute name.
    ## @param default
    #  The default value (returned if the attribute does not exist or the
    #  eval statement fails).

    def evalAttribute(self, attributeName, default=None):
        attribute = self.getAttribute(attributeName, default)
        if attribute == default:
            return default
        try:
            return eval(attribute)
        except:
            logging.error('Could not eval attribute %s for node %s. ' %\
                          (attributeName, self.NodeName)              +\
                          'Returning %s...' % default)
            return default

    ## @brief Return a list of dom elements corrisponding to a given tag
    #  name.
    #
    #  If there are no such elements, an empty list is returned instead.
    ## @param self
    #  The class instance.
    ## @param tagName
    #  The tag name
    
    def getElementsByTagName(self, tagName):
        return self.DomElement.getElementsByTagName(tagName)

    ## @brief Return a single dom element corresponding to a given tag name.
    #
    #  This function should be used for those tag that apperar exactly once
    #  into the underlying DomElement.
    #  An optional default value can be provided, to be returned in case there
    #  are no tags corresponding to the given tag name. If the tags are
    #  multiply defined, an error message is printed and the first is
    #  returned.
    ## @param self
    #  The class instance.
    ## @param tagName
    #  The tag name
    ## @param default
    #  The value to be returned in case there are no tags corresponding to a
    #  given tag name.

    def getElementByTagName(self, tagName, default=None):
        elementsList = self.getElementsByTagName(tagName)
        if elementsList == []:
            return default
        elif len(elementsList)> 1:
            logging.error('Tag %s multiply defined for node %s. ' %\
                          (tagName, self.NodeName)                +\
                          'Returning the first one...')
        return elementsList[0]

    ## @brief Get the content of a particular tag (supposingly defined
    #  exactly once).
    ## @param self
    #  The class instance.
    ## @param tagName
    #  The tag name
    ## @param default
    #  The value to be returned in case there are no tags corresponding to a
    #  given tag name or the tag has no value.
    
    def getTagValue(self, tagName, default=None):
        element = self.getElementByTagName(tagName, default)
        if element == default:
            return default
        try:
            return str(element.childNodes[0].data).strip()
        except:
            return default

    ## @brief Eval the content of a particular tag (supposingly defined
    #  exactly once).
    ## @param self
    #  The class instance.
    ## @param tagName
    #  The tag name
    ## @param default
    #  The value to be returned in case there are no tags corresponding to a
    #  given tag name or the tag has no value or the eval statement fails
    #  for some reason.

    def evalTagValue(self, tagName, default=None):
        value = self.getTagValue(tagName, default)
        if value == default:
            return default
        try:
            return eval(self.getTagValue(tagName))
        except:
            return default

    def getTextSummary(self):
        return 'Node name: %s' % self.NodeName 

    ## @brief Class representation.
    ## @param self
    #  The class instance.  

    def __str__(self):
        return self.getTextSummary()


if __name__ == '__main__':
    from xml.dom  import minidom
    logging.basicConfig(level=logging.DEBUG)
    doc = minidom.parse(file('../xml/config.xml'))
    for domElement in doc.getElementsByTagName('alarmList'):
        xmlElement = pXmlBaseElement(domElement)
        print 'Printing pXmlBaseElement object...'
        print xmlElement
        print
        print 'Printing "enabled" attribute...'
        print xmlElement.evalAttribute('enabled')
        print 
        print 'Printing "enableds" attribute (with default False)...'
        print xmlElement.evalAttribute('enableds', False)
        print
        print 'Printing miscellanea...'
        print xmlElement.getElementsByTagName('parameter')
        print xmlElement.getElementsByTagName('parameters')
        print xmlElement.getElementByTagName('warning_limits')
        print xmlElement.getTagValue('parameter')
