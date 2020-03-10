import math


class userVector:
    def __init__(self, usrID, baseVector=None, GameRemoved=None):
        self.userID = usrID
        self.gameListID = list()
        self.gameListNames = list()
        self.playTime = dict()
        self.purchaseInfoFile = "steamData/game_purchase.dat"
        self.gamePlayInfoFile = "steamData/game_play.dat"
        self.vector = baseVector
        self.objDict = dict()
        # Init
        self.getListOfGames(GameRemoved)
        self.getPlayTime()

    def __str__(self):
        return "User ID: " + self.userID

    def getListOfGames(self, gameRemoved=None):
        with open(self.purchaseInfoFile, mode='r') as info:
            for line in info:
                currentUsrID, currentGameID = line.replace("\n", "").split("\t")[0], line.replace("\n", "").split("\t")[
                    1]
                if currentUsrID == self.userID:
                    if gameRemoved is None:
                        self.gameListID.append(int(currentGameID))
                    elif currentGameID != gameRemoved:
                        self.gameListID.append(int(currentGameID))

    def getPlayTime(self):
        with open(self.gamePlayInfoFile, mode='r') as info:
            for line in info:
                currentUsrID, currentGameID, currentGameTime = line.replace("\n", "").split("\t")[0], \
                                                               line.replace("\n", "").split("\t")[1], \
                                                               line.replace("\n", "").split("\t")[2]
                if currentUsrID == self.userID:
                    self.playTime[currentGameID] = currentGameTime

    def calculateUserVector(self, gameVectors):
        for game in self.gameListID:
            try:
                gameVector = gameVectors[game]
            except KeyError:
                continue
            for key in gameVector.vectorValues.keys():
                # Multiply by log of time play for each user to factor the playing time in the vector of the game
                if self.playTime.get(str(game), -1) == -1:  # if the user purchased the game but didn't play
                    self.vector[key] += (gameVector.vectorValues[key] * 0)
                else:
                    self.vector[key] += float(gameVector.vectorValues[key] * math.log(float(self.playTime[str(game)])))

    def createObjDir(self):
        self.objDict['user_id'] = self.userID
        for key in self.vector:
            if key != '-1':
                self.objDict[key] = self.vector[key]



# region TestMain
# usr = userVector('1')
# usr.getListOfGames()
# usr.getPlayTime()
# print()
# endregion
