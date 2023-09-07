import sys, os, sqlite3
from tkinter import ttk, Tk, Frame, Entry, Listbox, Label, Button, Canvas

sys.path.insert(0, '.local/database/')
import database

# Can't use __file__ because we're freezing this script into an exe.
THISFILE = os.path.abspath(sys.argv[0])

LOCAL_DATABASE_PATH = '.local/database/springerbk.sqlite'

DEFAULT_FONT = ('sans', 24, 'bold')
DEFAULT_STATUS_FONT = ('sans', 16, '')
DEFAULT_MENU_FONT = ('sans', 12, 'bold')
DEFAULT_GRID_FONT = ('mono', 20, '')

def tabBarGetCurrentTabText():
	tab = tabBar.tab('current')
	return tab['text']

def tabBarGetCurrentTabIndex():
	return tabBar.index("current")

def cb_root_Escape(e):
	if tabBarGetCurrentTabText() == 'Players':
		return
	root.quit()

def cb_root_NextTab(e):
	currentTab = tabBar.index("current")
	currentTab = (currentTab + 1) % len(tabBar.tabs())
	tabBar.select(currentTab)

def cb_root_PrevTab(e):
	currentTab = tabBar.index("current")
	currentTab = (currentTab - 1) % len(tabBar.tabs())
	tabBar.select(currentTab)

root = Tk()
root.title(THISFILE)
root.geometry('1200x800')
root.bind('<Escape>', cb_root_Escape)

s = ttk.Style()
s.theme_create("Style1", parent="alt", settings={
	"TNotebook": {"configure": {"tabmargins": [2, 5, 2, 0] } },
	"TNotebook.Tab": {"configure": {"padding": [100, 10],
	"font" : DEFAULT_MENU_FONT},}
})
s.theme_use("Style1")


# n = ttk.Notebook(root, style = 'TNotebook')
tabBar = ttk.Notebook(root, takefocus = 0)

def cb_n_TabChanged(_):
	# print(tabBar.index("current"))
	currentTab = tabBar.index("current")
	# print(e.widget, currentTab)
	if currentTab == 2:
		playerAdderFrame.edit.focus_set()

root.bind("<Control-Next>", cb_root_NextTab)
root.bind("<Control-Prior>", cb_root_PrevTab)
tabBar.bind(" <<NotebookTabChanged>>", cb_n_TabChanged)

f1 = Frame(tabBar)
f1.pack(side = 'top', fill = 'x')

padding = 8

class CrossTable(Frame):
	def __init__(self, parent):
		Frame.__init__(self, parent)
		self.pack()

		self.data = [
			['#' , 'Name',		'1', '2', '3', '4', '5', '6', '7', '8', '9', '10', '11', '12', 'Punkte', 'Platz'],
			['1' , 'Aronian',	 '',  '',  '',  '',  '',  '',  '',  '',  '',   '',   '',   '',      '0',     '1'],
			['2' , 'Botvinnik',	 '',  '',  '',  '',  '',  '',  '',  '',  '',   '',   '',   '',      '0',     '1'],
			['3' , 'Carlsen',	 '',  '',  '',  '',  '',  '',  '',  '',  '',   '',   '',   '',      '0',     '1'],
			['4' , 'Ding',		 '',  '',  '',  '',  '',  '',  '',  '',  '',   '',   '',   '',      '0',     '1'],
			['5' , 'Euwe',		 '',  '',  '',  '',  '',  '',  '',  '',  '',   '',   '',   '',      '0',     '1'],
			['6' , 'Fischer',	 '',  '',  '',  '',  '',  '',  '',  '',  '',   '',   '',   '',      '0',     '1'],
			['7' , 'Gligorić',	 '',  '',  '',  '',  '',  '',  '',  '',  '',   '',   '',   '',      '0',     '1'],
			['8' , 'Hou',		 '',  '',  '',  '',  '',  '',  '',  '',  '',   '',   '',   '',      '0',     '1'],
			['9' , 'Ivanchuk',	 '',  '',  '',  '',  '',  '',  '',  '',  '',   '',   '',   '',      '0',     '1'],
			['10', 'Jobava',	 '',  '',  '',  '',  '',  '',  '',  '',  '',   '',   '',   '',      '0',     '1'],
			['11', 'Kramnik',	 '',  '',  '',  '',  '',  '',  '',  '',  '',   '',   '',   '',      '0',     '1'],
			['12', 'Larsen',	 '',  '',  '',  '',  '',  '',  '',  '',  '',   '',   '',   '',      '0',     '1'],
		]

		height = len(self.data)
		width = len(self.data[0])

		self.table = Frame(self)
		self.table.pack(anchor = 'w', padx = padding, pady = padding)

		for i in range(height): #Rows
			for j in range(width): #Columns
				cursor = 'X_cursor' if i == j - 1 else 'hand2'
				text = 'x' if i == j - 1 else self.data[i][j]
				b = Label(self.table, text = text,
					font = DEFAULT_GRID_FONT,
					relief = "sunken", cursor = cursor, anchor = "center",
					padx = padding, pady = padding,
					background = 'white', borderwidth = 3)
				b.grid(row=i, column=j, sticky = 'n e w s')

		self.table.rowconfigure('all', minsize = 50)
		self.table.columnconfigure('all', minsize = 50)

f2 = Frame(tabBar)
f2.pack(side = 'top', fill = 'x')

canvas = Canvas(f2, width = 1200, height = 800)
canvas.grid(column=0, row=0, sticky='n e w s')
canvas.create_line((0, 0, 1000, 1000))

class PlayerList(Listbox):
	def __init__(self, parent):
		Listbox.__init__(self, parent)


