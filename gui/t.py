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
		self.grid = None

		self.createGrid(7)
		self.setCellText(1, 1, 'Anandarandanand')
		self.setCellText(2, 1, 'Bodkinick')
		self.setCellText(3, 1, 'Carlsbadson')
		self.setCellText(4, 1, 'Ding')
		self.setCellText(5, 1, 'Euwe')
		self.setCellText(6, 1, 'Fischer')
		self.setCellText(7, 1, 'Grischuck')

	def onCellEvent(self, e):
		row, col, text, x, y, w, h = self.getCellDataFromWidget(e.widget)
		print(row, col, text, x, y, w, h)
		# e.widget.focus_set()

	def createGrid(self, playerCount):
		self.destroyGrid()
		rows = playerCount + 1
		cols = playerCount + 4
		self.grid = [[None for i in range(cols)] for j in range(rows)]
		self.table = Frame(self)
		self.table.pack(anchor = 'w', padx = PADDING, pady = PADDING)

		self.createCellAt(0, 0, '#')
		self.createCellAt(0, 1, 'Name')
		for col in range(playerCount):
			self.createCellAt(0, 2 + col, f'{col + 1}')
		self.createCellAt(0, 2 + playerCount + 0, 'Punkte')
		self.createCellAt(0, 2 + playerCount + 1, 'Platz')
		for row in range(1, playerCount + 1):
			self.createCellAt(row, 0, f'{row}')
			self.createCellAt(row, 1, '')
			for col in range(playerCount):
				cursor = 'X_cursor' if row > 0 and row == col + 1 else 'hand2'
				text = 'x' if row == col + 1 else ''
				self.createCellAt(row, 2 + col, text, cursor)
			self.createCellAt(row, 2 + playerCount + 0, '0')
			self.createCellAt(row, 2 + playerCount + 1, '1')

		self.table.rowconfigure('all', minsize = 50)
		self.table.columnconfigure('all', minsize = 50)

	def destroyGrid(self):
		if self.grid:
			for row in self.grid:
				for cell in row:
					print(self.getCellDataFromWidget(cell))
					cell.destroy()
			self.grid = None

	def createCellAt(self, row, col, text = '', cursor = 'hand2'):
		cell = Label(self.table, text = text,
			font = DEFAULT_GRID_FONT,
			relief = "sunken", cursor = cursor, anchor = "center",
			padx = PADDING, pady = PADDING,
			background = 'white', borderwidth = 3)
		cell.grid(row=row, column=col, sticky = 'n e w s')
		cell.bind('<Button>', self.onCellEvent)
		# cell.bind('<KeyPress>', self.onCellEvent)
		self.grid[row][col] = cell

	def setCellText(self, row, col, text):
		if self.grid:
			self.grid[row][col]['text'] = text

	def getCellDataFromWidget(self, widget):
		assert widget.widgetName == 'label'
		i = widget.grid_info()
		row = i['row']
		col = i['column']
		text = widget.config('text')
		x = widget.winfo_x()
		y = widget.winfo_y()
		w = widget.winfo_width()
		h = widget.winfo_height()
		# print(widget.winfo_geometry())
		return row, col, text, x, y, w, h

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
		Listbox.__init__(self, parent, bg = 'white', takefocus = False,
			font = DEFAULT_GRID_FONT, relief = 'flat',
			selectmode = 'browse', activestyle = 'dotbox',
			borderwidth = 0, highlightthickness = 3,
			highlightbackground = 'white', highlightcolor = 'white',
			selectforeground = 'red', selectbackground = 'white',
			selectborderwidth = 1)
		self.pack(side = 'top', fill = 'both', expand = 1, padx = PADDING)
		self.bind("<BackSpace>", self.onBackSpace)

	def onBackSpace(self, e):
		cur = self.index('active')
		self.delete(cur)

	def addRow(self, text):
		self.insert('end', text)

	def loadNames(self):
		with database.connect(LOCAL_DATABASE_PATH) as db:
			for name in database.getNames(db):
				self.addRow(f"{name['id']:2}: {name['name']}")

class PlayerAdderFrame(Frame):
	def __init__(self, parent):
		Frame.__init__(self, parent)
		self.pack()

		# self.button = Button(self, text = 'add', takefocus = False, font = DEFAULT_FONT)
		# self.button.pack(anchor = 'n', side = 'right')

		self.edit = Entry(self, font = DEFAULT_FONT, bg = 'white')
		# se.bind('<Return>', cb_se_Return)
		self.edit.pack(side = 'top', fill = 'x', padx = PADDING, pady = PADDING)

		padder = Frame(self, background = 'white')
		self.playerList = PlayerList(padder)
		padder.pack(side = 'top', fill = 'both', expand = 1, padx = PADDING)

		self.status = StatusBar(self)
		self.popup = SuggestionPopup(self, self.edit)

		self.edit.bind("<Return>", lambda e: self.commmitSuggestion())
		self.edit.bind("<Escape>", self.onEditEscape)
		self.edit.bind("<Tab>", self.onEditTab)
		self.edit.bind("<Up>", self.onUpArrow)
		self.edit.bind("<Down>", self.onDownArrow)
		# self.edit.bind("<KeyPress>", self.onKeyPress)
		self.edit.bind("<Next>", self.onEditPageDown)
		self.playerList.bind("<Prior>", self.onPlayerListPageUp)

		self.writeDatabasePlayerCountToStatusBar()

	def onEditPageDown(self, e):
		self.popup.hide()
		self.playerList.focus_set()

	def onPlayerListPageUp(self, e):
		self.edit.focus_set()

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

	def onUpArrow(self, e):
		if self.popup.shown():
			self.selectPrev()

	def onDownArrow(self, e):
		if self.popup.shown():
			self.selectNext()

	def commmitSuggestion(self):
		if self.popup.shown():
			sel = self.popup.selection()
			if sel is not None:
				name = self.popup.get(sel)
				self.popup.hide()
				if name:
					self.setEditText(name)
					return
		else:
			text = self.getEditText()
			if text:
				self.playerList.addRow(text)
				self.clearEdit()

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

	playerAdderFrame = PlayerAdderFrame(root)
	tabBar.add(playerAdderFrame, text = 'Players')

	crossTable = CrossTable(root)
	tabBar.add(crossTable, text = 'Table')

	graphs = Frame(tabBar)
	canvas = Canvas(graphs, width = 1200, height = 800)
	# canvas.pack(side = 'top', fill = 'both', expand = 1)
	canvas.pack()
	tabBar.add(graphs, text = 'Graphs')

	canvas.create_line((0, 0, 1000, 1000))

	tabBar.autoFocusItems.append(('Players', playerAdderFrame.edit))
	tabBar.pack(side = 'top', fill = 'both', expand = 1)

	# import tkinter.font
	# print(tkinter.font.families(root))

	def onEscape(e):
		if tabBar.getCurrentTabText() == 'Players':
			widget = playerAdderFrame.focus_get()
			if widget.widgetName == 'entry':
				return
		root.quit()

	root.bind('<Escape>', onEscape)

	playerAdderFrame.edit.focus_set()

	root.mainloop()

if __name__ == '__main__':
	sys.exit(main())
