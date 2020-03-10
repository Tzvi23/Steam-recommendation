#!/usr/bin/env python
# coding: utf-8

# In[1]:
import pickle

import pandas as pd
from random import randint
from random import choice
import math
from user_vector_class import userVector


def evaluate_feature_rec():
    # In[2]:

    userVectorData = pd.read_csv('Vectors_data/user_vector.csv')
    userVectorData.head()

    # In[3]:

    userVectorData.dtypes

    # In[4]:

    gameVector = pd.read_csv('Vectors_data/game_vector.csv')
    gameVector.head()

    # In[5]:

    userPlayTime = pd.read_csv('steamData/game_play.dat', sep='\t')
    userPlayTime.head()

    # In[6]:

    gamePurchas = pd.read_csv('steamData/game_purchase.dat', sep='\t')
    gamePurchas.head()

    # ## =================================================

    # In[7]:

    def choose_random_user(max_user_id, base_number_of_items=5):
        current_user = [1]
        while len(current_user) < base_number_of_items:  # If chosed user id containts only one game choose another
            random_user_id = randint(1, max_user_id)
            current_user = gamePurchas[gamePurchas['User_ID'] == random_user_id]
        return current_user.drop(columns='Purchase'), random_user_id

    # In[8]:

    max_user_id = gamePurchas['User_ID'].max()
    current_user, current_userID = choose_random_user(max_user_id)
    current_user

    # In[9]:

    # Choose game id from user gamelist to remove
    def choose_game_to_remove():
        user_game_ids = current_user['Game_ID'].tolist()
        game_id_for_removal = choice(user_game_ids)
        print('Game id for removal: ' + str(game_id_for_removal))
        return game_id_for_removal

    # In[10]:

    game_to_remove_id = choose_game_to_remove()
    while len(gameVector[gameVector['steam_id'] == game_to_remove_id]) == 0:
        game_to_remove_id = choose_game_to_remove()
    removed_game_vector = gameVector[gameVector['steam_id'] == game_to_remove_id]
    removed_game_vector

    # In[11]:

    # Time user played the game to be removed
    # Needed for calculation of log function upon the game vector to sub from exisitng user vector
    play_time = \
        userPlayTime[(userPlayTime['User_ID'] == current_userID) & (userPlayTime['Game_ID'] == game_to_remove_id)][
            'Hours']
    play_time

    # In[12]:

    removed_game_vector.dtypes

    # In[13]:

    save_steam_id = removed_game_vector['steam_id']
    print('Save steam id: ' + str(save_steam_id))
    removed_game_vector.select_dtypes(exclude=['object'])

    # In[14]:

    # Multiple all the valeus by the log of play time of the game
    try:
        removed_game_vector = removed_game_vector[removed_game_vector.select_dtypes(exclude=['object']).columns].mul(
            math.log(play_time))
        # Return the saved steam id game and changing the type back to int64
        removed_game_vector.iloc[0]['steam_id'] = int(save_steam_id)
        removed_game_vector = removed_game_vector.astype({'steam_id': 'int64'})
        removed_game_vector = removed_game_vector.drop(columns='steam_id')
    except TypeError:
        print('Play time is missing. Time: ' + str(play_time))
    removed_game_vector

    # In[15]:

    try:
        removed_game_vector = removed_game_vector.drop(columns='game_name')
        removed_game_vector = removed_game_vector.drop(columns='steam_id')
    except Exception:
        print('No columns removed')
    removed_game_vector

    # In[16]:

    current_user = current_user[current_user['Game_ID'] != game_to_remove_id]  # Remove the game from the user list
    current_user

    # In[17]:

    base_user_vector = userVectorData[userVectorData['user_id'] == current_userID]
    base_user_vector

    # In[18]:

    removed_game_vector = removed_game_vector.set_index([pd.Series([base_user_vector.index[0]])])
    removed_game_vector

    # In[19]:

    base_user_vector['user_id'].tolist()[0]

    # In[20]:

    removed_game_vector.insert(0, 'user_id', base_user_vector['user_id'].tolist()[0])
    removed_game_vector

    # In[21]:

    userVectorData[userVectorData['user_id'] == base_user_vector['user_id'].tolist()[0]].columns

    # In[22]:

    updatedVector = userVectorData[userVectorData['user_id'] == base_user_vector['user_id'].tolist()[0]].subtract(
        removed_game_vector)
    updatedVector

    # In[23]:

    updatedVector['user_id'] = base_user_vector['user_id'].tolist()[0]
    updatedVector['user_id']

    # In[24]:

    userVectorData.update(updatedVector)

    # In[25]:

    updateUserDict = updatedVector.to_dict('index')[removed_game_vector.index[0]]
    updateUserDict

    # In[26]:

    updateUserDict['user_id']

    # ## ==============Re-arrange data for exisitng functions==================

    # In[81]:

    # %%capture
    from user_vector_data_class import userVectorData
    from src import load_gameIds, recommend_eval, clearVector
    from vector_class import Vector
    import copy

    # In[28]:

    gamesID = load_gameIds()
    gamesID

    # In[32]:

    usr = userVectorData(str(base_user_vector['user_id'].tolist()[0]), gamesID)
    usr

    # In[33]:

    usr.usrVector = updatedVector.to_dict('index')[removed_game_vector.index[0]]
    usr.usrVector

    # ## Convert updated matrix to class vetorDict

    # In[63]:

    game_dict = gameVector.to_dict()
    game_dict

    # In[64]:

    game_keys = game_dict.keys()

    # In[65]:

    def create_empty_vector(keys):
        base_game_vector = dict()
        for item in keys:
            if item != 'game_name' and item != 'steam_id':
                base_game_vector[item] = 0
        return base_game_vector

    # In[66]:

    base_clear_vector = create_empty_vector(game_keys)

    # In[67]:

    number_of_games = len(game_dict['game_name'])

    # In[68]:

    VectorDict = dict()

    # In[78]:

    def convertMatrix(game_dict, number_of_games, game_keys, base_clear_vector, VectorDict):
        val_vector = clearVector(base_clear_vector)
        for index in range(number_of_games):  # Rows
            newVector = Vector(val_vector)
            for key in game_keys:  # Columns
                if key == 'steam_id':
                    newVector.gameSteamID = int(game_dict[key][index])
                elif key == 'game_name':
                    newVector.gameName = game_dict[key][index]
                else:
                    newVector.vectorValues[key] = game_dict[key][index]
            newVector.create_full_dict()
            VectorDict[newVector.gameSteamID] = copy.deepcopy(newVector)
        return VectorDict

    # In[79]:

    VectorDict = convertMatrix(game_dict, number_of_games, game_keys, base_clear_vector, VectorDict)

    with open('backupData/vectorData.pickle', mode='rb') as p:
        print('Pickle Data Exists. Loading !!')
        VectorDict2 = pickle.load(p)

    new_user = userVector(str(current_userID), clearVector(base_clear_vector), str(game_to_remove_id))
    new_user.calculateUserVector(VectorDict2)
    usr.usrVector = copy.deepcopy(new_user.vector)
    # ## ==============================================

    # In[80]:

    return recommend_eval(usr, VectorDict, game_to_remove_id)


counter = 0
numberOfTests = 4
for _ in range(numberOfTests):
    print('============== Test Number {0} ================'.format(_))
    counter += evaluate_feature_rec()

print('Number of attempts: {0} \nNumber of Success: {1} \nRatio:{2}'.format(numberOfTests, counter,
                                                                            counter / float(numberOfTests)))