class SuggestionPopup:

	def __init__(self, parent, sibling):
		self.parent = parent
		self.sibling = sibling
		self.listFrame = None
		self.list = None

	def onListReturn(self, e):
		self.parent.commmitSuggestion()
		self.sibling.focus_set()

	def onListEscape(self, e):
		self.hide()
		self.sibling.focus_set()

	def show(self, names = []):
		if self.list or self.listFrame:
			self.hide()

		self.listFrame = Frame(self.parent, relief = "solid",
			bg = "white", takefocus = 0, bd = 1)
		self.listFrame.place(in_ = self.sibling,
			x=0, y=(self.sibling.winfo_height() + 4),
			anchor="nw", bordermode="outside")

		self.list = Listbox(self.listFrame, font = DEFAULT_FONT,
			selectmode = "single", bg = "white", takefocus = 0,
			relief = "flat")
		self.list.pack(anchor = 'center', padx = padding, pady = padding)

		for name in names:
			self.list.insert('end', name['name'])

		self.list.bind('<Return>', self.onListReturn)
		self.list.bind('<Escape>', self.onListEscape)
		# self.list.bind('<<ListboxSelect>>', self.onListSelect)

	def hide(self):
		if self.list:
			self.list.destroy()
			self.list = None
		if self.listFrame:
			self.listFrame.destroy()
			self.listFrame = None

	def shown(self):
		return self.list

	def count(self):
		return self.list.size()

	def selection(self):
		sel = self.list.curselection()
		if sel: return sel[0]

	def select(self, index):
		self.list.selection_set(index)

	def deselect(self):
		self.list.selection_clear(0, 'end')

	def get(self, index):
		return self.list.get(index)

class StatusBar(Frame):
	def __init__(self, parent):
		Frame.__init__(self, parent)
		self.pack(side = 'bottom', fill = 'x')

		self.main = Label(self, font = DEFAULT_STATUS_FONT)
		self.main.pack(side = 'left', padx = padding)

	def setMainText(self, text):
		self.main['text'] = text


class PlayerAdderFrame(Frame):
	def __init__(self, parent):
		Frame.__init__(self, parent)
		# self.pack(side = 'top', fill = 'both', expand = 1)
		self.pack()

		# self.button = Button(self, text = 'add', takefocus = False, font = DEFAULT_FONT)
		# self.button.pack(anchor = 'n', side = 'right')

		self.edit = Entry(self, font = DEFAULT_FONT, bg = 'white')
		# se.bind('<Return>', cb_se_Return)
		self.edit.pack(side = 'top', fill = 'x', padx = padding, pady = padding)

		self.list = PlayerList(self)

		self.status = StatusBar(self)

		self.popup = SuggestionPopup(self, self.edit)

		self.edit.bind("<Return>", lambda e: self.commmitSuggestion())
		self.edit.bind("<Escape>", self.onEditEscape)
		self.edit.bind("<Tab>", self.onEditTab)
		self.edit.bind("<Up>", lambda e: self.selectPrev())
		self.edit.bind("<Down>", lambda e: self.selectNext())
		# self.edit.bind("<KeyPress>", self.onKeyPress)

		self.writeDatabasePlayerCountToStatusBar()

	def writeDatabasePlayerCountToStatusBar(self):
		playerCount = 0
		with database.connect(LOCAL_DATABASE_PATH) as db:
			db.row_factory = None
			r = db.execute('SELECT count(*) FROM names')
			playerCount = r.fetchone()[0]
		self.status.setMainText(f'There are {playerCount} players in the database.')

	def onEditEscape(self, e):
		if self.getEditText():
			self.clearEdit()
		elif self.popup.shown():
			self.popup.hide()
		else:
			root.quit()

	def commmitSuggestion(self):
		if self.popup.shown():
			sel = self.popup.selection()
			if sel is not None:
				name = self.popup.get(sel)
				self.popup.hide()
				if name:
					self.setEditText(name)
					return

	def onEditTab(self, e):
		self.popup.hide()
		text = self.edit.get()
		self.edit.delete(0, "end")
		# print(text)
		with database.connect(LOCAL_DATABASE_PATH) as db:
			names = database.findName(db, text)
		if names:
			if len(names) == 1:
				self.setEditText(names[0]['name'])
			else:
				self.popup.show(names)
		self.edit.focus_set()

	def getEditText(self):
		return self.edit.get()

	def setEditText(self, text):
		self.edit.delete(0, 'end')
		self.edit.insert(0, text)

	def clearEdit(self):
		self.edit.delete(0, 'end')

	def selectPrev(self):
		if not self.popup.shown(): return
		sel = self.popup.selection()
		self.popup.deselect()
		count = self.popup.count()
		if sel is None: sel = count
		sel = (sel - 1) % count
		self.popup.select(sel)

	def selectNext(self):
		if not self.popup.shown(): return
		sel = self.popup.selection()
		self.popup.deselect()
		count = self.popup.count()
		if sel is None: sel = -1
		sel = (sel + 1) % count
		self.popup.select(sel)

# def popup_bonus(parent):
# 	import tkinter
# 	win = tkinter.Toplevel()
# 	win.transient(parent)
# 	win.attributes("-topmost", True)
# 	win.wm_title("Window")

# 	l = tk.Label(win, text="Input")
# 	l.grid(row=0, column=0)

# 	b = ttk.Button(win, text="Okay", command=win.destroy)
# 	b.grid(row=1, column=0)

playerAdderFrame = PlayerAdderFrame(root)
crossTable = CrossTable(root)

tabBar.add(playerAdderFrame, text = 'Players')
tabBar.add(crossTable, text = 'Table')
tabBar.add(f2, text = 'Graphs')
tabBar.pack(side = 'top', fill = 'both', expand = 1)

playerAdderFrame.edit.focus_set()

# import tkinter.font
# print(tkinter.font.families(root))

root.mainloop()
