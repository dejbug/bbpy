class Result:
	NO_ID = '0000'
	BLACK = 'b'
	WHITE = 'w'
	NO_COLOR = '-'
	WIN = '1'
	DRAW = '='
	LOSS = '0'
	WIN_0 = 'W'
	DRAW_0 = 'D'
	LOSS_0 = 'L'
	HBYE = 'H'
	FBYE = 'F'
	UBYE = 'U'
	ZBYE = 'Z'

	def __init__(self, opponent, color, result):
		self.opponent = opponent
		self.color = color
		self.result = result

	def toTrf(self):
		if not self.opponent or self.opponent == self.NO_ID:
			return f'  0000 {self.color} {self.result}'
		return f'  {self.opponent:4d} {self.color} {self.result}'
