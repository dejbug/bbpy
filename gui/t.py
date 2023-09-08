import sys, os, sqlite3
from tkinter import ttk, Tk, Frame, Entry, Listbox, Label, Button, Canvas

# FIXME: This needs to work from wherever we execute this script.
sys.path.insert(0, ('.'))
import database

# Can't use __file__ because we're freezing this script into an exe.
THISFILE = os.path.abspath(sys.argv[0])

LOCAL_DATABASE_PATH = 'springerbk.sqlite'

DEFAULT_FONT = ('sans', 24, 'bold')
DEFAULT_STATUS_FONT = ('sans', 16, '')
DEFAULT_MENU_FONT = ('sans', 12, 'bold')
DEFAULT_GRID_FONT = ('mono', 20, '')

PADDING = 8

class TabBar(ttk.Notebook):
	def __init__(self, parent):
		ttk.Notebook.__init__(self, parent, takefocus = 0)
		parent.bind("<Control-Next>", lambda e: self.nextTab())
		parent.bind("<Control-Prior>", lambda e: self.prevTab())
		self.bind("<<NotebookTabChanged>>", self.onActiveTabChanged)
		self.autoFocusItems = []

	def getCurrentTabText(self):
		tab = self.tab('current')
		return tab['text']

	def getCurrentTabIndex(self):
		return self.index("current")

	def nextTab(self):
		currentTab = self.index("current")
		currentTab = (currentTab + 1) % len(self.tabs())
		self.select(currentTab)

	def prevTab(self):
		currentTab = self.index("current")
		currentTab = (currentTab - 1) % len(self.tabs())
		self.select(currentTab)

	def onActiveTabChanged(self, e):
		currentText = self.getCurrentTabText()
		for text, item in self.autoFocusItems:
			if currentText == text:
				item.focus_set()

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
		self.table.pack(anchor = 'w', padx = PADDING, pady = PADDING)

		for i in range(height): #Rows
			for j in range(width): #Columns
				cursor = 'X_cursor' if i == j - 1 else 'hand2'
				text = 'x' if i == j - 1 else self.data[i][j]
				b = Label(self.table, text = text,
					font = DEFAULT_GRID_FONT,
					relief = "sunken", cursor = cursor, anchor = "center",
					padx = PADDING, pady = PADDING,
					background = 'white', borderwidth = 3)
				b.grid(row=i, column=j, sticky = 'n e w s')

		self.table.rowconfigure('all', minsize = 50)
		self.table.columnconfigure('all', minsize = 50)

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
		self.list.pack(anchor = 'center', padx = PADDING, pady = PADDING)

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
		self.main.pack(side = 'left', padx = PADDING)

	def setMainText(self, text):
		self.main['text'] = text

class PlayerList(Listbox):
	def __init__(self, parent):
		Listbox.__init__(self, parent, bg = 'hotpink')

class PlayerAdderFrame(Frame):
	def __init__(self, parent):
		Frame.__init__(self, parent)
		self.pack()

		# self.button = Button(self, text = 'add', takefocus = False, font = DEFAULT_FONT)
		# self.button.pack(anchor = 'n', side = 'right')

		self.edit = Entry(self, font = DEFAULT_FONT, bg = 'white')
		# se.bind('<Return>', cb_se_Return)
		self.edit.pack(side = 'top', fill = 'x', padx = PADDING, pady = PADDING)

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

	def onEditEscape(self, e):
		if self.popup.shown():
			self.popup.hide()
		elif self.getEditText():
			self.clearEdit()
		else:
			# root.quit()
			self.master.quit()

	def onEditTab(self, e):
		self.popup.hide()
		with database.connect(LOCAL_DATABASE_PATH) as db:
			text = self.edit.get()
			names = database.findName(db, text)
		if names:
			if len(names) == 1:
				self.setEditText(names[0]['name'])
			else:
				self.popup.show(names)
		self.edit.focus_set()

	def commmitSuggestion(self):
		if self.popup.shown():
			sel = self.popup.selection()
			if sel is not None:
				name = self.popup.get(sel)
				self.popup.hide()
				if name:
					self.setEditText(name)
					return

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

	def writeDatabasePlayerCountToStatusBar(self):
		playerCount = 0
		with database.connect(LOCAL_DATABASE_PATH) as db:
			db.row_factory = None
			r = db.execute('SELECT count(*) FROM names')
			playerCount = r.fetchone()[0]
		self.status.setMainText(f'There are {playerCount} players in the database.')

def main():
	root = Tk()
	root.title(THISFILE)
	root.geometry('1200x800')

	s = ttk.Style()
	s.theme_create("Style1", parent="alt", settings={
		"TNotebook": {"configure": {"tabmargins": [2, 5, 2, 0] } },
		"TNotebook.Tab": {"configure": {"padding": [100, 10],
		"font" : DEFAULT_MENU_FONT},}
	})
	s.theme_use("Style1")

	tabBar = TabBar(root)

	def cb_root_Escape(e):
		if tabBar.getCurrentTabText() == 'Players':
			return
		root.quit()

	root.bind('<Escape>', cb_root_Escape)


	f1 = Frame(tabBar)
	f1.pack(side = 'top', fill = 'x')

	f2 = Frame(tabBar)
	f2.pack(side = 'top', fill = 'x')

	canvas = Canvas(f2, width = 1200, height = 800)
	canvas.grid(column=0, row=0, sticky='n e w s')
	canvas.create_line((0, 0, 1000, 1000))

	playerAdderFrame = PlayerAdderFrame(root)
	crossTable = CrossTable(root)

	tabBar.add(playerAdderFrame, text = 'Players')
	tabBar.add(crossTable, text = 'Table')
	tabBar.add(f2, text = 'Graphs')
	tabBar.pack(side = 'top', fill = 'both', expand = 1)

	tabBar.autoFocusItems.append(('Players', playerAdderFrame.edit))

	playerAdderFrame.edit.focus_set()

	# import tkinter.font
	# print(tkinter.font.families(root))

	root.mainloop()

if __name__ == '__main__':
	sys.exit(main())
