import re

from utils import stringify

@stringify
class Name:
	def __init__(self, last = '', first = '', nick = ''):
		self.last = last or ''
		self.first = first or ''
		self.nick = nick or ''

	@classmethod
	def parse(cls, text):
		'''
		>>> Name.parse('Rainer Maria Rilke')
		Name{'last': 'Rilke', 'first': 'Rainer Maria', 'nick': ''}
		>>> Name.parse('Rilke, Rainer Maria')
		Name{'last': 'Rilke', 'first': 'Rainer Maria', 'nick': ''}
		>>> Name.parse('Rainer "Der Panther" Maria Rilke')
		Name{'last': 'Rilke', 'first': 'Rainer Maria', 'nick': 'Der Panther'}
		>>> Name.parse('Rainer Maria "Der Panther" Rilke')
		Name{'last': 'Rilke', 'first': 'Rainer Maria', 'nick': 'Der Panther'}
		>>> Name.parse('Rilke, Rainer "Der Panther" Maria')
		Name{'last': 'Rilke', 'first': 'Rainer Maria', 'nick': 'Der Panther'}
		>>> Name.parse('Rilke, Rainer Maria "Der Panther"')
		Name{'last': 'Rilke', 'first': 'Rainer Maria', 'nick': 'Der Panther'}
		>>> Name.parse('"Der Panther" Rilke, Rainer Maria')
		Name{'last': 'Rilke', 'first': 'Rainer Maria', 'nick': 'Der Panther'}
		>>> Name.parse('Rilke "Der Panther", Rainer Maria')
		Name{'last': 'Rilke', 'first': 'Rainer Maria', 'nick': 'Der Panther'}
		>>> Name.parse('Rilke "Der Panther", Rainer Maria "Orpheus"')
		Name{'last': 'Rilke', 'first': 'Rainer Maria', 'nick': ['Der Panther', 'Orpheus']}
		>>> Name.parse('René Karl Wilhelm Johann Josef Maria Rilke')
		Name{'last': 'Rilke', 'first': 'René Karl Wilhelm Johann Josef Maria', 'nick': ''}
		'''
		name, nicknames = cls.extractNickname(text)
		obj = cls.parseLV(name)
		if not obj:
			obj = cls.parseVL(name)
			if not obj:
				return None
		if nicknames:
			if len(nicknames) == 1:
				obj.nick = nicknames[0]
			else:
				obj.nick = nicknames
		return obj

	@classmethod
	def extractNickname(cls, text):
		parts = re.split(r'("[^"]+")', text)
		parts = (part.strip() for part in parts)
		parts = (part for part in parts if part)
		regulars = []
		nicknames = []
		for part in parts:
			if part[0] == '"':
				nicknames.append(part.strip('"'))
			else:
				regulars.append(part)
		return " ".join(regulars), nicknames

	@classmethod
	def parseLV(cls, text):
		m = re.match(r'\s*(.+?)\s*,\s*(.+)\s*', text)
		if m: return cls(m.group(1), m.group(2))

	@classmethod
	def parseVL(cls, text):
		m = re.match(r'\s*(.+)\s+(.+)\s*', text)
		if m: return cls(m.group(2), m.group(1))

	@classmethod
	def parseVNL(cls, text):
		m = re.match(r'\s*(.+?)\s*"([^"]+)"\s*(.+)\s*', text)
		if m: return cls(m.group(3), m.group(1), m.group(2))
