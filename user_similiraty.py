import pandas as pd
from sklearn.metrics.pairwise import cosine_similarity
import pickle
import os


def create_recommend_pairs(new_user_obj=None, new_user_flag=False):
    if not new_user_flag:
        results = dict()
        if not os.path.isfile('user_similarity_cosine.pickle'):
            print('Loading User Vector for cosine similarity...')
            # Load user vector data set
            dataSet = pd.read_csv('Vectors_data/user_vector.csv')

            ids = dataSet['user_id'].tolist()  # Convert to list all the user_id col

            #  Create dict to correspond between user_id to vector id
            index_ids = dict()
            for user_id in range(len(ids)):
                index_ids[user_id] = ids[user_id]

            data = dataSet.drop('user_id', axis=1)  # removing the user_id column
            print('Calculating cosine similarity data....')
            cosine_similarities = cosine_similarity(data)

            results = dict()
            for id_rep in range(len(cosine_similarities)):
                results[index_ids[id_rep]] = index_ids[cosine_similarities[id_rep].argsort()[:-3:-1][1]]

            with open('user_similarity_cosine.pickle', mode='wb') as pickle_rick:
                pickle.dump(results, pickle_rick)
        else:
            print('Loading data from user_similarity_cosine.pickle')
            with open('user_similarity_cosine.pickle', mode='rb') as pickle_rick:
                results = pickle.load(pickle_rick)

        return results
    else:
        print('Loading User Vector for cosine similarity...')
        # Load user vector data set
        dataSet = pd.read_csv('Vectors_data/user_vector.csv')

        ids = dataSet['user_id'].tolist()  # Convert to list all the user_id col

        #  Create dict to correspond between user_id to vector id
        index_ids = dict()
        for user_id in range(len(ids)):
            index_ids[user_id] = ids[user_id]
        index_ids[len(ids)] = new_user_obj.userID  # add the new user default id

        # dataSet = dataSet.append(new_user_obj.vector, ignore_index=True)
        data = dataSet.drop('user_id', axis=1)  # removing the user_id column
        data = data.append(new_user_obj.vector, ignore_index=True)
        print('Calculating cosine similarity data....')
        cosine_similarities = cosine_similarity(data)

        results = dict()
        for id_rep in range(len(cosine_similarities)):
            results[index_ids[id_rep]] = index_ids[cosine_similarities[id_rep].argsort()[:-3:-1][1]]

        return results


def create_recommend_pairs_eval(update_user_vector):
    results = dict()
    # Load user vector data set
    dataSet = update_user_vector

    ids = dataSet['user_id'].tolist()  # Convert to list all the user_id col

    #  Create dict to correspond between user_id to vector id
    index_ids = dict()
    for user_id in range(len(ids)):
        index_ids[user_id] = ids[user_id]

    data = dataSet.drop('user_id', axis=1)  # removing the user_id column
    print('Calculating cosine similarity data....')
    cosine_similarities = cosine_similarity(data)

    results = dict()
    for id_rep in range(len(cosine_similarities)):
        results[index_ids[id_rep]] = index_ids[cosine_similarities[id_rep].argsort()[:-3:-1][1]]

    return results
