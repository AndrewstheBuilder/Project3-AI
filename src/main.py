from tkinter import *
from tkinter import ttk
from tkinter import filedialog
from tkinter import Canvas
from tkinter import Scrollbar
from typing import OrderedDict
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
        :clauses - list of digitized strings in cnf form. CNF forms have been split by AND before being passed into clauses. No ANDs allowed in clauses
        :n - input n = 0 to get all models from clasp
        Run clasp with clauses
        :return models from clasp output
        '''
        claspInput = 'p cnf '+str(int(len(cls.symbolsList)/2)) + ' ' + str(len(clauses))
        for c in clauses:
            claspInput += '\n'

            #handle ~(NOT) conversions. Convert ~ to -1* because that is what not is.
            #~-1 = 1, ~1 = -1
            for individualVariable in  c.split('|'):
                #split on ors and add spaces in between the individualVariable inputs
                cReplacedNot = individualVariable.replace('~','-1*')#if individualVariable contains a NOT it will be evaluated
                evalulatedStr = str(eval(cReplacedNot))
                claspInput += evalulatedStr + ' '
            claspInput += ' 0'
        claspFile = './output.cnf'
        with open(claspFile,'w') as o:
            o.write(claspInput)
        p = Popen(["clasp","./output.cnf","-n",str(n)],stdout=PIPE,stderr=PIPE)
        stdout,stderr = p.communicate()
        objectsList = cls.extractObjectsFromClaspOutput(str(stdout))
        return objectsList

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
        q1IsOptimal = False
        q2IsOptimal = False
        for i in range(0,len(q1)):
            if(q1[i] == 'inf' and q2[i] != 'inf'):
                q2IsOptimal = True
            elif(q1[i] != 'inf' and q2[i] == 'inf'):
                q1IsOptimal = True
            elif(q1[i] > q2[i]):
                q2IsOptimal = True
            elif(q1[i] < q2[i]):
                q1IsOptimal = True
        if(q1IsOptimal and q2IsOptimal):
            #incomparable rows
            return 0
        elif(q2IsOptimal):
            return 0
        elif(q1IsOptimal):
            return 1
        else:
            #q1 and q2 probably equivalent
            return 0
    @classmethod
    def omnioptimize(cls):
        '''
        find an optimal object w.r.t T.
        '''
        objectsList = []
        objectsList = cls.getNObjectsFromClasp(0)
        omnioptimizeOutputStr = 'OMNI-OPTIMIZATION\n\n'
        modelList = cls.modelToString(objectsList)
        omnioptimizeOutputStr += 'All possible objects:\n'
        for m in range(0,len(modelList)):
            omnioptimizeOutputStr += 'Object '+str(m+1) + '.' + modelList[m] +'\n'
        omnioptimizeOutputStr += '\n'

        #optimize for Penalty logic
        omnioptimizeOutputStr += '\nPenalty Logic:\n'
        objectPenalties = [0]*len(objectsList)
        for i in range(0,len(objectsList)):
            penaltyClauses = []
            penaltyClauses.extend([o.strip() for o in objectsList[i].split() if o != '0'])
            for value in cls.preferences.get('Penalty Logic'):
                temp = penaltyClauses.copy()
                temp.extend([re.sub(r"\(|\)","",v).strip() for v in value[0].split('&')])
                models = cls.inputToClasp(temp,1)
                if(models == None or models == []):
                    objectPenalties[i] += value[1]

        #get all indexes that have the minimum penalty(the most optimal object(s))
        indexList = [index for index, value in enumerate(objectPenalties) if value == min(objectPenalties)]
        for prefIndex in indexList:
            omnioptimizeOutputStr += 'Object '+str((prefIndex+1)) + ' is an optimal object.\n'

        #optimize for Possibilistic Logic
        possibilisticClauses = []
        objectPref= [1]*len(objectsList)
        omnioptimizeOutputStr += '\nPossibilistic Logic:\n'
        for i in range(0,len(objectsList)):
            possibilisticClauses = []
            possibilisticClauses.extend([o for o in objectsList[i].split() if o != '0'])
            for value in cls.preferences.get('Possibilistic Logic'):
                temp = possibilisticClauses.copy()
                temp.extend([re.sub(r"\(|\)","",v).strip() for v in value[0].split('&')])
                models = cls.inputToClasp(temp,1)
                if(models == None or models == []):
                    pref = 1 - value[1]
                    if(objectPref[i]>pref):
                        #the lowest preference wins out for each object
                        objectPref[i] = pref

        indexList = [index for index, value in enumerate(objectPref) if value == max(objectPref)]
        for prefIndex in indexList:
            omnioptimizeOutputStr += 'Object '+str((prefIndex+1)) + ' is an optimal object.\n'

        #optimize for Qualitative Choice Logic
        qualitativeMatrix = [] #list of lists each list inside will be for a single object
        for objectNum in range(0,len(objectsList)):
            qualitativeMatrix.append(['inf']*len(cls.preferences.get('Qualitative Choice Logic')))

        qualRuleNum = 0 #which clause am I on?
        omnioptimizeOutputStr += '\nQualitative Choice Logic:\n'
        for i in range(0,len(objectsList)):
            qualRuleNum = 0 #pretty much serves as the counter for the next for loop
            for value in cls.preferences.get('Qualitative Choice Logic'):
                qualClause = value[0] #dict
                implies = value[1] #digitized value of implication attribute
                if(implies != None):
                    impliesRegex = str(implies)
                    if(implies > 0):
                        impliesRegex = '[^-]'+str(implies)
                    implicationPass = re.search(impliesRegex,objectsList[i])
                    if(implicationPass == None):
                        #implication does not pass -> GoTo next qualitative rule
                        qualRuleNum += 1
                        continue
                #populate qualitative matrix

                for partOfClause,partOfClauseOrder in qualClause.items():
                    claspInput = []
                    claspInput.extend([o for o in objectsList[i].split() if o != '0'])
                    claspInput.extend([re.sub(r"\(|\)","",v).strip() for v in partOfClause.split('&')])
                    models = cls.inputToClasp(claspInput,1)
                    if(models == None or models == []):
                        #clause not matched
                        continue
                    else:
                        #clause matched
                        if(qualitativeMatrix[i][qualRuleNum] == 'inf' or qualitativeMatrix[i][qualRuleNum] > partOfClauseOrder):
                            #a greater priority partialClause has passed
                            #ex: gun and car BT gun and cake. gun and car passed so update with 1 in this case

                            qualitativeMatrix[i][qualRuleNum] = partOfClauseOrder
                qualRuleNum += 1 #moving on to next clause

        #figure out preference for qualitative logic
        #after table is created
        qOptimal = [0]*len(qualitativeMatrix) #this variable will contain how many times is qualitative matrix row at q(see below) greater than all of the other rows
        for q in range(0,len(qualitativeMatrix)):
            for qual in qualitativeMatrix:
                qOptimal[q] += cls.checkIfQualitativeRowGreaterThan(qualitativeMatrix[q],qual)

        # print('Qualitative Choice Logic matrix',qualitativeMatrix)
        indexList = [index for index, value in enumerate(qOptimal) if value == max(qOptimal)]
        for prefIndex in indexList:
            omnioptimizeOutputStr += 'Object '+str((prefIndex+1)) + ' is an optimal object.\n'

        return omnioptimizeOutputStr

    @classmethod
    def optimize(cls):
        '''
        find an optimal object w.r.t T.
        '''
        objectsList = []
        objectsList = cls.getNObjectsFromClasp(0)
        optimizeOutputStr = 'OPTIMIZATION\n\n'
        modelList = cls.modelToString(objectsList)
        optimizeOutputStr += 'All possible objects:\n'
        for m in range(0,len(modelList)):
            optimizeOutputStr += 'Object '+str(m+1) + '.' + modelList[m] +'\n'
        optimizeOutputStr += '\n'

        #optimize for Penalty logic
        optimizeOutputStr += 'Penalty Logic -> '
        objectPenalties = [0]*len(objectsList)
        for i in range(0,len(objectsList)):
            penaltyClauses = []
            penaltyClauses.extend([o.strip() for o in objectsList[i].split() if o != '0'])
            for value in cls.preferences.get('Penalty Logic'):
                temp = penaltyClauses.copy()
                temp.extend([re.sub(r"\(|\)","",v).strip() for v in value[0].split('&')])
                models = cls.inputToClasp(temp,1)
                if(models == None or models == []):
                    objectPenalties[i] += value[1]

        #get all indexes that have the minimum penalty(the most optimal object(s))
        indexList = [index for index, value in enumerate(objectPenalties) if value == min(objectPenalties)]
        preferredObjectNum = indexList.pop()
        optimizeOutputStr += 'Object '+str((preferredObjectNum+1)) + ' is an optimal object.\n'

        #optimize for Possibilistic Logic
        possibilisticClauses = []
        objectPref= [1]*len(objectsList)
        optimizeOutputStr += 'Possibilistic Logic -> '
        for i in range(0,len(objectsList)):
            possibilisticClauses = []
            possibilisticClauses.extend([o for o in objectsList[i].split() if o != '0'])
            for value in cls.preferences.get('Possibilistic Logic'):
                temp = possibilisticClauses.copy()
                temp.extend([re.sub(r"\(|\)","",v).strip() for v in value[0].split('&')])
                models = cls.inputToClasp(temp,1)
                if(models == None or models == []):
                    pref = 1 - value[1]
                    if(objectPref[i]>pref):
                        #the lowest preference wins out for each object
                        objectPref[i] = pref

        indexList = [index for index, value in enumerate(objectPref) if value == max(objectPref)]
        preferredObjectNum = indexList.pop()
        optimizeOutputStr += 'Object '+str((preferredObjectNum+1)) + ' is an optimal object.\n'


        #optimize for Qualitative Choice Logic
        qualitativeMatrix = [] #list of lists each list inside will be for a single object
        for objectNum in range(0,len(objectsList)):
            qualitativeMatrix.append(['inf']*len(cls.preferences.get('Qualitative Choice Logic')))

        # print('Qualitative Matrix initialized',qualitativeMatrix)
        qualRuleNum = 0 #which clause am I on?
        optimizeOutputStr += 'Qualitative Choice Logic -> '
        for i in range(0,len(objectsList)):
            qualRuleNum = 0 #pretty much serves as the counter for the next for loop
            for value in cls.preferences.get('Qualitative Choice Logic'):
                qualClause = value[0] #dict
                implies = value[1] #digitized value of implication attribute
                if(implies != None):
                    impliesRegex = str(implies)
                    if(implies > 0):
                        impliesRegex = '[^-]'+str(implies)
                    implicationPass = re.search(impliesRegex,objectsList[i])
                    if(implicationPass == None):
                        #implication does not pass -> GoTo next qualitative rule
                        qualRuleNum += 1
                        continue

                #populate qualitative matrix
                for partOfClause,partOfClauseOrder in qualClause.items():
                    claspInput = []
                    claspInput.extend([o for o in objectsList[i].split() if o != '0'])
                    claspInput.extend([re.sub(r"\(|\)","",v).strip() for v in partOfClause.split('&')])
                    models = cls.inputToClasp(claspInput,1)
                    if(models == None or models == []):
                        #clause not matched
                        continue
                    else:
                        #clause matched
                        if(qualitativeMatrix[i][qualRuleNum] == 'inf' or qualitativeMatrix[i][qualRuleNum] > partOfClauseOrder):
                            #a greater priority partialClause has passed
                            #ex: gun and car BT gun and cake. gun and car passed so update with 1 in this case

                            # print('qualitativeMatrix[i]',qualitativeMatrix[i])
                            qualitativeMatrix[i][qualRuleNum] = partOfClauseOrder
                qualRuleNum += 1 #moving on to next clause

        #figure out preference for qualitative logic
        #after table is created
        qOptimal = [0]*len(qualitativeMatrix) #this variable will contain how many times is qualitative matrix row at q(see below) greater than all of the other rows
        for q in range(0,len(qualitativeMatrix)):
            for qual in qualitativeMatrix:
                qOptimal[q] += cls.checkIfQualitativeRowGreaterThan(qualitativeMatrix[q],qual)

        indexList = [index for index, value in enumerate(qOptimal) if value == max(qOptimal)]
        preferredObjectNum = indexList.pop()
        optimizeOutputStr += 'Object '+str((preferredObjectNum+1)) + ' is an optimal object.\n'

        return optimizeOutputStr

    @classmethod
    def exemplify(cls):
        '''
        Generate, if possible, two random feasible objects, and show the
        preference between the two (strict preference or equivalence) w.r.t T
        :returns output as string
        '''
        objectsList = []
        objectsList = cls.getNObjectsFromClasp(2)

        exemplifyOutputStr = 'EXEMPLIFICATION\n\n'
        modelList = cls.modelToString(objectsList)
        exemplifyOutputStr += 'Random Objects Generated:\n'
        for m in range(0,len(modelList)):
            exemplifyOutputStr += 'Object '+str(m+1) + '.' + modelList[m] +'\n'
        exemplifyOutputStr += '\n'

        # exemplify for Penalty logic
        exemplifyOutputStr += 'Penalty Logic Preference -> '
        penaltyClauses = []
        objectPenalties= [0,0] #object1 penalty,
        for i in range(0,len(objectsList)):
            penaltyClauses = []
            penaltyClauses.extend([o.strip() for o in objectsList[i].split() if o != '0'])
            for value in cls.preferences.get('Penalty Logic'):
                temp = penaltyClauses.copy()
                temp.extend([re.sub(r"\(|\)","",v).strip() for v in value[0].split('&')])
                models = cls.inputToClasp(temp,1)
                if(models == None or models == []):
                    #apply penalty value[1]
                    objectPenalties[i] += value[1]

        if(objectPenalties[0] == objectPenalties[1]):
            exemplifyOutputStr += 'Objects are equivalent.\n'
        else:
            preferredObjectNum = objectPenalties.index(min(objectPenalties))
            modelList = cls.modelToString(objectsList)
            exemplifyOutputStr += 'Object '+str((preferredObjectNum+1)) + ' is preferred.\n'

        #exemplify for Possibilistic
        possibilisticClauses = []
        objectPref= [1,1]
        exemplifyOutputStr += 'Possibilistic Logic preference -> '
        for i in range(0,len(objectsList)):
            possibilisticClauses = []
            possibilisticClauses.extend([o for o in objectsList[i].split() if o != '0'])
            for value in cls.preferences.get('Possibilistic Logic'):
                # print('value[0]',value[0])
                temp = possibilisticClauses.copy()
                temp.extend([re.sub(r"\(|\)","",v).strip() for v in value[0].split('&')])
                models = cls.inputToClasp(temp,1)
                if(models == None or models == []):
                    #Do 1 - possibilistic value
                    pref = 1 - value[1]
                    if(objectPref[i]>pref):
                        #the lowest preference wins out for each object
                        objectPref[i] = pref
        if(objectPref[0] == objectPref[1]):
            exemplifyOutputStr += 'Objects are equivalent.\n'
            modelList = cls.modelToString(objectsList)
        else:
            preferredObjectNum = objectPref.index(max(objectPref))
            modelList = cls.modelToString(objectsList)
            exemplifyOutputStr += 'Object ' + str((preferredObjectNum+1)) + ' is preferred.\n'

        #exemplify for Qualitative
        qualitativeMatrix = [['inf']*len(cls.preferences.get('Qualitative Choice Logic')),['inf']*len(cls.preferences.get('Qualitative Choice Logic'))]
        clauseNum = 0 #which clause am I on?
        exemplifyOutputStr += 'Qualitative Choice Logic -> '
        for i in range(0,len(objectsList)):
            clauseNum = 0
            for value in cls.preferences.get('Qualitative Choice Logic'):
                qualClause = value[0] #dict
                implies = value[1] #digitized value of implication attribute
                if(implies != None):
                    impliesRegex = str(implies)
                    if(implies > 0):
                        impliesRegex = '[^-]'+str(implies)
                    implicationPass = re.search(impliesRegex,objectsList[i])
                    if(implicationPass == None):
                        clauseNum += 1
                        continue

                for partOfClause,partOfClauseOrder in qualClause.items():
                    claspInput = []
                    claspInput.extend([o for o in objectsList[i].split() if o != '0'])
                    claspInput.extend([re.sub(r"\(|\)","",v).strip() for v in partOfClause.split('&')])
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

        if(qGreaterThan[0] == qGreaterThan[1]):
            exemplifyOutputStr += 'Objects are equivalent.\n'
        else:
            exemplifyOutputStr += 'Object ' + str((qGreaterThan.index(max(qGreaterThan))+1)) + ' is preferred.\n'
        return exemplifyOutputStr

    @classmethod
    def extractObjectsFromClaspOutput(cls,output):
        '''
        Find objects from clasp output
        :returns list of objects
        '''
        regexToExtractObjects = r'-?[0-9] '*(int(len(cls.symbolsList)/2)) + r'0'
        return re.findall(regexToExtractObjects,output)

    @classmethod
    def getNObjectsFromClasp(cls,n):
        '''
        :n - number of objects needed from clasp, n should be 0 to get all objects
        :returns objectsList - n objects in digitized form
        '''
        objectsList = []
        if(cls.checkSatisfyBoolean() == True):
            clauses = []
            for cnfConstraint in cls.hardConstraintsCNF:
                clauses.extend(cnfConstraint.split('&')) #every & is a new line in clasp
            claspInput = 'p cnf '+str(int(len(cls.symbolsList)/2)) + ' ' + str(len(clauses))
            for c in clauses:
                claspInput += '\n'
                claspInput += ' '.join(c.split('|')) + ' 0' #split on ors and add spaces in between
            claspFile = './output.cnf'
            with open(claspFile,'w') as o:
                o.write(claspInput)
            p = Popen(["clasp","./output.cnf","-n",str(n)],stdout=PIPE,stderr=PIPE)
            stdout,stderr = p.communicate()
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

    @classmethod
    def clearAttributes(cls):
        '''
        clear everything that is used in reading in attributes file
        '''
        cls.symbolsList.clear()
        cls.parsedAttributes.clear()
        cls.parsedAttributesReversed.clear()

    @classmethod
    def clearHardConstraints(cls):
        '''
        clear everything used in reading in hard constraints file
        '''
        cls.hardConstraints.clear()
        cls.hardConstraintsCNF.clear()

    @classmethod
    def clearPreferences(cls):
        '''
        clear everything used in reading in Preferences file
        '''
        for key,value in cls.preferences.items():
            cls.preferences[key].clear()

    @classmethod
    def printParsedAttributes(cls):
        '''
        Test to see if parsed attributes are there
        '''
        print('ParsedAttributes dict',cls.parsedAttributes)
        print('symbols',cls.symbolsList)

    @classmethod
    def getAttributeIndex(cls,key):
        '''
        :returns parsedAttributes[key] -> int (value)
        '''
        return cls.parsedAttributes.get(key)

    @classmethod
    def addToHardConstraints(cls,term):
        '''
        Add string to hardConstraints list
        '''
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
            cls.hardConstraintsCNF.append(str(to_cnf(eval(evalStr))))

    @classmethod
    def convertToCNF(cls,clause):
        '''
        Convert data to CNF
        :clause - singular clause that may contain boolean statements with ANDs and ORs and IF
        :return CNF converted string
        '''
        symbolRep = symbols(" ,".join(cls.symbolsList))
        evalStr = ''
        implicationArr = [val.strip() for val in clause.split('IF')]
        if(len(implicationArr) == 2):
            #implication exists
            ifCondition = implicationArr[1] #if p then q
            ifClauseNum = str(cls.getAttributeIndex(ifCondition))
            index = cls.symbolsList.index(ifClauseNum)
            evalStr += 'symbolRep['+str(index)+']' + ' >> '
        thenCondition = implicationArr[0]
        dataArr = thenCondition.split() #split by spaces
        for d in dataArr:
            dNum = str(cls.getAttributeIndex(d))
            if(dNum in cls.symbolsList):
                index = cls.symbolsList.index(dNum)
                evalStr += 'symbolRep['+str(index)+']'
            else:
                evalStr += ' ' +cls.binaryOperators.get(d)+' '
        return str(to_cnf((eval(evalStr))))

    @classmethod
    def checkSatisfyBoolean(cls):
        '''
        clasp format:
        p cnf #of attributes #of clauses
        ...hard constraints
        ...preferences
        ...clauses
        :return True if SATISFIABLE else False
        '''
        cls.convertHardCToCNF()
        clauses = []
        for cnfConstraint in cls.hardConstraintsCNF:
            clauses.extend(cnfConstraint.split('&')) #every & is a new line in clasp

        claspInput = 'p cnf '+str(int(len(cls.symbolsList)/2)) + ' ' + str(len(clauses))
        for c in clauses:
            claspInput += '\n'
            claspInput += ' '.join(c.split('|')) + ' 0' #split on ors and add spaces in between
        claspFile = './output.cnf'
        with open(claspFile,'w') as o:
            o.write(claspInput)
        p = Popen(["clasp","./output.cnf"],stdout=PIPE,stderr=PIPE)
        stdout,stderr = p.communicate()
        satisfy = not 'UNSATISFIABLE' in str(stdout)
        return satisfy

    @classmethod
    def checkSatisfy(cls):
        '''
        :return output string
        '''
        satisfy = cls.checkSatisfyBoolean()
        return 'FEASIBLE OBJECTS EXIST' if satisfy else 'FEASIBLE OBJECTS DO NOT EXIST'


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
        self.clearAttributes()
        lines = fileData.split('\n')#get each line
        parsedAttributeIndex = 1 #will contribute to creating integer version of attributes
        for line in lines:
            lineToSplit = line.replace(',',' ')
            attributes = lineToSplit.split()
            self.addToParsedAttributes(attributes[1],parsedAttributeIndex)
            self.addToParsedAttributes(attributes[2],-1*parsedAttributeIndex)#NOT attributes[1] == attributes[2]
            parsedAttributeIndex += 1

        # self.printParsedAttributes()

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
        self.clearHardConstraints()
        # self.clearHardConstraints()#clear buffers for hard constraints
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
                    constraintList.append(str(negate * self.getAttributeIndex(term)))
                    negate = 1 #reset negate variable to 1 after use
            self.addToHardConstraints(constraintList)
        # self.printHardConstraints()

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
        PenaltyClause,PenaltyNum = [d.strip() for d in data.split(",")]
        PenaltyClauseCNF = self.convertToCNF(PenaltyClause)
        return [PenaltyClauseCNF,int(PenaltyNum)]

    def transformPossibilisticData(self,data):
        '''
        Transforms Possibilistic clause,Preference to (CNF) Possibilistic clause,Preference
        Ex:gun AND cake, 10 -> [[gun,cake],10]
        :returns transformedPossibilisticList
        '''
        possiClause,possiNum = [d.strip() for d in data.split(",")]
        possiClauseCNF = self.convertToCNF(possiClause)
        return [possiClauseCNF,float(possiNum)]

    def transformQualitativeChoiceData(self,data):
        '''
        :returns [{clause CNF form,orderNum},IF]
        '''
        qualClauseStr,qualImplies = [i.strip() for i in data.split('IF')]
        qualClauses = [i.strip() for i in qualClauseStr.split('BT')]
        tempDict = OrderedDict()
        for j in range(0,len(qualClauses)):
            qualCNFStr = self.convertToCNF(qualClauses[j])
            tempDict[qualCNFStr] = (j+1) #order of clause is (j+1)
        return [tempDict,self.getAttributeIndex(qualImplies)]

    def parseFileData(self,fileData):
        '''
        Parse Preferences file
        '''
        self.clearPreferences()#clear buffers for preferences
        lines = fileData.split('\n')
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
                self.addToPreferences('Penalty Logic',transformedPenaltyData)
            elif(possib):
                transformedPossibilisticData = self.transformPossibilisticData(line)
                self.addToPreferences('Possibilistic Logic',transformedPossibilisticData)
            elif(qualit):
                transformedQualitativeData = self.transformQualitativeChoiceData(line)
                self.addToPreferences('Qualitative Choice Logic',transformedQualitativeData)

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
    def __init__(self,dataObject,frame,frame2):
        '''
        Initialize UI object. Window has already been initialized. Canvas becomes a instance of every UI object
        '''
        self.dataObject = dataObject
        self.frame = frame
        self.frame2 = frame2
        self.canvas = None
        self.uniqueTag = self.dataObject.type
        self.createCanvasForInputTab()
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
        self.canvas2.delete(self.uniqueTag)
        output = self.dataObject.checkSatisfy()
        self.canvas2.create_text(10, 10, text=output, anchor='nw', tag=self.uniqueTag)

    def exemplify(self):
        '''
        Call DataObject.exemplify()
        '''
        self.canvas2.delete(self.uniqueTag)
        output = self.dataObject.exemplify()
        self.canvas2.create_text(10, 10, text=output, anchor='nw', tag=self.uniqueTag)

    def optimize(self):
        '''
        Call DataObject.optimize()
        '''
        self.canvas2.delete(self.uniqueTag)
        output = self.dataObject.optimize()
        self.canvas2.create_text(10, 10, text=output, anchor='nw', tag=self.uniqueTag)

    def omnioptimize(self):
        '''
        Call DataObject.optimize()
        '''
        self.canvas2.delete(self.uniqueTag)
        output = self.dataObject.omnioptimize()
        self.canvas2.create_text(10, 10, text=output, anchor='nw', tag=self.uniqueTag)

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
            b4=ttk.Button(self.frame, text="Optimization", command=self.optimize)
            b4.grid(column=8, row=3, pady=5)
            b5=ttk.Button(self.frame, text="Omni-Optimization", command=self.omnioptimize)
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

        outputDict = {'attr':'Penalty Logic', 'hardc':'Possibilistic Logic','pref':'Qualitative Choice Logic'}
        #scrollbar
        h = ttk.Scrollbar(self.frame2, orient=HORIZONTAL)
        v = ttk.Scrollbar(self.frame2, orient=VERTICAL)

        #create canvas
        self.canvas2 = Canvas(self.frame2, width=750, height=300, bg="white", scrollregion=(0, 0, 3000, 3000), yscrollcommand=v.set, xscrollcommand=h.set)
        h['command'] = self.canvas2.xview
        v['command'] = self.canvas2.yview

        self.canvas2.grid(column=columnNum2, row=0,padx=20, sticky=(N,W,E,S))
        h.grid(column=columnNum2, row=1, sticky=(W,E))
        v.grid(column=(columnNum2+1), row=0, sticky=(N,S))

    @classmethod
    def disableButtons(cls):
        '''
        disables buttons in buttonsToDisable list
        '''
        for button in cls.buttonsToDisable:
            button.state(['disabled'])

    @classmethod
    def enableButtons(cls):
        '''
        enables all buttons in buttonsToDisable list
        '''
        for button in cls.buttonsToDisable:
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
        if(self.getType()=='attr'):
                 self.enableButtons()

        file = filedialog.askopenfilename(initialdir = "../assets", title=("Select a file"), filetypes=(("Text file", "*.txt*"),("Any File", "*.*")))
        self.setFileName(file)

        #reset canvas before inserting text
        self.canvas.delete(self.uniqueTag)

        #read from file and set file data
        if(file):
            fileObj = open(file)
            fileData = fileObj.read().strip()
            self.canvas.create_text(10, 10, text=fileData, anchor='nw', tag=self.uniqueTag)
            self.setFileData(fileData)
            self.parseFileData(fileData)
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
attrUI = UI(attrObj,frame1,frame2)

#Create Hard Constraints UI
hardCObj = HardConstraintObject()
hardCUI = UI(hardCObj,frame1,frame2)

#Create Preferences UI
prefObj = PreferencesObject()
prefUI = UI(prefObj, frame1,frame2)

root.mainloop()