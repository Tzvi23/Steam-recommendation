import os
import csv
import math
import copy


class userVectorData:
    def __init__(self, usrId, gameID):
        self.userId = usrId
        self.usrVector = dict()
        self.gameNames = gameID
        self.purchaseInfoFile = "steamData/game_purchase.dat"
        self.userPurchasedGamesStr = list()
        self.results = list()
        self.gamePurchasedIds = list()
        # Init
        self.getListOfGames()

    def __str__(self):
        return "User ID: " + self.userId

    def getListOfGames(self):
        with open(self.purchaseInfoFile, mode='r') as info:
            for line in info:
                currentUsrID, currentGameID = line.replace("\n", "").split("\t")[0], line.replace("\n", "").split("\t")[
                    1]
                if currentUsrID == self.userId:
                    self.userPurchasedGamesStr.append(self.gameNames[currentGameID])
                    self.gamePurchasedIds.append(int(currentGameID))

    def loadUsrVector(self, fileName):
        if os.path.isfile(fileName):
            with open(fileName, mode='r') as dataFile:
                dataReader = csv.DictReader(dataFile)
                firstLine = True
                for line in dataReader:
                    if firstLine:
                        self.createDict(line)
                        if line['user_id'] == self.userId:
                            self.loadVector(line)
                            break
                        firstLine = False
                    else:
                        if line['user_id'] == self.userId:
                            self.loadVector(line)
                            break

    def createDict(self, data):
        for item in data.keys():
            self.usrVector[item] = 0
        del self.usrVector['user_id']

    def loadVector(self, data):
        for key in self.usrVector.keys():
            self.usrVector[key] = data[key]

    def calculate(self, vectorDataSet):
        print("Calculating vectors for {0}".format(self))
        for key in vectorDataSet.keys():
            # If game already in user vector skip.
            # if str(key) in self.usrVector:
            #     continue
            upper_sum, left_square, right_square = 0, 0, 0
            x = copy.deepcopy(self.usrVector)
            y = vectorDataSet[key].vectorValues
            for xKey in x:
                if xKey == 'user_id':
                    continue
                upper_sum += (float(x[xKey]) * y[xKey])
                left_square += math.pow(float(x[xKey]), 2)
                right_square += math.pow(float(y[xKey]), 2)
            left_square = math.sqrt(left_square)
            right_square = math.sqrt(right_square)
            try:
                res = upper_sum / (left_square * right_square)
                if res > 1:
                    res = 1
                ans = math.acos(res)
            except ZeroDivisionError:
                ans = math.acos(0)
            self.results.append((vectorDataSet[key].gameSteamID, ans))
        self.results = self.Sort_Tuple(self.results)  # Sort ascending all the values
        self.print_Top(5)
        return self.results

    # Function to sort hte list by second item of tuple
    def Sort_Tuple(self, tup):

        # reverse = None (Sorts in Ascending order)
        # key is set to sort using second element of
        # sublist lambda has been used
        tup.sort(key=lambda x: x[1], reverse=True)
        return tup

    def print_Top(self, top=5):
        print("Recommending Top {0} Games for {1}".format(top, self.userId))
        for i in range(top):
            print("[#{0}] Game Name: {1} | Cosine Score: {2:2.4f}".format(i + 1, self.gameNames[str(self.results[i][0])], self.results[i][1]))

    def print_Owned_games(self):
        owned_games = list()
        print(" ================================ ")
        print("{0} owned the following games: ".format(self.userId))
        counter = 1
        for game in self.userPurchasedGamesStr:
            owned_games.append(str(counter) + ' ' + str(game))
            print("[{0}] {1}".format(counter, game))
            counter += 1
        print("[!] Total of : {0}".format(counter - 1))
        print(" ================================ ")
        return owned_games

# usr = userVectorData('1652', None)
# usr.loadUsrVector('Vectors_data/user_vector.csv')
