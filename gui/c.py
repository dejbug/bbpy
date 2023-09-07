import curses
import curses.textpad
import sys, re, io
import random


class Tournament:
	def __init__(self):
		self.players = []
		self.text = ''

	def update(self):
		s = io.StringIO()

		nameColumnWidth = self.getMaxNameColumnWidth()
		nameFormat = f'%-{nameColumnWidth}s'

		s.write(f' # | ' + nameFormat % 'Name' + ' |\n')
		s.write(f'---+-' + '-' * nameColumnWidth + '-+\n')
		for row, name in enumerate(self.players):
			s.write(f'{row + 1:2d} | ' + nameFormat % name + ' |')
			for col, _ in enumerate(self.players):
				s.write(f'{col + 1:2d} |')
			s.write('\n')
		self.text = s.getvalue()
		return self.text

	def addPlayer(self, name):
		self.players.append(name)

	def getMaxNameColumnWidth(self):
		return max(len(name) for name in self.players)

	def getHeight(self):
		return 1 + 1 + len(self.players)

	def getWidth(self):
		return (3 + 1 + (1 + self.getMaxNameColumnWidth() + 1) + 1
			+ (4 * len(self.players)) + 1)

t = Tournament()
t.addPlayer('Rubinstein')
t.addPlayer('Steinitz')
t.addPlayer('Benko')
t.addPlayer('Karpov')
t.addPlayer('Teichmann')
t.addPlayer('Lasker')
t.update()
# print(t.text)



def crosstable(win, table):
	SY, SX = win.getmaxyx()

	win.resize(t.getHeight() + 2, t.getWidth() + 2)

	win.box()

	for i, line in enumerate(t.text.split('\n')):
		win.addstr(i + 1, 1, line)

	win.noutrefresh()


def movetorandom(parent, child):
	PSY, PSX = parent.getmaxyx()
	CSY, CSX = child.getmaxyx()
	child.mvwin(random.randint(0, PSY-CSY), random.randint(0, PSX-CSX))


def main(win):
	curses.set_escdelay(100)

	curses.init_pair(1, curses.COLOR_BLUE, curses.COLOR_BLACK)
	curses.init_pair(2, curses.COLOR_CYAN, curses.COLOR_BLACK)
	curses.init_pair(3, curses.COLOR_RED, curses.COLOR_BLACK)
	curses.init_pair(4, curses.COLOR_BLACK, curses.COLOR_WHITE)
	blue = curses.color_pair(1) | curses.A_DIM
	cyan = curses.color_pair(2) | curses.A_DIM
	red = curses.color_pair(3) | curses.A_DIM
	bgred = curses.color_pair(3) | curses.A_DIM | curses.A_REVERSE

	SY, SX = win.getmaxyx()

	sel = 0

	names = ['Player 1', 'Player 2']

	t = win.subwin(20, 30, 5, 3)

	# curses.textpad.rectangle(win, SY-3, 0, SY-1, SX-2)
	w = win.subwin(1, SX - 6, 0, 5)
	editor = curses.textpad.Textbox(w)

	key = None
	while key != 27:

		win.clear()
		win.refresh()

		crosstable(t, {})
		movetorandom(win, t)

		for i, n in enumerate(names):
			# c = red
			# s = curses.A_UNDERLINE if i == sel else 0
			s = curses.color_pair(3) if i == sel else 0
			win.addstr((i+1) % SY, 1, f'{i+1:3}. {n}', s)
		win.move(SY-1, SX-1)

		key = win.getch()
		win.addstr(SY-1, SX-4, "%3d" % key)

		if key == 258: # DOWN ARROW
			# sel = (sel + 1) % len(names)
			if sel + 1 < len(names): sel += 1

		elif key == 259: # UP ARROW
			# sel = (sel - 1) % len(names)
			if sel - 1 >= 0: sel -= 1

		elif key == 8: # BACKSPACE
			if sel >= 0 and sel < len(names):
				del names[sel]
				win.erase()
				win.refresh()
			if sel >= len(names):
				sel = max(0, sel - 1)

		# elif key == 331: # INSERT
		elif key == 10: # RETURN
			w.mvwin(len(names) + 1, 6)
			w.bkgdset(0, curses.color_pair(4))
			w.clear()
			win.refresh()

			editor.edit()
			text = editor.gather()
			text = text.strip()
			if text:
				names.append(text)
				sel = len(names) - 1

			w.bkgdset(0, curses.color_pair(1))
			w.clear()
			win.refresh()

			editor.do_command(1)	# Control-A "Pos 0"
			editor.do_command(11)	# Control-K "Kill Line"
			editor.do_command(12)	# Control-L "Refresh Screen"

		win.addstr(SY-1, SX-8, "%3d" % sel)

		# win.noutrefresh()
		# curses.doupdate()
		# win.refresh()

	# win.getkey()

curses.wrapper(main)
