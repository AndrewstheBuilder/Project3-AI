from tkinter import *
from tkinter import ttk
from tkinter import filedialog
from tkinter import Canvas
from tkinter import Scrollbar
from sympy import to_cnf,symbols
from subprocess import Popen,PIPE
import re


class DataObject:
    '''
    Object to represent attributes, hard constraints, and preferences at a high level
    '''
    parsedAttributes = dict() #dictionary of keys(binary attributes) and their values(integer representations)
    parsedAttributesReversed = dict() #same as above but keys(integer representations) and values(attributes)
    binaryOperators = dict({'NOT':'~','OR':'|','AND':'&'})
    hardConstraints = [] #list of constraints
    hardConstraintsCNF = [] #list of constraints in CNF/digitized form
    preferences = dict({'Penalty Logic':[],'Possibilistic Logic':[],'Qualitative Choice Logic':[]}) #dict of preferences[key is preference name(Qualitative logic,Penalty,Possibilistic)]: value is list[[each preference clause in CNF,etc]]
    symbolsList = [] #for input into sympy.symbols()

    def __init__(self):
        self.fileData = None
        self.fileName = None

    def setFileData(self, data):
        self.fileData = data

    def getFileData(self):
        return self.fileData

    def setFileName(self,name):
        self.fileName = name

    def getFileName(self):
        '''
        :returns name of filepath
        '''
        return self.fileName

    @classmethod
    def inputToClasp(cls,clauses,n):
        '''
        :clauses - cnf form
        :n - input n = 0 to get all models from clasp
        Run clasp with clauses
        :return models from clasp output
        '''
        claspInput = 'p cnf '+str(int(len(cls.symbolsList)/2)) + ' ' + str(len(clauses))
        for c in clauses:
            claspInput += '\n'
            claspInput += ' '.join(c.split('|')) + ' 0' #split on ors and add spaces in between
        # print('clasp input\n',claspName)
        claspFile = './output.cnf'
        with open(claspFile,'w') as o:
            o.write(claspInput)
        p = Popen(["clasp","./output.cnf","-n",str(n)],stdout=PIPE,stderr=PIPE)
        stdout,stderr = p.communicate()
        # if(stderr): print('@inputToClasp stderr',stderr)
        objectsList = cls.extractObjectsFromClaspOutput(str(stdout))
        return objectsList
        # print('@inputToClasp objectsList',objectsList)

    @classmethod
    def modelToString(cls,objects):
        '''
        :returns list of strings of objects from digitized form
        '''
        outputArr = []#array of strings
        for o in objects:
            nums = o.split()
            objStr = '< '
            for n in nums:
                if(n != '0'):
                    objStr +=  cls.parsedAttributesReversed.get(int(n)) + ' '
            objStr += '>'
            outputArr.append(objStr)
        return outputArr

    @classmethod
    def checkIfQualitativeRowGreaterThan(cls,q1,q2):
        '''
        Check if q1 values greater than q2 if so return 1 else return 0
        :q1 - row in qualitative matrix after being evaluated
        :q2 - row to compare against in qualitative matrix after being evaluated
        '''
        #check if q1 and q2 are comparable
        q1IsGreater = False
        q2IsGreater = False
        for i in range(0,len(q1)):
            if(q1[i] == 'inf' and q2[i] != 'inf'):
                q2IsGreater = True
            elif(q1[i] != 'inf' and q2[i] == 'inf'):
                q1IsGreater = True
            elif(q1[i] > q2[i]):
                q1IsGreater = True
            elif(q1[i] < q2[i]):
                q2IsGreater = True
        if(q1IsGreater and q2IsGreater):
            #incomparable rows
            return 0
        elif(q2IsGreater):
            return 0
        elif(q1IsGreater):
            return 1
        else:
            #q1 and q2 probably equivalent
            return 0

    @classmethod
    def exemplify(cls):
        '''
        Generate, if possible, two random feasible objects, and show the
        preference between the two (strict preference or equivalence) w.r.t T
        '''
        objectsList = []
        objectsList = cls.getNObjectsFromClasp(2)
        print('Emplify random objects',objectsList)
        print('Preferences dict',cls.preferences)

        # exemplify for Penalty logic
        penaltyClauses = []
        objectPenalties= [0,0] #object1 penalty,
        for i in range(0,len(objectsList)):
            # print('object in ObjectList',object.split())
            # objectDict[object] = 0#initally 0 penalty
            penaltyClauses = []
            penaltyClauses.extend([o for o in objectsList[i].split() if o != '0'])
            for value in cls.preferences.get('Penalty Logic'):
                print('value[0]',value[0])
                temp = penaltyClauses.copy()
                temp.extend([v for v in value[0].split('&')])
                models = cls.inputToClasp(temp,1)
                if(models == None or models == []):
                    #apply penalty value[1]
                    # print('Apply penalty for object',object)
                    # print('Apply penalty value',value)
                    objectPenalties[i] += value[1]
                # print('objectDict',objectPenalties)
                # print('models',models)
        if(objectPenalties[0] == objectPenalties[1]):
            print('Objects are equivalent')
            modelList = cls.modelToString(objectsList)
            top1 = Toplevel()
            top1.geometry("750x250")
            top1.title("Exemplify")
            popupText = 'Penalty Logic'
            popupText += '\nObjects are equivalent'
            for m in range(0,len(modelList)):
                popupText += '\n' + str(m+1) + '.' + modelList[m]
            Label(top1, text=(popupText), font=('12')).place(x=150,y=80)
        else:
            preferredObjectNum = objectPenalties.index(min(objectPenalties))
            modelList = cls.modelToString(objectsList)
            print('modelList',modelList)
            print('preference',(preferredObjectNum+1))
            top1 = Toplevel()
            top1.geometry("750x250")
            top1.title("Exemplify")
            popupText = 'Penalty Logic'
            popupText += '\nPreferred Object is '+ str(preferredObjectNum+1)
            for m in range(0,len(modelList)):
                popupText += '\n' + str(m+1) + '.' + modelList[m]
            Label(top1, text=(popupText), font=('12')).place(x=150,y=80)

        #exemplify for Possibilistic
        possibilisticClauses = []
        objectPref= [1,1]
        for i in range(0,len(objectsList)):
            # print('object in ObjectList',object.split())
            # objectDict[object] = 0#initally 0 penalty
            possibilisticClauses = []
            possibilisticClauses.extend([o for o in objectsList[i].split() if o != '0'])
            for value in cls.preferences.get('Possibilistic Logic'):
                # print('value[0]',value[0])
                temp = possibilisticClauses.copy()
                temp.extend([v for v in value[0].split('&')])
                models = cls.inputToClasp(temp,1)
                if(models == None or models == []):
                    #Do 1 - possibilistic value
                    # print('Apply penalty for object',object)
                    # print('Apply penalty value',value)
                    pref = 1 - value[1]
                    if(objectPref[i]>pref):
                        #the lowest preference wins out for each object
                        objectPref[i] = pref
                # print('objectDict',objectPenalties)
                # print('models',models)
        if(objectPref[0] == objectPref[1]):
            print('Objects are equivalent')
            modelList = cls.modelToString(objectsList)
            # top1 = Toplevel()
            # top1.geometry("750x250")
            # top1.title("Exemplify")
            # popupText = 'Penalty Logic'
            # popupText += '\nObjects are equivalent'
            # for m in range(0,len(modelList)):
            #     popupText += '\n' + str(m+1) + '.' + modelList[m]
            # Label(top1, text=(popupText), font=('12')).place(x=150,y=80)
        else:
            preferredObjectNum = objectPref.index(max(objectPref))
            modelList = cls.modelToString(objectsList)
            print('modelList',modelList)
            print('possibilistic preference',(preferredObjectNum+1))
            # top1 = Toplevel()
            # top1.geometry("750x250")
            # top1.title("Exemplify")
            # popupText = 'Penalty Logic'
            # popupText += '\nPreferred Object is '+ str(preferredObjectNum+1)
            # for m in range(0,len(modelList)):
            #     popupText += '\n' + str(m+1) + '.' + modelList[m]
            # Label(top1, text=(popupText), font=('12')).place(x=150,y=80)

        #exemplify for Qualitative
        qualitativeMatrix = [['inf','inf'],['inf','inf']] #list of lists each list inside will be for a single object
        clauseNum = 0 #which clause am I on?
        for i in range(0,len(objectsList)):
            for value in cls.preferences.get('Qualitative Choice Logic'):
                qualClause = value[0] #dict
                implies = value[1] #digitized value of implication attribute
                if(implies != None):
                    print('implies,objectsList[i]:' +str(implies) + ' ' +objectsList[i])
                    print('re.match(str(implies),objectsList[i]',re.match(str(implies),objectsList[i]))
                    implicationPass = re.match(str(implies),objectsList[i])
                    if(implicationPass == None):
                        continue
                claspInput = []
                claspInput.extend([o for o in objectsList[i].split() if o != '0'])
                for partOfClause,partOfClauseOrder in qualClause.items():
                    print('typeof partOfClauseOrder',type(partOfClauseOrder))
                    claspInput.extend([v for v in partOfClause.split('&')])
                    models = cls.inputToClasp(claspInput,1)
                    if(models == None or models == []):
                        #clause not matched
                        continue
                    else:
                        #clause matched
                        if(qualitativeMatrix[i][clauseNum] == 'inf' or qualitativeMatrix[i][clauseNum] > partOfClauseOrder):
                            #a greater priority partialClause has passed
                            #ex: gun and car BT gun and cake. gun and car passed so update with 1 in this case
                            qualitativeMatrix[i][clauseNum] = partOfClauseOrder
                clauseNum += 1 #moving on to next clause

        #figure out precedence for qualitative logic in exemplify()
        qGreaterThan = [0]*len(qualitativeMatrix) #how many times is qualitative matrix row at q(see below) greater than all of the other rows
        for q in range(0,len(qualitativeMatrix)):
            for qual in qualitativeMatrix:
                qGreaterThan[q] += cls.checkIfQualitativeRowGreaterThan(qualitativeMatrix[q],qual)

        print('qualitative matrix after',qualitativeMatrix)
        print('QualClauses',cls.preferences.get('Qualitative Choice Logic'))
        print('Generated objects',objectsList)
        if(qGreaterThan[0] == qGreaterThan[1]):
            print('Objects are equivalent according QCL')
        else:
            print('Preference is for object:',(qGreaterThan.index(max(qGreaterThan))+1))

    @classmethod
    def extractObjectsFromClaspOutput(cls,output):
        '''
        Find objects from clasp output
        :returns list of objects
        '''
        # print('Clasp output',output)
        # print('Clasp output type',type(output))
        # print('Satisfiable models\n',re.findall(r'-?[0-9] -?[0-9] -?[0-9] -?[0-9] -?[0-9] -?[0-9] -?[0-9] -?[0-9] 0',output))
        regexToExtractObjects = r'-?[0-9] '*(int(len(cls.symbolsList)/2)) + r'0'
        # print(regexToExtractObjects)
        return re.findall(regexToExtractObjects,output)

    @classmethod
    def getNObjectsFromClasp(cls,n):
        '''
        :n - number of objects needed from clasp, n should be 0 to get all objects
        :returns objectsList - n objects in digitized form
        '''
        objectsList = []
        if(cls.checkSatisfy() == True):
            clauses = []
            for cnfConstraint in cls.hardConstraintsCNF:
                clauses.extend(cnfConstraint.split('&')) #every & is a new line in clasp
            claspInput = 'p cnf '+str(int(len(cls.symbolsList)/2)) + ' ' + str(len(clauses))
            for c in clauses:
                claspInput += '\n'
                claspInput += ' '.join(c.split('|')) + ' 0' #split on ors and add spaces in between
            # print('clasp input\n',claspName)
            claspFile = './output.cnf'
            with open(claspFile,'w') as o:
                o.write(claspInput)
            p = Popen(["clasp","./output.cnf","-n",str(n)],stdout=PIPE,stderr=PIPE)
            stdout,stderr = p.communicate()
            # if(stderr): print('@getNObjectsFromClasp stderr',stderr)
            objectsList = cls.extractObjectsFromClaspOutput(str(stdout))
        else:
            top = Toplevel()
            top.geometry("750x250")
            top.title("ERROR")
            Label(top, text=('ERROR NOT SATISFIABLE'), font=('18')).place(x=150,y=80)
        return objectsList

    @classmethod
    def addToPreferences(cls,key,value):
        '''
        Append to preferences dict[key].list.append()
        '''
        cls.preferences[key].append(value)

    @classmethod
    def addToParsedAttributes(cls,attribute, index):
        '''
        Add to parsed attributes dictionary and symbols list
        '''
        if(str(index) not in cls.symbolsList):
            cls.symbolsList.append(str(index))
        cls.parsedAttributes[attribute] = index
        cls.parsedAttributesReversed[index] = attribute
        # print('@ add method',cls.parsedAttributes)

    @classmethod
    def clearAttributes(cls):
        '''
        clear everything that is used in reading in attributes file
        '''
        cls.symbolsList = []
        cls.parsedAttributes = dict()
        cls.parsedAttributesReversed = dict()
        print("CLEARED ATTRIBUTES DATA")

    @classmethod
    def clearHardConstraints(cls):
        '''
        clear everything used in reading in hard constraints file
        '''
        cls.hardConstraints = []
        cls.hardConstraintsCNF = []
        print("CLEARED HARD CONSTRAINTS DATA")

    @classmethod
    def clearPreferences(cls):
        '''
        clear everything used in reading in Preferences file
        '''
        cls.preferences = dict()
        print("CLEARED PREFERENCES DATA")

    @classmethod
    def printParsedAttributes(cls):
        '''
        Test to see if parsed attributes are there
        '''
        print('ParsedAttributes dict',cls.parsedAttributes)
        print('symbols',cls.symbolsList)

    @classmethod
    def getAttribute(cls,key):
        '''
        :returns parsedAttributes[key] -> int (value)
        '''
        # print('parsedAttributes from getAttribute()', cls.parsedAttributes)
        return cls.parsedAttributes.get(key)

    @classmethod
    def addToHardConstraints(cls,term):
        '''
        Add string to hardConstraints list
        '''
        #print('addToHardConstraints',term)
        cls.hardConstraints.append(term)

    @classmethod
    def printHardConstraints(cls):
        '''
        Test to see if hardConstraints list is populated
        '''
        print(cls.hardConstraints)

    @classmethod
    def convertHardCToCNF(cls):
        '''
        Converts hard constraints to CNF
        Adds to cls.hardConstraintsCNF
        '''
        symbolRep = symbols(" ,".join(cls.symbolsList))
        for term in cls.hardConstraints:
            evalStr = ''
            for letter in term:
                if(letter in cls.symbolsList):
                    index = cls.symbolsList.index(letter)
                    evalStr += 'symbolRep['+str(index)+']'
                else:
                    #letter will be AND(&), OR(|)
                    evalStr += letter
            # print('evalStr:\t',evalStr)
            # print('to_cnf(evalStr):\t',to_cnf(eval(evalStr)))
            cls.hardConstraintsCNF.append(str(to_cnf(eval(evalStr))))

    @classmethod
    def convertToCNF(cls,clause):
        '''
        Convert data to CNF
        :clause - singular clause with ANDs and ORs no extra info
        :return CNF converted string
        '''
        symbolRep = symbols(" ,".join(cls.symbolsList))
        dataArr = clause.split() #split by spaces
        evalStr = ''
        for d in dataArr:
            # print('d in dataARR',d)
            # print('getAttr',cls.getAttribute(d))
            # print('(cls.getAttribute(d)) in cls.symbolsList',(cls.getAttribute(d)) in cls.symbolsList)
            # print('symbolsList',cls.symbolsList)
            dNum = str(cls.getAttribute(d))
            if(dNum in cls.symbolsList):
                index = cls.symbolsList.index(dNum)
                evalStr += 'symbolRep['+str(index)+']'
            else:
                evalStr += ' ' +cls.binaryOperators.get(d)+' '
        # print('@ convertToCNF evalStr',evalStr)
        # print('@ convertToCNF to_cnf(evalStr):\t',to_cnf((eval(evalStr))))
        return str(to_cnf((eval(evalStr))))

    # @classmethod
    # def convertToCNFforQualitative(cls,data):
    #     '''
    #     Convert data to CNF for Qualitative Choice Logic
    #     :returns CNF converted string
    #     '''
    #     symbolRep = symbols(" ,".join(cls.symbolsList))
    #     dataArr = data.split() #split by spaces
    #     evalStr = ''
    #     for d in dataArr:
    #         # print('d in dataARR',d)
    #         # print('getAttr',cls.getAttribute(d))
    #         # print('(cls.getAttribute(d)) in cls.symbolsList',(cls.getAttribute(d)) in cls.symbolsList)
    #         # print('symbolsList',cls.symbolsList)
    #         dNum = str(cls.getAttribute(d))
    #         if(dNum in cls.symbolsList):
    #             index = cls.symbolsList.index(dNum)
    #             evalStr += 'symbolRep['+str(index)+']'
    #         else:
    #             evalStr += ' ' +cls.binaryOperators.get(d)+' '
    #     print('@ convertToCNF evalStr',evalStr)
    #     print('@ convertToCNF to_cnf(evalStr):\t',to_cnf((eval(evalStr))))
    #     return str(to_cnf((eval(evalStr))))

    @classmethod
    def checkSatisfy(cls):
        '''
        clasp format:
        p cnf #of attributes #of clauses
        ...hard constraints
        ...preferences TODO
        :return True if SATISFIABLE else False
        '''
        cls.convertHardCToCNF()
        clauses = []
        for cnfConstraint in cls.hardConstraintsCNF:
            clauses.extend(cnfConstraint.split('&')) #every & is a new line in clasp

        # print('Inside input to clasp function',cls.hardConstraintsCNF)
        claspInput = 'p cnf '+str(int(len(cls.symbolsList)/2)) + ' ' + str(len(clauses))
        for c in clauses:
            claspInput += '\n'
            claspInput += ' '.join(c.split('|')) + ' 0' #split on ors and add spaces in between
        # print('clasp input\n',claspName)
        claspFile = './output.cnf'
        with open(claspFile,'w') as o:
            o.write(claspInput)
        p = Popen(["clasp","./output.cnf"],stdout=PIPE,stderr=PIPE)
        stdout,stderr = p.communicate()
        # print('stdout\n',stdout)
        print('UNSATISFIABLE:\t','UNSATISFIABLE' in str(stdout))
        satisfy = not 'UNSATISFIABLE' in str(stdout)
        top= Toplevel()
        top.geometry("750x250")
        top.title("Satisfiability Output")
        Label(top, text=('FEASIBLE OBJECTS EXIST' if satisfy else 'FEASIBLE OBJECTS DO NOT EXIST'), font=('18')).place(x=150,y=80)
        #cls.parseClaspOutput(str(stdout))
        return satisfy
        # print('stderr\n',stderr)




