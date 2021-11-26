def listWithoutTwo(playerList, i):
    return playerList[1:i] + playerList[i+1:]


class Matchmaker:
    def __init__(self, db):
        self.db = db

    def check(self, pairing):
        def hasNotMetBefore(pairing):
            prevMatchups = self.db.filterPlayerGames(
                pairing[0], self.db.getPlayerGames(pairing[1]))
            return len(prevMatchups) == 0

        checks = [hasNotMetBefore]
        for check in checks:
            if not check(pairing):
                return False
        return True

    def pairingHelper(self, playerList):
        def makePairing(p1, p2):
            if self.db.getFirstPlayerAmount(p1) < self.db.getFirstPlayerAmount(p2):
                return [p1, p2]
            return [p2, p1]

        for secondIndex in range(1, len(playerList)):
            pairing = makePairing(playerList[0].id, playerList[secondIndex].id)
            if self.check(pairing):
                if len(playerList) < 4:
                    return [pairing]
                else:
                    res = self.pairingHelper(
                        listWithoutTwo(playerList, secondIndex))
                    if len(res) > 0:
                        res.append(pairing)
                        return res
            else:
                if len(playerList) < 4:
                    return []

        return []

    def pairingHelper2(self, playerList):
        def makePairing(p1, p2):
            if self.db.getFirstPlayerAmount(p1) < self.db.getFirstPlayerAmount(p2):
                return [p1, p2]
            return [p2, p1]

        potentialPairings = []
        for secondIndex in range(1, len(playerList)):
            pairing = makePairing(playerList[0].id, playerList[secondIndex].id)
            if self.check(pairing):
                if len(playerList) < 4:
                    return [[pairing]]
                else:
                    res = self.pairingHelper(
                        listWithoutTwo(playerList, secondIndex))
                    if len(res) > 0:
                        for l in res:
                            l.append(pairing)
                        potentialPairings += res
            else:
                if len(playerList) < 4:
                    return potentialPairings

        return potentialPairings

    def generatePairings(self):
        pairings = self.pairingHelper(self.db.sortedPlayers())
        return pairings
