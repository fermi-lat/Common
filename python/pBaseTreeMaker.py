## @package pBaseTreeMaker
## @brief Package responsible for the creation of a ROOT tree,
#  based on the xml configuration file.

from pSafeROOT import ROOT

## @brief Implementation of the ROOT tree maker.
#
#  The things it needs as an input are:
#  @li A suitable xml parser providing a EnabledVariablesDict variable.
#  @li A path to the output file in which the Tree must be stored.
#  It is responability of the program using this class to set the value
#  of the variables and call the fillTree() method for writing them
#  to the output file

class pBaseTreeMaker:

    ## @brief Contructor.
    ## @param self
    #  The class instance.
    ## @param xmlParser
    #  The parser object responsible for reading the configuration file.
    ## @param outputFilePath
    #  The path to the output ROOT file.
    ## @param treeName
    #  The name of the output ROOT tree.

    def __init__(self, xmlParser, outputFilePath, treeName = 'rootTree'):

        ## @var RootFile
        ## @brief The output ROOT TFile object.

        ## @var RootTree
        ## @brief The output ROOT TTree object.

        ## @var XmlParser
        ## @brief The xml parser responsible for the parsing of the
        #  configuration file.

        ## @var VariablesDictionary
        ## @brief The dictionary containing the tree variables
        #  (which are numpy.array objects).

        self.XmlParser      = xmlParser
        self.OutputFilePath = outputFilePath
        self.OutputFile     = ROOT.TFile(self.OutputFilePath, 'recreate')
        self.RootTree       = ROOT.TTree(treeName, treeName)
        self.VariablesDictionary = {}
        self.__createBranches()

    ## @brief Close the output ROOT file.
    ## @param self
    #  The class instance.
    
    def close(self):
        self.OutputFile.Write()
        self.OutputFile.Close()

    ## @brief Create all the tree branches, based on the information
    #  from the xml parser.
    ## @param self
    #  The class instance.

    def __createBranches(self):
        for variable in self.XmlParser.EnabledVariablesDict.values():
            self.VariablesDictionary[variable.getName()] = variable.Array
            self.__createTreeBranch(variable)

    ## @brief Create the tree branch for a specific variable.
    ## @param self
    #  The class instance.
    ## @param variable
    #  The xml variable representation from the pXmlParser object.

    def __createTreeBranch(self, variable):
        self.RootTree.Branch(variable.getName(),\
                             self.VariablesDictionary[variable.getName()],\
                             variable.LeafList)

    ## @brief Fill the ROOT tree.
    ## @param self
    #  The class instance.

    def fillTree(self):
        self.RootTree.Fill()

    ## @brief Return a specific variable from VariablesDictionary.
    ## @param self
    #  The class instance.
    ## @param name
    #  The VariablesDictionary key corresponding to the desired variable. 

    def getVariable(self, name):
        return self.VariablesDictionary[name]

    ## @brief Reset variable Array
    ## @param self
    #  The class instance.

    def resetVariables(self):
        for variable in self.XmlParser.EnabledVariablesDict.values():
            variable.reset()

    ## @brief Check if a specific variable is defined in the VariablesDictionary
    ## @param self
    #  The class instance.
    ## @param name
    #  The VariablesDictionary key corresponding to the desired variable. 

    def existVariable(self, name):
        return self.VariablesDictionary.has_key(name)
