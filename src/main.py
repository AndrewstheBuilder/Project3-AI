from tkinter import *
from tkinter import ttk
from tkinter import filedialog
from tkinter import Canvas
from tkinter import Scrollbar

global attrObj, hardCObj,prefObj

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

def selectFile(canvas,uniqueId):
    '''
    '''
    file = filedialog.askopenfilename(initialdir = "../assets", title=("Select a file"), filetypes=(("Text file", "*.txt*"),("Any File", "*.*")))
    #print(open(file).read())
    #setattr(dataObj, "fileData", open(file).read())
    #print(label.configure()['text'][-1])

    #reset canvas before inserting text
    canvas.delete(uniqueId)

    if(file):
        fileObj = open(file)
        canvas.create_text(10, 10, text=fileObj.read(), anchor='nw', tag=uniqueId)
        #label.configure(text=fileObj.read())
        #txt.insert(INSERT, 'TEST')
        #canvas.create_text(0,0,text=fileObj.read())
        #canvas.configure(text=fileObj.read())
        fileObj.close()

# def printFileData():
#     print('Attributes\n', attrObj.fileData)
#     print('Hard Constraints\n', attrObj.fileData)
#     print("Preferences\n", prefObj.fileData)

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

#Attribute File

#scrollbar
h = ttk.Scrollbar(frame1, orient=HORIZONTAL)
v = ttk.Scrollbar(frame1, orient=VERTICAL)

attrCanvas = Canvas(frame1, width=250, height=300, bg="white", scrollregion=(0, 0, 1000, 1000), yscrollcommand=v.set, xscrollcommand=h.set)

h['command'] = attrCanvas.xview
v['command'] = attrCanvas.yview

attrCanvas.grid(column=0, row=0,padx=20, sticky=(N,W,E,S))
h.grid(column=0, row=1, sticky=(W,E))
v.grid(column=1, row=0, sticky=(N,S))
attrCanvasTag = "attrTag"#unique id for attrCanvas

ttk.Label(frame1, text="Attributes",borderwidth=3, relief="raised").grid(column=0, row=2)
ttk.Button(frame1, text="Insert a file", command=lambda: selectFile(attrCanvas,attrCanvasTag)).grid(column=0, row=3)

#Hard Constraints File

#scroll
h1 = ttk.Scrollbar(frame1, orient=HORIZONTAL)
v1 = ttk.Scrollbar(frame1, orient=VERTICAL)

hardCCanvas = Canvas(frame1, width=250, height=300, bg="white", scrollregion=(0, 0, 1000, 1000), yscrollcommand=v1.set, xscrollcommand=h1.set)

h1['command'] = hardCCanvas.xview
v1['command'] = hardCCanvas.yview

hardCCanvas.grid(column=2, row=0,padx=20, sticky=(N,W,E,S))
h1.grid(column=2, row=1, sticky=(W,E))
v1.grid(column=3, row=0, sticky=(N,S))
hardCCanvasTag = "hardCTag"#unique id for attrCanvas

ttk.Label(frame1, text="Hard Constraints",borderwidth=3, relief="raised").grid(column=2, row=2)
ttk.Button(frame1, text="Insert a file", command=lambda: selectFile(hardCCanvas,hardCCanvasTag)).grid(column=2, row=3)

#Preferences File

#scroll
h2 = ttk.Scrollbar(frame1, orient=HORIZONTAL)
v2 = ttk.Scrollbar(frame1, orient=VERTICAL)

prefCanvas = Canvas(frame1, width=250, height=300, bg="white", scrollregion=(0, 0, 1000, 1000), yscrollcommand=v2.set, xscrollcommand=h2.set)

h2['command'] = prefCanvas.xview
v2['command'] = prefCanvas.yview

prefCanvas.grid(column=4, row=0,padx=20, sticky=(N,W,E,S))
h2.grid(column=4, row=1, sticky=(W,E))
v2.grid(column=5, row=0, sticky=(N,S))
prefCanvasTag = "prefTag"#unique id for attrCanvas

ttk.Label(frame1, text="Preferences",borderwidth=3, relief="raised").grid(column=4, row=2)
ttk.Button(frame1, text="Insert a file", command=lambda: selectFile(prefCanvas,prefCanvasTag)).grid(column=4, row=3)



# attrObj = DataObject()

# #Hard Constraints File
# ttk.Label(frame1, text="Hard Constraints").grid(column=1, row=0)
# hardCObj = DataObject()
# ttk.Button(frame1, text="Insert a file", command=lambda: selectFile(hardCObj)).grid(column=1, row=1)


# #Preferences File
# ttk.Label(frame1, text="Preferences").grid(column=2, row=0)
# prefObj = DataObject()
# ttk.Button(frame1, text="Insert a file", command=lambda: selectFile(prefObj)).grid(column=2, row=1)
# #printFileData()


root.mainloop()