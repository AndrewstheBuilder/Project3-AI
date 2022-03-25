from tkinter import *
from tkinter import ttk
from tkinter import filedialog
from tkinter import Canvas
from tkinter import Scrollbar



class DataObject:
    '''
    Object to represent attributes, hard constraints, and preferences
    '''
    def __init__(self):
        self.fileData = None

    def setFileData(self, data):
        self.fileData = data

    def getFileData(self):
        return self.fileData

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

maxValue = 0
#attrFileLabel = None
attr_var = None

# def selectFile(canvas,uniqueId,dataObj=None,attrFileLabel=None):
#     '''
#     '''
#     #global file, maxValue
#     file = filedialog.askopenfilename(initialdir = "../assets", title=("Select a file"), filetypes=(("Text file", "*.txt*"),("Any File", "*.*")))

#     # if(attrFileLabel):
#     #     print("YESSSS")
#     #     attrFileLabel.configure(text=file)
#     #     print(attrFileLabel.configure()['text'])
#     #     print('file variable', type(file))
#     #     #maxValue += 1

#     #reset canvas before inserting text
#     canvas.delete(uniqueId)

#     if(file):
#         fileObj = open(file)
#         canvas.create_text(10, 10, text=fileObj.read(), anchor='nw', tag=uniqueId)
#         fileObj.close()
class UI:

    #static class variable
    global columnNum, buttonText
    columnNum = 0
    buttonText = {'attr':"Attribute", 'hardc':"Hard Constraints", 'pref':"Preferences"}

    def __init__(self,dataObject,frame):
        self.dataObject = dataObject
        self.frame = frame
        self.canvas = None
        self.uniqueTag = self.dataObject.type
        self.fileName = None

        self.createCanvas()

    def setFileData(self, fileData):
        self.dataObject.setFileData(fileData)

    def getFileData(self):
        return self.dataObject.getFileData()

    def setFileName(self, fileName):
        self.fileName = fileName

    def getFileName(self):
        return self.fileName

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

    def selectFile(self):
        '''
        '''
        #global file, maxValue
        file = filedialog.askopenfilename(initialdir = "../assets", title=("Select a file"), filetypes=(("Text file", "*.txt*"),("Any File", "*.*")))
        self.setFileName(file)
        # if(attrFileLabel):
        #     print("YESSSS")
        #     attrFileLabel.configure(text=file)
        #     print(attrFileLabel.configure()['text'])
        #     print('file variable', type(file))
        #     #maxValue += 1

        #reset canvas before inserting text
        self.canvas.delete(self.uniqueTag)

        if(file):
            fileObj = open(file)
            self.canvas.create_text(10, 10, text=fileObj.read(), anchor='nw', tag=self.uniqueTag)
            self.dataObject.setFileData(fileObj.read())
            print('Inside func', self.getFileName())
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

#universal file content

#Create Attribute UI
attrObj = AttributeObject()
attrUI = UI(attrObj,frame1)
print('UI filename', attrUI.getFileData())

#Create Hard Constraints UI
hardCObj = HardConstraintObject()
hardCUI = UI(hardCObj,frame1)

#Create Preferences UI
prefObj = PreferencesObject()
prefUI = UI(prefObk, frame1)

# #Attribute File

# #scrollbar
# h = ttk.Scrollbar(frame1, orient=HORIZONTAL)
# v = ttk.Scrollbar(frame1, orient=VERTICAL)

# #create canvas to show attributes in tab 1.
# attrCanvas = Canvas(frame1, width=250, height=300, bg="white", scrollregion=(0, 0, 1000, 1000), yscrollcommand=v.set, xscrollcommand=h.set)

# h['command'] = attrCanvas.xview
# v['command'] = attrCanvas.yview

# #set horizontal and vertical scrollbar

# attrCanvas.grid(column=0, row=0,padx=20, sticky=(N,W,E,S))
# h.grid(column=0, row=1, sticky=(W,E))
# v.grid(column=1, row=0, sticky=(N,S))
# attrCanvasTag = "attrTag"#unique id for attrCanvas.create_text()
# attrObj = AttributeObject()

# attrUI = UI(attrCanvas, attrObj, attrCanvasTag)

# attr_var = StringVar()
# def printStuff(fileName,index,mode):
#     print('File Name',attr_var.get())
#     # print('o', o)
#     # print('l', l)
# attr_var.trace_add('write',printStuff)

# attrFileLabel = Label(textvariable=attr_var)

# #button to insert attributes
# ttk.Label(frame1, text="Attributes",borderwidth=3, relief="raised").grid(column=0, row=2)
# ttk.Button(frame1, text="Insert a file", command=attrUI.selectFile()).grid(column=0, row=3)

# print('outside func', attrUI.dataObject)

#print(attrFileLabel.configure(text=str(maxValue)))
#print(attrFileLabel.configure()['text'])
#print('maxValue', maxValue)

# attrFileName.trace("w", printStuff)

# #Hard Constraints File

# #scrollbar
# h1 = ttk.Scrollbar(frame1, orient=HORIZONTAL)
# v1 = ttk.Scrollbar(frame1, orient=VERTICAL)

# #create canvas to show hard constraints in tab 1.
# hardCCanvas = Canvas(frame1, width=250, height=300, bg="white", scrollregion=(0, 0, 1000, 1000), yscrollcommand=v1.set, xscrollcommand=h1.set)

# h1['command'] = hardCCanvas.xview
# v1['command'] = hardCCanvas.yview

# #set horizontal and vertical scrollbar
# hardCCanvas.grid(column=2, row=0,padx=20, sticky=(N,W,E,S))
# h1.grid(column=2, row=1, sticky=(W,E))
# v1.grid(column=3, row=0, sticky=(N,S))
# hardCCanvasTag = "hardCTag"#unique id for hardCCanvas.create_tag()

# #button to insert hard constraints
# ttk.Label(frame1, text="Hard Constraints",borderwidth=3, relief="raised").grid(column=2, row=2)
# ttk.Button(frame1, text="Insert a file", command=lambda: selectFile(hardCCanvas,hardCCanvasTag)).grid(column=2, row=3)

# #Preferences File

# #scrollbar
# h2 = ttk.Scrollbar(frame1, orient=HORIZONTAL)
# v2 = ttk.Scrollbar(frame1, orient=VERTICAL)

# #create canvas to show preferences in tab1
# prefCanvas = Canvas(frame1, width=250, height=300, bg="white", scrollregion=(0, 0, 1000, 1000), yscrollcommand=v2.set, xscrollcommand=h2.set)

# h2['command'] = prefCanvas.xview
# v2['command'] = prefCanvas.yview

# #set horizontal and vertical scrollbar
# prefCanvas.grid(column=4, row=0,padx=20, sticky=(N,W,E,S))
# h2.grid(column=4, row=1, sticky=(W,E))
# v2.grid(column=5, row=0, sticky=(N,S))
# prefCanvasTag = "prefTag"#unique id for prefCanvas.create_tag()

# #button to insert preferences
# ttk.Label(frame1, text="Preferences",borderwidth=3, relief="raised").grid(column=4, row=2)
# ttk.Button(frame1, text="Insert a file", command=lambda: selectFile(prefCanvas,prefCanvasTag)).grid(column=4, row=3)

#Objects to work on for converting to CNF and to digit form before feeding to CLASP
# attr = AttributeObject()
# hardC = HardConstraintObject()
# pref = PreferencesObject()
# print(attrFileName.get())
root.mainloop()