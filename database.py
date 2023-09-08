import sys, sqlite3
import contextlib

SAMPLE_NAMES_FILE = '.local/database/names.csv'

def dict_factory(cursor, row):
	d = {}
	for idx, col in enumerate(cursor.description):
		d[col[0]] = row[idx]
	return d

@contextlib.contextmanager
def connect(path = 'springerbk.sqlite'):
	with sqlite3.connect(path) as db:
		db.row_factory = dict_factory
		yield db

def create(db):
	db.execute('CREATE TABLE IF NOT EXISTS names (id INTEGER PRIMARY KEY, name TEXT UNIQUE, nname TEXT)')

def fillWithNames(db, path = SAMPLE_NAMES_FILE):
	import csv
	with open(path) as file:
		for row in csv.reader(file):
			fname = row[0].strip() if len(row) >= 1 else ''
			name = row[1].strip() if len(row) >= 2 else ''
			nname = row[2].strip() if len(row) >= 3 else ''
			# print(f'{name} "{nname}" {fname}')
			addName(db, fname, name, nname)

def addName(db, fname, name, nname = ''):
	s = f'{fname}, {name}'
	c = db.execute('INSERT OR IGNORE INTO names (name, nname) VALUES (?,?)', (s, nname, ))
	return c.lastrowid

def listNames(db):
	c = db.execute('SELECT * FROM names')
	return c.fetchall()

def findName(db, name):
	name = name.strip() if name else None
	if not name: return []
	c = db.execute('SELECT * FROM names WHERE nname LIKE ? or name LIKE ?', (name, '%' + name + '%'))
	return c.fetchall()

def getNames(db, limit = 64):
	c = db.execute('SELECT * FROM names LIMIT ?', (limit, ))
	# print(c.lastrowid, c.rowcount)
	return c.fetchall()

def getNameById(db, id):
	if not isinstance(id, int): return None
	c = db.execute('SELECT * FROM names WHERE id = ?', (id, ))
	# print(c.lastrowid, c.rowcount)
	return c.fetchone()

def test():
	with connect('springerbk.sqlite') as db:
		create(db)
		fillWithNames(db)

		print(getNameById(db, 3))
		print(getNameById(db, 300))

		pid = addName(db, 'Budimir', 'Dejan')
		if pid: print(f'* Name added with names.id = {pid}')
		print('* found?', findName(db, 'dejan'))

		for name in listNames(db):
			print(name)

def main():
	with connect('springerbk.sqlite') as db:
		create(db)
		fillWithNames(db)

if __name__ == '__main__':
	sys.exit(main())
