import tkinter as tk
from tkinter import simpledialog
from tkinter import messagebox

def tk_askstring(content, defaultvalue='', windowtitle='Question'):
	'''
	simpledialog.askstring helper\n
	\n
	This function asks the user to write down a string.\n
	Returns None if the user clicked on Cancel, the stripped string otherwise
	'''
	application_window = tk.Tk()
	application_window.eval('tk::PlaceWindow . center')
	application_window.withdraw()
	ret = simpledialog.askstring(windowtitle, content, parent=application_window, initialvalue=defaultvalue)
	application_window.destroy()
	if(ret != None):
		ret = ret.lstrip().rstrip()
	
	return ret

def tk_message(content, title="Information"):
	application_window = tk.Tk()
	application_window.eval('tk::PlaceWindow . center')
	application_window.withdraw()
	messagebox.showinfo(title, content)
	application_window.destroy()
