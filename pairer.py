import sys, os, re, io, tempfile, subprocess

from utils import stringify

from Tournament import Tournament
from Player import Player
from Result import Result

BBP = '.local/bin/bbpPairings-v5.0.1/bbpPairings.exe'

DEFAULT_TEMP_PATH = '.local/tmp/'
PLAYERS_SAMPLE_PATH = '.local/sample.players'

class Error(Exception): pass
class PairingExeError(Error): pass

def PlayerFactory(tournament, sex = '', title = '', federation = ''):
	sex = sex or ''
	title = title or ''
	federation = federation or ''
	def _(name = '', rating = 0, birthDate = '', fideNumber = 0, id = 0, sex = sex, title = title, federation = federation):
		player = Player(id, sex, title, name, rating, federation, fideNumber, birthDate)
		player.tournament = tournament
		return player
	return _

def getNextPairingsText(tournament):
	file, tmpPath  = tempfile.mkstemp(suffix = '.trf', dir = DEFAULT_TEMP_PATH, text = True)
	os.write(file, tournament.toTrf().encode('utf8'))
	os.close(file)
	p = subprocess.run([os.path.abspath(BBP), '--dutch', tmpPath, '-p'], capture_output = True)
	if p.stderr:
		raise PairingExeError(p.stderr)
	# os.remove(tmpPath)
	return p.stdout.decode('utf8')

def parsePairingsText(text):
	mm = re.finditer(r'\d+', text)
	mm = list(mm)
	nn = (int(m.group(0)) for m in mm)
	count = next(nn)
	pairings = list(nn)
	if len(pairings) // 2 != count:
		return None
	for i in range(0, len(pairings), 2):
		yield pairings[i], pairings[i+1]

def getNextPairings(tournament):
	text = getNextPairingsText(tournament)
	# return list(parsePairingsText(text))
	for wid, bid in parsePairingsText(text):
		yield tournament.getPairing(wid, bid)

def iterPlayersFromPlayersFile(path, playerFactory = Player):
	with open(path) as file:
		for line in file:
			parts = line.split(',')
			parts = [part.strip() for part in parts]
			name = parts[0]
			rating = int(parts[1])
			bday = parts[2]
			fid = int(parts[3] if parts[3] else 0)
			yield playerFactory(name = name, rating = rating, birthDate = bday, fideNumber = fid)

if __name__ == '__main__':
	tournament = Tournament(maxRounds = 5)
	playerFactory = PlayerFactory(tournament, Player.MALE, Player.UNTITLED, 'GER')
	for player in iterPlayersFromPlayersFile(PLAYERS_SAMPLE_PATH, playerFactory):
		tournament.addPlayer(player)
	print(tournament.toTrf())
	# tournament.updateInitialRanking()
	# print(tournament.toTrf())

	pairings = list(getNextPairings(tournament))
	# print(pairings); print()

	pairings[0].setResult(Result.WIN)
	pairings[1].setResult(Result.LOSS)
	pairings[2].setResult(Result.WIN)
	pairings[3].setResult(Result.LOSS)
	pairings[4].setResult(Result.WIN)
	pairings[5].setResult(Result.DRAW)
	pairings[6].setResult(Result.UBYE)
	tournament.updateRanking()

	for pairing in pairings:
		print(f'{pairing:>32}')

	print(tournament.toTrf())

	pairings = list(getNextPairings(tournament))
	for pairing in pairings:
		print(f'{pairing:>32}')
