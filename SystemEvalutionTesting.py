#!/usr/bin/env python
# coding: utf-8

# In[1]:


import pandas as pd
from random import randint
from random import choice
import math


# In[2]:
from src import game_Ids
from user_similiraty import create_recommend_pairs_eval
from user_vector_data_class import userVectorData


def create_new_user_vector_matrix():
    userVector = pd.read_csv('Vectors_data/user_vector.csv')
    userVector.head()

    # In[3]:

    userVector.dtypes

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
    userPlayTime[(userPlayTime['User_ID'] == current_userID) & (userPlayTime['Game_ID'] == game_to_remove_id)]['Hours']
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

    base_user_vector = userVector[userVector['user_id'] == current_userID]
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

    userVector[userVector['user_id'] == base_user_vector['user_id'].tolist()[0]].columns

    # In[22]:

    updatedVector = userVector[userVector['user_id'] == base_user_vector['user_id'].tolist()[0]].subtract(
        removed_game_vector)
    updatedVector

    # In[23]:

    updatedVector['user_id'] = base_user_vector['user_id'].tolist()[0]
    updatedVector['user_id']

    # In[24]:

    userVector.update(updatedVector)

    # In[25]:

    updateUserDict = updatedVector.to_dict('index')[removed_game_vector.index[0]]
    updateUserDict

    # In[26]:

    updateUserDict['user_id']

    return userVector, current_userID, game_to_remove_id


def recommend_similar_user():
    updateMatrix, current_user, remove_game = create_new_user_vector_matrix()
    results = create_recommend_pairs_eval(updateMatrix)
    matched_user_id = int(results[float(current_user)])
    usr = userVectorData(str(matched_user_id), game_Ids)
    if str(remove_game) in usr.gameNames.keys():
        print('Similar user: game removed Found!')
        return 1
    else:
        print('Similar user: game not Found!')
        return 0


def eval_similarUser(numOfTests):
    counter = 0
    for _ in range(numOfTests):
        counter += recommend_similar_user()
    result = counter / float(numOfTests)
    print('Similar user eval results: {0}'.format(result))

