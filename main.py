from tkinter import *
from tkinter import ttk
from tkinter import filedialog

def selectFile():
    '''
    '''
    file = filedialog.askopenfilename(initialdir = "/", title=("Select a file"), filetypes=(("Text file", "*.txt*"),("Any File", "*.*")))

def createGui():
    '''
    '''
    gui = Tk()
    gui.title('Select files for Project 3')
    gui.geometry("450x250")
    frm = ttk.Frame(gui, padding=10)
    frm.grid()
    ttk.Label(frm, text="Enter a file for Attributes:").grid(column=0, row=0)
    #global attrLabel
    attrLabel = ttk.Label(frm,text="")
    attrLabel.grid(column=1, row=0)
    ttk.Button(frm, text="Browse", command=selectFile).grid(column=1, row=0)
    gui.mainloop()

def main():
    createGui()


if __name__ == '__main__':
    main()