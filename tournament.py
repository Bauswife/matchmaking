from functools import cmp_to_key
from os.path import exists
from matchmaking import Matchmaker
import pickle
from random import shuffle


class Player:

    def __init__(self, playerID, name):
        self.id = playerID
        self.name = name
        self.playing = True
        self.tables = []


class Result:
    count = 0
    tieID = -1

    def __init__(self, player1ID, player2ID, winnerID):
        self.id = Result.count
        self.player1ID = player1ID
        self.player2ID = player2ID
        self.winnerID = winnerID
        Result.count += 1


class Database:
    players = []
    results = []

    def __init__(self, name, winPoints, tiePoints):
        self.name = name
        self.winPoints = winPoints
        self.tiePoints = tiePoints
        self.playerCount = 0

    def addPlayer(self, name, playerID=-1):
        if playerID == -1:
            playerID = self.playerCount
        self.players.append(Player(playerID, name))
        if (playerID >= self.playerCount):
            self.playerCount = playerID + 1

    def reportResult(self, player1ID, player2ID, winnerID):
        self.results.append(Result(player1ID, player2ID, winnerID))

    def playerFileName(self):
        return self.name + "_players.txt"

    def resultsFileName(self):
        return self.name + "_results.txt"

    def fileName(self):
        return self.name + "_data.lit"

    def writeToFile(self):
        pickle.dump(self, open(self.fileName(), "wb"))

    def readFromFile(self):
        db = pickle.load(open(self.fileName(), "rb"))
        self.results += db.results
        self.players += db.players
        self.playerCount = db.playerCount

    def printPlayers(self):
        for player in self.sortedPlayers():
            print("{0}: {1} - {2} poäng".format(player.id,
                  player.name, self.getPlayerScore(player.id)))

    def printResults(self):
        def pString(playerID):
            if (playerID == Result.tieID):
                return "Ingen segrare"
            player = self.getPlayerByID(playerID)
            return player.name + '(id: ' + str(player.id) + ')'
        for result in self.results:
            print("Parti {} - Spelare 1: {:20} Spelare 2: {:20} Segrare: {:20}".format(result.id,
                  pString(result.player1ID), pString(result.player2ID), pString(result.winnerID)))

    def getPlayerByID(self, playerID):
        return list(filter(lambda player: player.id == playerID, self.players))[0]

    def getResultByID(self, resultID):
        return list(filter(lambda result: result.id == resultID, self.results))[0]

    def filterPlayerGames(self, playerID, lst):
        return list(filter(lambda elem: (elem.player1ID == playerID or elem.player2ID == playerID), lst))

    def getPlayerGames(self, playerID):
        return self.filterPlayerGames(playerID, self.results)

    def getFirstPlayerAmount(self, playerID):
        return sum(game.player1ID == playerID for game in self.results)

    def getPlayerScore(self, playerID):
        games = self.getPlayerGames(playerID)
        wPoints = self.winPoints * \
            sum(game.winnerID == playerID for game in games)
        tPoints = self.tiePoints * \
            sum(game.winnerID == Result.tieID for game in games)
        return wPoints + tPoints

    def comparePlayers(self, player1, player2):

        def scoreComparison(player1ID, player2ID):
            player1Score = self.getPlayerScore(player1ID)
            player2Score = self.getPlayerScore(player2ID)
            return player2Score - player1Score

        def prevMatchupComparison(player1ID, player2ID):
            prevGames = self.filterPlayerGames(
                player2ID, self.getPlayerGames(player1ID))
            player1Wins = sum(game.winnerID == player1ID for game in prevGames)
            player2Wins = sum(game.winnerID == player2ID for game in prevGames)
            return player2Wins - player1Wins

        def firstPlayerComparison(player1ID, player2ID):
            player1FirstPlayer = self.getFirstPlayerAmount(player1ID)
            player2FirstPlayer = self.getFirstPlayerAmount(player2ID)
            return player2FirstPlayer - player1FirstPlayer

        comparisons = [scoreComparison,
                       prevMatchupComparison, firstPlayerComparison]
        for comparison in comparisons:
            comparisonValue = comparison(player1.id, player2.id)
            if (comparisonValue != 0):
                return comparisonValue
        return 0

    def sortedPlayers(self):
        players = self.players
        shuffle(players)
        players = sorted(players, key=cmp_to_key(self.comparePlayers))
        playingPlayers = []
        for player in players:
            if (player.playing):
                playingPlayers.append(player)
        return playingPlayers

    def removePlayer(self, playerID):
        self.getPlayerByID(playerID).playing = False

    def removeResult(self, resultID):
        self.results.remove(self.getResultByID(resultID))


def inputResult(db):
    while True:
        db.printPlayers()
        player1ID = int(input("Mata in id för spelare 1: "))
        player1 = db.getPlayerByID(player1ID)
        player2ID = int(input("Mata in id för spelare 2: "))
        player2 = db.getPlayerByID(player2ID)
        tie = input("Blev det lika? (Y/N): ")
        if tie == "Y":
            winnerID = Result.tieID
        else:
            winnerID = int(input("Mata in id för segrare: "))
            winner = db.getPlayerByID(winnerID)

        print("Är detta korrekt?")
        print("Spelare 1")
        print("id:", player1.id)
        print("namn:", player1.name, "\n")
        print("Spelare 2")
        print("id:", player2.id)
        print("namn:", player2.name, "\n")
        if tie == "Y":
            print("Ingen segrare")
        else:
            print("Segrare")
            print("id:", winner.id)
            print("namn:", winner.name)
        korrekt = input("(Y/N): ")

        if (korrekt == 'Y'):
            db.reportResult(player1ID, player2ID, winnerID)
            break


def printPairings(db, pairings):
    counter = 1
    for pairing in pairings:
        player1 = db.getPlayerByID(pairing[0])
        player2 = db.getPlayerByID(pairing[1])
        print("Bord {} - Spelare 1: {}, Spelare 2: {}".format(counter,
              player1.name, player2.name))
        counter += 1


print('''Välkommen till dominionturneringsprogrammet!''')
while True:
    eventName = input('''Vänligen mata in namn på turneringen: ''')
    db = Database(eventName, 3, 1)
    if exists(db.fileName()):
        willImport = input(
            '''Det finns en tidigare turnering med det namnet. Vill du återuppta den? (Y/N): ''')
        if willImport == "Y":
            db.readFromFile()
            break
    else:
        break


while True:
    val = int(input('''
    
Meny

1. Lägg till spelare
2. Rapportera resultat
3. Visa spelarlista
4. Visa resultatlista
5. Ta bort resultat
6. Ta bort spelare
7. Generera pairings
8. Avsluta turnering
    
Vad vill du göra? '''))
    modified = False
    if val == 1:
        namn = input("Mata in spelarnamn: ")
        db.addPlayer(namn)
        modified = True
    if val == 2:
        inputResult(db)
        modified = True
    if val == 3:
        db.printPlayers()
    if val == 4:
        db.printResults()
    if val == 5:
        db.printResults()
        resultID = int(input("Mata in partiets ID: "))
        db.removeResult(resultID)
        modified = True
    if val == 6:
        db.printPlayers()
        playerID = int(input("Mata in spelares ID: "))
        db.removePlayer(playerID)
        modified = True
    if val == 7:
        matchmaker = Matchmaker(db)
        printPairings(db, matchmaker.generatePairings())
    if val == 8:
        break
    if modified:
        db.writeToFile()
