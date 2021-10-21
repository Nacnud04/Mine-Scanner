# Importing tkinter module 
from tkinter import *
from tkinter.ttk import *
  
# creating Tk window 
master = Tk() 
  
# cretaing a Fra, e which can expand according 
# to the size of the window 
pane = Frame(master) 
pane.pack(fill = BOTH, expand = True) 
  
# button widgets which can also expand and fill 
# in the parent widget entirely 
b1 = Button(pane, text = "Click me !") 
b1.pack(fill = BOTH, expand = True) 
  
b2 = Button(pane, text = "Click me too") 
b2.pack(fill = BOTH, expand = True) 
  
mainloop()