#
#
#Below three classes inherit from DataObject class
#
#

class AttributeObject(DataObject):
    '''
    Object to represent Attributes
    '''
    def __init__(self, attrFileData=None):
        self.setFileData(attrFileData)
        self.type = 'attr'

    def parseFileData(self,fileData):
        '''
        Parse file data for Attribute File and save it to a data structure
        '''
        #self.clearAttributes()
        #print('Inside attribute class\n',fileData)
        lines = fileData.split('\n')#get each line
        parsedAttributeIndex = 1 #will contribute to creating integer version of attributes
        for line in lines:
            lineToSplit = line.replace(',',' ')
            attributes = lineToSplit.split()
            #print(attributes)
            self.addToParsedAttributes(attributes[1],parsedAttributeIndex)
            #self.addToParsedAttributes('NOT '+attributes[1],-1*parsedAttributeIndex)
            self.addToParsedAttributes(attributes[2],-1*parsedAttributeIndex)#NOT attributes[1] == attributes[2]
            parsedAttributeIndex += 1

        self.printParsedAttributes()

class HardConstraintObject(DataObject):
    '''
    Object to represent Hard Constraints
    '''
    def __init__(self, hardCFileData=None):
        self.setFileData(hardCFileData)
        self.type = 'hardc'

    def parseFileData(self,fileData):
        '''
        Parse file data for Constraint file and save it to array of strings
        '''
        #self.clearHardConstraints()
        lines = fileData.split('\n')#get each line
        for line in lines:
            terms = line.split(' ')
            negate = 1
            constraintList = []
            for term in terms:
                if(term.upper() == 'NOT'):
                    negate = -1
                    continue
                elif(term.upper() == 'AND'):
                    constraintList.append(' & ')
                elif(term.upper() == 'OR'):
                    constraintList.append(' | ')
                elif(term == '(' or term == ')'):
                    constraintList.append(term)
                else:
                    #has to be a binary attribute
                    constraintList.append(str(negate * self.getAttribute(term)))
                    negate = 1 #reset negate variable to 1 after use
            self.addToHardConstraints(constraintList)
        self.printHardConstraints()

