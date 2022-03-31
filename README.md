Name: 202210.CAP4630.10979 Project 3

Contributors:
Andrews Peter
Emanuel Tesfa
Jonathan Shih

Description: 
Knowledge-based intelligent system that collects user preferences as input and utilizes penalty, possibilistic, and qualititative choice logical reasoning to output feasible models, exemplification models, as well as optimized and omni-optimized models. The program utilizes a GUI designed with the Python Tkinter package that allows the user to input attributes, hard constraints, and preferences as individual plain text files, of which the contents can be viewed in the "Input" tab, and with results of reasoning tasks that can be viewed in the "Output" tab. Sympy package is used to convert the logical statements from user input into CNF form, which generates an "output.cnf" file in the /src folder. The output.cnf file is parsed by CLASP, a SAT solver that resolves CNF propositional formulas, returns feasible models, and determines whether models are unfeasible. These calculations are used to support user-selected reasoning function buttons on the UI, including:

Check if Feasibile Objects - determine whether feasible models exist given hard constraints
Exemplification - generates two possible models and detemines which is preferable
Optimization - returns an optimal model
Omni-optimization - returns all optimal models

Programming Language: Python 3.9

Packages/Plugins: 
conda 4.9.2 - for package management
tkinter - for GUI development
sympy - for CNF conversions
potassco clingo 5.5.1 - for CLASP integration

Usage:
Execute program from command line using "./python main.py"
User clicks "Insert a File" under the "Attributes" section to open a file explorer window to select a file to upload.
Select "Attributes.txt" and click "Open" to upload file containing 8 attributes for the first test case.
This action unlocks the next "Insert a File" button for the "Hard Constraints" section.
User clicks "Insert a File" under the "Hard Constraints" section to open a file explorer window to select a file to upload.
Select "Hard Constraints.txt" and click "Open" to upload file containing 6 constraints for the first test case. 
This action unlocks the next "Insert a File" button for the "Preferences" section.
User clicks "Insert a File" under the "Preferences" section to open a file explorer window to select a file to upload.
Select "Hard Constraints.txt" and click "Open" to upload file containing 6 preferences for the first test case.
User may select "Check if Feasibile Objects", "Exemplification", "Optimzation", or "Omni-optimzation" to perform reasoning tasks.
Outcomes from reasoning tasks can be viewed in the "Output" tab in the main window.
Reasoning tasks may be run repeatedly until program is terminated.
Program may be terminated by closing the window or by pressing Ctrl-C.

