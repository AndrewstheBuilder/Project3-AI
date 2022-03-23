from tkinter import *
from tkinter import ttk
from tkinter import filedialog

def selectFile(label):
    '''
    '''
    file = filedialog.askopenfilename(initialdir = "/", title=("Select a file"), filetypes=(("Text file", "*.txt*"),("Any File", "*.*")))
    if(file):
        label.configure(text=file)
        #print(type(label.configure()['text'][-1]))
        print(label.configure()['text'][-1])
    else:
        label.configure(text=" [File name here] ")

#Create a GUI
root = Tk()
root.title('Project 3 - AI')
root.geometry("650x250")

#create a notebook for tabs
notebook = ttk.Notebook(root)
notebook.pack(pady=10, expand=True)

#create frames
frame1 = ttk.Frame(notebook, width=650, height=230)
frame2 = ttk.Frame(notebook, width=650, height=230)
frame1.grid()
frame2.grid()

#add frames to notebook
notebook.add(frame1, text="Input")
notebook.add(frame2, text="Output")

# frm = ttk.Frame(root, padding=10)
# frm.grid()

#Attribute File
ttk.Label(frame1, text="Enter a file for Attributes:").grid(column=0, row=0)
attrLabel = ttk.Label(frame1,text=" [File name here] ",background="white")
attrLabel.grid(column=1, row=0)
ttk.Button(frame1, text="Open a file", command=lambda: selectFile(attrLabel)).grid(column=2, row=0)

#Hard Constraints File
ttk.Label(frame1, text="Enter a file for Hard Constraints:").grid(column=0, row=1)
hardCLabel = ttk.Label(frame1,text=" [File name here] ",background="white")
hardCLabel.grid(column=1, row=1)
ttk.Button(frame1, text="Open a file", command=lambda: selectFile(hardCLabel)).grid(column=2, row=1)

#Preferences File
ttk.Label(frame1, text="Enter a file for Preference:").grid(column=0, row=2)
prefLabel = ttk.Label(frame1,text=" [File name here] ",background="white")
prefLabel.grid(column=1, row=2)
ttk.Button(frame1, text="Open a file", command=lambda: selectFile(prefLabel)).grid(column=2, row=2)

root.mainloop()