class PreferencesObject(DataObject):
    '''
    Object to represent Preferences
    '''
    def __init__(self, prefFileData=None):
        self.setFileData(prefFileData)
        self.type = 'pref'

    def transformPenaltyData(self,data):
        '''
        Transforms Penalty clause,Penalty to (CNF) Penalty clause,Penalty
        Ex:gun AND cake, 10 -> [[gun,cake],10]
        :returns transformedPenaltyList
        '''
        # print('@ transformPenaltyData()',data)
        PenaltyClause,PenaltyNum = [d.strip() for d in data.split(",")]
        # print('@ transformPenaltyData() PenaltyClause,PenaltyNum:' + PenaltyClause + ' ' +PenaltyNum)
        PenaltyClauseCNF = self.convertToCNF(PenaltyClause)
        return [PenaltyClauseCNF,int(PenaltyNum)]

    def transformPossibilisticData(self,data):
        '''
        Transforms Possibilistic clause,Preference to (CNF) Possibilistic clause,Preference
        Ex:gun AND cake, 10 -> [[gun,cake],10]
        :returns transformedPossibilisticList
        '''
        # print('@ transformPossiData()',data)
        possiClause,possiNum = [d.strip() for d in data.split(",")]
        # print('@ transformPossiData() PossiClause,PossiNum:' + possiClause + ' ' +possiNum)
        possiClauseCNF = self.convertToCNF(possiClause)
        return [possiClauseCNF,float(possiNum)]

    def transformQualitativeChoiceData(self,data):
        '''
        :returns [{clause CNF form,orderNum},IF]
        '''
        # print('transform qualitative choice data:',data)
        qualClauseStr,qualImplies = [i.strip() for i in data.split('IF')]
        qualClauses = [i.strip() for i in qualClauseStr.split('BT')]
        # print('@transform qual data qualClause,qualImplies' + qualClauseStr +','+qualImplies)
        tempDict = dict()
        for j in range(0,len(qualClauses)):
            qualCNFStr = self.convertToCNF(qualClauses[j])
            # print('qualCNFstr',qualCNFStr)
            tempDict[qualCNFStr] = (j+1) #order of clause is (j+1)
        return [tempDict,self.getAttribute(qualImplies)]

    def parseFileData(self,fileData):
        '''
        Parse Preferences file
        '''
        lines = fileData.split('\n')
        #print(lines)
        penalty = False
        possib = False
        qualit = False
        for line in lines:
            if(line.strip() == ''):
                continue
            if(line == 'Penalty Logic'):
                penalty = True
                qualit = False
                possib = False
                continue
            elif(line == 'Possibilistic Logic'):
                possib = True
                penalty = False
                qualit = False
                continue
            elif(line == 'Qualitative Choice Logic'):
                qualit = True
                penalty = False
                possib = False
                continue
            if(penalty):
                transformedPenaltyData = self.transformPenaltyData(line)
                # print('@ parseFileData() transformedPenaltyData',transformedPenaltyData)
                self.addToPreferences('Penalty Logic',transformedPenaltyData)
            elif(possib):
                transformedPossibilisticData = self.transformPossibilisticData(line)
                # print('@ parseFileData() transformedPossibilisticData',transformedPossibilisticData)
                self.addToPreferences('Possibilistic Logic',transformedPossibilisticData)
            elif(qualit):
                transformedQualitativeData = self.transformQualitativeChoiceData(line)
                # print('@ parseFileData() transformedQualitativeData',transformedQualitativeData)
                self.addToPreferences('Qualitative Choice Logic',transformedQualitativeData)
        print('after adding to Preferences datastructure',self.preferences)

