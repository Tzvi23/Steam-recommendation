import math
import copy


class new_user:
    def __init__(self, userId, chosen_games, baseVector=None):
        self.userID = userId
        self.vector = baseVector
        self.gameOwned = chosen_games
        self.gameOwnedIds = dict()
        self.results = list()
        self.create_gameOwned_dict()

    def __str__(self):
        return "New User name : " + str(self.userID)

    def create_gameOwned_dict(self):
        for game in self.gameOwned:
            game_split = game.split('=')
            self.gameOwnedIds[int(game_split[0])] = game_split[1]

    def calculateNewUserVector(self, gameVectors):
        for game in self.gameOwnedIds.keys():
            try:
                gameVector = gameVectors[game]
            except KeyError:
                continue
            for key in gameVector.vectorValues.keys():
                self.vector[key] += float(gameVector.vectorValues[key])

    def calculate(self, vectorDataSet):
        print("Calculating vectors for {0}".format(self))
        for key in vectorDataSet.keys():
            # If game already in user vector skip.
            # if str(key) in self.vector:
            #     continue
            upper_sum, left_square, right_square = 0, 0, 0
            x = copy.deepcopy(self.vector)
            y = vectorDataSet[key].vectorValues
            for xKey in x:
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
        return self.results

    def Sort_Tuple(self, tup):

        # reverse = None (Sorts in Ascending order)
        # key is set to sort using second element of
        # sublist lambda has been used
        tup.sort(key=lambda x: x[1], reverse=True)
        return tup