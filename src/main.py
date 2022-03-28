from tkinter import *
from tkinter import ttk
from tkinter import filedialog
from tkinter import Canvas
from tkinter import Scrollbar
from turtle import bgcolor
from sympy import to_cnf,symbols
import re


class DataObject:
    '''
    Object to represent attributes, hard constraints, and preferences at a high level
    '''
    parsedAttributes = dict() #dictionary of binary attributes(keys) and their integer representations(values)
    binaryOperators = dict({'NOT':'~','OR':'|','AND':'&'})
    hardConstraints = [] #list of constraints
    preferences = dict() #dict of preferences[key is preference name(Qualitative logic,Penality,Possibilistic)]: value is array of strings for each preference
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
        return self.fileName

    @classmethod
    def addToParsedAttributes(cls,attribute, index):
        '''
        Add to parsed attributes dictionary and symbols list
        '''
        if(str(index) not in cls.symbolsList):
            cls.symbolsList.append(str(index))
        cls.parsedAttributes[attribute] = index

    @classmethod
    def printParsedAttributes(cls):
        '''
        Test to see if parsed attributes are there
        '''
        print(cls.parsedAttributes)
        print('symbols',cls.symbolsList)

    @classmethod
    def getAttribute(cls,key):
        '''
        :returns parsedAttributes[key] -> int (value)
        '''
        return cls.parsedAttributes[key]

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
    def generateFeasibleObjects(cls):
        '''
        Decide whether there are feasible objects w.r.t hard constraints
        '''
        # print(cls.hardConstraints)
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
            print('evalStr:\t',evalStr)
            print('to_cnf(evalStr):\t',to_cnf(eval(evalStr)))


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

    def parseFileData(self,fileData):
        '''
        Parse Preferences file
        '''
        lines = fileData.split('\n')
        #print(lines)
        for line in lines:
            if(line != ''):
                print(line)

class UI:
    '''
    Creates a Canvas and everything that goes with it
    '''

    #static class variable
    global columnNum, buttonText
    columnNum = 0
    buttonText = {'attr':"Attributes", 'hardc':"Hard Constraints", 'pref':"Preferences"}

    def __init__(self,dataObject,frame):
        '''
        Initialize UI object. Window has already been initialized. Canvas becomes a instance of every UI object
        '''
        self.dataObject = dataObject
        self.frame = frame
        self.canvas = None
        self.uniqueTag = self.dataObject.type
        self.createCanvas()

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

    def generateFeasibleObjects(self):
        '''
        Call DataObject.generateFeasibleObjects()
        '''
        self.dataObject.generateFeasibleObjects()

    def createCanvas(self):
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
        ttk.Button(self.frame, text="Insert a file", command=self.selectFile).grid(column=columnNum, row=3)
        if(self.getType() == 'attr'):
            ttk.Button(self.frame, text="Generate Feasible Objects", command=self.generateFeasibleObjects).grid(column=8, row=1,pady=5)
            ttk.Button(self.frame, text="Exemplification", command=self.generateFeasibleObjects).grid(column=8, row=2, pady=5)
            ttk.Button(self.frame, text="Optimization", command=self.generateFeasibleObjects).grid(column=8, row=3, pady=5)
            ttk.Button(self.frame, text="Omni-Optimization", command=self.generateFeasibleObjects).grid(column=8, row=4, pady=5)
        columnNum +=2 #for tab1 placement

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
            fileObj = open(file)
            fileData = fileObj.read()
            self.canvas.create_text(10, 10, text=fileData, anchor='nw', tag=self.uniqueTag)
            self.setFileData(fileData)
            self.parseFileData(fileData)
            #self.printFileData()
            fileObj.close()


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

root.mainloop()