class UI:
    '''
    Creates a Canvas and everything that goes with it
    '''

    #static class variable
    global columnNum, columnNum2, buttonText
    columnNum = 0
    columnNum2 = 0 #for tab2
    buttonText = {'attr':"Attributes", 'hardc':"Hard Constraints", 'pref':"Preferences"}
    buttonsToDisable = [] #list of buttons to disable and enable
    def __init__(self,dataObject,frame,tab='tab1'):
        '''
        Initialize UI object. Window has already been initialized. Canvas becomes a instance of every UI object
        '''
        self.dataObject = dataObject
        self.frame = frame
        self.canvas = None
        self.uniqueTag = self.dataObject.type
        if(tab=='tab1'):
            self.createCanvasForInputTab()
        elif(tab=='tab2'):
            self.createCanvasForOutputTab()

    def parseFileData(self,fileData):
        '''
        Calls dataObjects parseFileData()
        '''
        self.dataObject.parseFileData(fileData)

    def setFileData(self, fileData):
        '''
        Set file data to dataObject assigned to UI Object
        '''
        self.dataObject.setFileData(fileData)

    def getFileData(self):
        '''
        Get file data from dataObject assigned to UI Object
        '''
        return self.dataObject.getFileData()

    def setFileName(self, fileName):
        '''
        Set file name to dataObject assigned to UI Object
        '''
        self.dataObject.setFileName(fileName)

    def getFileName(self):
        '''
        Get file name from dataObject assigned to UI object
        '''
        return self.dataObject.getFileName()

    def getType(self):
        return self.dataObject.type

    def checkSatisfy(self):
        '''
        Call DataObject.checkSatisfy()
        '''
        self.dataObject.checkSatisfy()

    def exemplify(self):
        '''
        Call DataObject.exemplify()
        '''
        self.dataObject.exemplify()

    def createCanvasForInputTab(self):
        '''
        Create Canvas to insert text
        '''
        global columnNum, buttonText

        #scrollbar
        h = ttk.Scrollbar(self.frame, orient=HORIZONTAL)
        v = ttk.Scrollbar(self.frame, orient=VERTICAL)

        #create canvas
        self.canvas = Canvas(self.frame, width=250, height=300, bg="white", scrollregion=(0, 0, 1000, 1000), yscrollcommand=v.set, xscrollcommand=h.set)
        h['command'] = self.canvas.xview
        v['command'] = self.canvas.yview

        self.canvas.grid(column=columnNum, row=0,padx=20, sticky=(N,W,E,S))
        h.grid(column=columnNum, row=1, sticky=(W,E))
        v.grid(column=(columnNum+1), row=0, sticky=(N,S))

        #button to insert
        ttk.Label(self.frame, text=buttonText[self.getType()],borderwidth=3, relief="raised").grid(column=columnNum, row=2)
        b1 = ttk.Button(self.frame, text="Insert a file", command=self.selectFile)
        b1.grid(column=columnNum, row=3)
        if(self.getType() != 'attr'):
            self.buttonsToDisable.append(b1)
        if(self.getType() == 'pref'):
            b2=ttk.Button(self.frame, text="Check if Feasible Objects", command=self.checkSatisfy)
            b2.grid(column=8, row=1,pady=5)
            b3=ttk.Button(self.frame, text="Exemplification", command=self.exemplify)
            b3.grid(column=8, row=2, pady=5)
            b4=ttk.Button(self.frame, text="Optimization", command=self.checkSatisfy)
            b4.grid(column=8, row=3, pady=5)
            b5=ttk.Button(self.frame, text="Omni-Optimization", command=self.checkSatisfy)
            b5.grid(column=8, row=4, pady=5)
            self.buttonsToDisable.append(b2)
            self.buttonsToDisable.append(b3)
            self.buttonsToDisable.append(b4)
            self.buttonsToDisable.append(b5)
        columnNum +=2 #for tab1 placement
        self.disableButtons()

    def createCanvasForOutputTab(self):
        '''
        Create Canvas to insert text
        '''
        global columnNum2, buttonText

        #scrollbar
        h = ttk.Scrollbar(self.frame, orient=HORIZONTAL)
        v = ttk.Scrollbar(self.frame, orient=VERTICAL)

        #create canvas
        self.canvas = Canvas(self.frame, width=250, height=300, bg="white", scrollregion=(0, 0, 1000, 1000), yscrollcommand=v.set, xscrollcommand=h.set)
        h['command'] = self.canvas.xview
        v['command'] = self.canvas.yview

        self.canvas.grid(column=columnNum, row=0,padx=20, sticky=(N,W,E,S))
        h.grid(column=columnNum, row=1, sticky=(W,E))
        v.grid(column=(columnNum+1), row=0, sticky=(N,S))

        #button to insert
        ttk.Label(self.frame, text=buttonText[self.getType()],borderwidth=3, relief="raised").grid(column=columnNum, row=2)
        # b1 = ttk.Button(self.frame, text="Insert a file", command=self.selectFile)
        # b1.grid(column=columnNum, row=3)
        # if(self.getType() != 'attr'):
        #     self.buttonsToDisable.append(b1)
        # if(self.getType() == 'pref'):
        #     b2=ttk.Button(self.frame, text="Check if Feasible Objects", command=self.checkSatisfy)
        #     b2.grid(column=8, row=1,pady=5)
        #     b3=ttk.Button(self.frame, text="Exemplification", command=self.exemplify)
        #     b3.grid(column=8, row=2, pady=5)
        #     b4=ttk.Button(self.frame, text="Optimization", command=self.checkSatisfy)
        #     b4.grid(column=8, row=3, pady=5)
        #     b5=ttk.Button(self.frame, text="Omni-Optimization", command=self.checkSatisfy)
        #     b5.grid(column=8, row=4, pady=5)
            # self.buttonsToDisable.append(b2)
            # self.buttonsToDisable.append(b3)
            # self.buttonsToDisable.append(b4)
            # self.buttonsToDisable.append(b5)
        columnNum +=2 #for tab1 placement
        # self.disableButtons()

    @classmethod
    def disableButtons(cls):
        '''
        disables buttons in buttonsToDisable list
        '''
        for button in cls.buttonsToDisable:
            # print(button)
            button.state(['disabled'])

    @classmethod
    def enableButtons(cls):
        '''
        enables all buttons in buttonsToDisable list
        '''
        # print('its hitting',cls.buttonsToDisable)
        for button in cls.buttonsToDisable:
            # print(button)
            button.state(['!disabled'])

    def printFileData(self):
        '''
        Test to see if file data got saved
        '''
        print("File name:",self.getFileName())
        print("File data:\n",self.getFileData())

    def selectFile(self):
        '''
        Open a file and read data from it
        '''
        file = filedialog.askopenfilename(initialdir = "../assets", title=("Select a file"), filetypes=(("Text file", "*.txt*"),("Any File", "*.*")))
        self.setFileName(file)

        #reset canvas before inserting text
        self.canvas.delete(self.uniqueTag)

        #read from file and set file data
        if(file):
            if(self.getType()=='attr'):
                # print('it hits here')
                self.enableButtons()
            fileObj = open(file)
            fileData = fileObj.read()
            self.canvas.create_text(10, 10, text=fileData, anchor='nw', tag=self.uniqueTag)
            self.setFileData(fileData)
            self.parseFileData(fileData)
            #self.printFileData()
            fileObj.close()
        else:
            #no file selected
            if(self.getType() == 'attr'):
                self.disableButtons()


#Create a GUI
root = Tk()
root.title('Project 3 - AI')
root.geometry("1150x500")

#create a notebook for tabs
notebook = ttk.Notebook(root)
notebook.pack(pady=10, expand=True)

#create frames
frame1 = ttk.Frame(notebook, width=1150, height=500)
frame2 = ttk.Frame(notebook, width=1150, height=500)
frame1.grid()
frame2.grid()

#add frames to notebook
notebook.add(frame1, text="Input")
notebook.add(frame2, text="Output")

#All Objects for tab1 of UI

#Create Attribute UI
attrObj = AttributeObject()
attrUI = UI(attrObj,frame1)

#Create Hard Constraints UI
hardCObj = HardConstraintObject()
hardCUI = UI(hardCObj,frame1)

#Create Preferences UI
prefObj = PreferencesObject()
prefUI = UI(prefObj, frame1)

#create output page
outputUI1 = UI(attrObj,frame2,'tab2')
outputUI2 = UI(hardCObj,frame2,'tab2')
outputUI3 = UI(prefObj,frame2,'tab2')

root.mainloop()