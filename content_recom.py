import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import linear_kernel

data = pd.read_csv('summaryAnalyze/game_summary_updated.csv')

tf = TfidfVectorizer(analyzer='word', ngram_range=(1, 3), min_df=0, stop_words='english')
tfidf_matrix = tf.fit_transform(data['summary'])

cosine_similarities = linear_kernel(tfidf_matrix, tfidf_matrix)

results = dict()
for d, row in data.iterrows():
    similiar_indexes = cosine_similarities[d].argsort()[:-100:-1]
    similiar_games = [(cosine_similarities[d][i], data['game_name'][i]) for i in similiar_indexes]
    results[row['game_name']] = similiar_games[1:]


def game(gameName):
    return data.loc[data['game_name'] == gameName]['summary'].tolist()


def show_rec(game_name, top=5, eval_mode=False):
    print(results[game_name][:top])
    res = results[game_name][:top]
    rec_list = list()
    for counter in range(len(res)):
        rec_list.append(str(counter + 1) + ' ' + res[counter][1] + ' Score:' + str(res[counter][0]))
    if eval_mode:
        return res
    return rec_list

# show_rec('Fallout 4')
