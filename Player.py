import io

from Result import Result

class Player:
	'''
	>>> player = Player(7, Player.MALE, Player.UNTITLED, 'Dejan Budimir', 1560, 'GER', 0, '1980/06/07')
	>>> player.results = [Result(1, Result.BLACK, Result.LOSS)]
	>>> print('|', player.toTrf(), '|', sep='')
	|001    7 m    Dejan Budimir                     1560 GER           0 1980/06/07  0.0    1     1 b 0|
	'''
	MALE = 'm'
	FEMALE = 'w'
	UNTITLED = ' '
	GM = 'g'
	FM = 'f'
	CM = 'c'
	IM = 'i'

	def __init__(self, id = 0, sex = '', title = '', name = '', rating = 0, federation = '', fideNumber = 0, birthDate = ''):
		self.id = int(id or 0)
		self.sex = sex or ''
		self.title = title or ''
		self.name = name or ''
		self.rating = int(rating or 0)
		self.federation = federation or ''
		self.fideNumber = int(fideNumber or 0)
		self.birthDate = birthDate or ''
		self.tournament = None
		self.wins = 0
		self.draws = 0
		self.losses = 0
		self.ubyes = 0
		self.rank = 1
		self.results = []

	def __repr__(self):
		return f"{self.name}{f' ({self.rating})' if self.rating else ''}"

	def __format__(self, format):
		text = repr(self)
		return f'{text:{format}}'

	@property
	def score(self):
		if not self.tournament: return 0
		return sum((
			self.wins * self.tournament.pointsForWin,
			self.draws * self.tournament.pointsForDraw,
			self.losses * self.tournament.pointsForLoss,
			self.ubyes * self.tournament.pointsForUBye,
			))

	def isFemale(self):
		return self.sex == 'w'

	def isMale(self):
		return self.sex == 'm'

	def addResult(self, result):
		if result.result == Result.WIN:
			self.wins += 1
		elif result.result == Result.LOSS:
			self.losses += 1
		elif result.result == Result.DRAW:
			self.draws += 1
		elif result.result == Result.UBYE:
			self.ubyes += 1
		self.results.append(result)

	def toTrf(self):
		s = io.StringIO()
		s.write('001 ')
		s.write('%4d ' % self.id)
		s.write(self.sex[0] if self.sex else ' ')
		s.write('%3s ' % self.title)
		s.write('%-33s ' % self.name)
		s.write('%4d ' % self.rating)
		s.write('%-3s ' % self.federation)
		s.write('%11d ' % self.fideNumber)
		s.write('%-10s ' % self.birthDate)
		s.write('%4.1f ' % self.score)
		s.write('%4d' % self.rank)
		for result in self.results:
			s.write(result.toTrf())
		return s.getvalue()
