import io

from utils import getTitleRank

from Pairing import Pairing

class Tournament:
	def __init__(self, maxRounds = 0):
		self.maxRounds = int(maxRounds or 0)
		self.initialColorWhite = True
		self.pointsForWin = 1
		self.pointsForDraw = 0.5
		self.pointsForLoss = 0
		self.pointsForUBye = self.pointsForWin
		self.pointsForFBye = self.pointsForWin
		self.pointsForHBye = self.pointsForDraw
		self.pointsForZBye = self.pointsForLoss
		self.players = []

	def addPlayer(self, player):
		player.id = len(self.players) + 1
		self.players.append(player)

	def getPlayerById(self, id):
		for player in self.players:
			if player.id == id:
				return player

	def getPairing(self, wid, bid):
		return Pairing(self.getPlayerById(wid), self.getPlayerById(bid))

	def updateInitialRanking(self):
		# FIDE 2023 C.04.2.B
		def normalizeName(p):
			return p.name.lower()
		def normalizeTitle(p):
			return getTitleRank(p.title, p.isFemale())
		def normalizeRating(p):
			return int(p.rating)
		self.players = sorted(self.players, key = normalizeName)
		self.players = sorted(self.players, key = normalizeTitle)
		self.players = sorted(self.players, key = normalizeRating, reverse = True)
		for rank, player in enumerate(self.players, start = 1):
			player.rank = rank

	def updateRanking(self):
		# FIDE 2023  C.04.3.A.1-2
		self.players = sorted(self.players, key = lambda p: p.id, reverse = False)
		self.players = sorted(self.players, key = lambda p: p.score, reverse = True)
		for rank, player in enumerate(self.players, start = 1):
			player.rank = rank

	def toTrf(self):
		s = io.StringIO()
		s.write(f'XXR {self.maxRounds}\n')
		s.write(f'XXC rank {"white1" if self.initialColorWhite else "black1"}\n')
		for player in self.players:
			s.write(player.toTrf())
			s.write('\n')
		return s.getvalue()
