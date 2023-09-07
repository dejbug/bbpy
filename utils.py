import re

def stringify(cls):
	setattr(cls, '__repr__', lambda self: type(self).__name__ + str(self.__dict__))
	return cls

def getTitleRank(text, female = None):
	# FIDE 2023 C.04.2.B.2.b
	# GM-IM- WGM -FM- WIM -CM- WFM-WCM
	if not text: return 0
	text = text.strip().lower()
	if not text: return 0
	more = len(text) >= 2
	if text[0] == 'g': return 3 if female else 1 #  [G]M
	if text[0] == 'i': return 5 if female else 2 #  [I]M
	if more and text[1] == 'g': return 3         # W[G]M
	if text[0] == 'f': return 7 if female else 4 #  [F]M
	if more and text[1] == 'i': return 5         # W[I]M
	if text[0] == 'c': return 8 if female else 6 #  [C]M
	if more and text[1] == 'f': return 7         # W[F]M
	if more and text[1] == 'c': return 8         # W[C]M
	return 0

def parseBirthDate(text):
	'''
	>>> parseBirthDate('')
	(None, None, None)
	>>> parseBirthDate('1980')
	(1980, None, None)
	>>> parseBirthDate('1980/06')
	(1980, 6, None)
	>>> parseBirthDate('1980/06/07')
	(1980, 6, 7)
	'''
	m = re.search(r'(\d{4})(?:/(\d{2})?(?:/(\d{2})?)?)?', text)
	if not m: return None, None, None
	year, month, day = m.groups()
	if year: year = int(year)
	if month: month = int(month)
	if day: day = int(day)
	return year, month, day
