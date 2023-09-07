from Result import Result

class Pairing:

	def __init__(self, white, black):
		self.white = white
		self.black = black
		self.result = None

	def setResult(self, result):
		if result == Result.WIN:
			self.white.addResult(Result(self.black.id, Result.WHITE, Result.WIN))
			self.black.addResult(Result(self.white.id, Result.BLACK, Result.LOSS))
		elif result == Result.LOSS:
			self.white.addResult(Result(self.black.id, Result.WHITE, Result.LOSS))
			self.black.addResult(Result(self.white.id, Result.BLACK, Result.WIN))
		elif result == Result.DRAW:
			self.white.addResult(Result(self.black.id, Result.WHITE, Result.DRAW))
			self.black.addResult(Result(self.white.id, Result.BLACK, Result.DRAW))
		elif result == Result.UBYE:
			player = self.white if self.white else self.black
			player.addResult(Result(Result.NO_ID, Result.NO_COLOR, Result.UBYE))
		else:
			raise ValueError('invalid result')
		self.result = result

	def __iter__(self):
		yield self.white
		yield self.black

	def __repr__(self):
		result = self.result if self.result else '-'
		return f'{self.white} {result} {self.black}'

	def __format__(self, format):
		result = self.result if self.result else '-'
		return f'{self.white:{format}} {result} {self.black}'
