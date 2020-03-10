class Vector:
    def __init__(self, vectorVals, name="", gameID=-1):
        self.vectorValues = vectorVals
        self.gameName = name
        self.gameSteamID = gameID
        self.vectorDict = dict()

    def create_full_dict(self):
        self.vectorDict['game_name'] = self.gameName
        self.vectorDict['steam_id'] = self.gameSteamID
        for key in self.vectorValues:
            self.vectorDict[key] = self.vectorValues[key]
