from tkinter import *
from tkinter import ttk
from tkinter import filedialog
from tkinter import Canvas
from tkinter import Scrollbar



class DataObject:
    '''
    Object to represent attributes, hard constraints, and preferences at a high level
    '''
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

#Below three classes inherit from DataObject class
class AttributeObject(DataObject):
    def __init__(self, attrFileData=None):
        self.setFileData(attrFileData)
        self.type = 'attr'

class HardConstraintObject(DataObject):
    def __init__(self, hardCFileData=None):
        self.setFileData(hardCFileData)
        self.type = 'hardc'

class PreferencesObject(DataObject):
    def __init__(self, prefFileData=None):
        self.setFileData(prefFileData)
        self.type = 'pref'

class UI:

    #static class variable
    global columnNum, buttonText
    columnNum = 0
    buttonText = {'attr':"Attributes", 'hardc':"Hard Constraints", 'pref':"Preferences"}

    def __init__(self,dataObject,frame):
        self.dataObject = dataObject
        self.frame = frame
        self.canvas = None
        self.uniqueTag = self.dataObject.type
        self.createCanvas()

    def setFileData(self, fileData):
        self.dataObject.setFileData(fileData)

    def getFileData(self):
        return self.dataObject.getFileData()

    def setFileName(self, fileName):
        self.dataObject.setFileName(fileName)

    def getFileName(self):
        return self.dataObject.getFileName()

    def createCanvas(self):
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
        ttk.Label(self.frame, text=buttonText[self.dataObject.type],borderwidth=3, relief="raised").grid(column=columnNum, row=2)
        ttk.Button(self.frame, text="Insert a file", command=self.selectFile).grid(column=columnNum, row=3)
        columnNum +=2 #for tab1 placement

    def printFileData(self):
        print("File name:",self.getFileName())
        print("File data:\n",self.getFileData())

    def selectFile(self):
        '''
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
            self.printFileData()
            fileObj.close()


#Create a GUI
root = Tk()
root.title('Project 3 - AI')
root.geometry("950x500")

#create a notebook for tabs
notebook = ttk.Notebook(root)
notebook.pack(pady=10, expand=True)

#create frames
frame1 = ttk.Frame(notebook, width=950, height=500)
frame2 = ttk.Frame(notebook, width=950, height=500)
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