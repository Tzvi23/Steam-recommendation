# Steam-recommendation
Steam recommendation system.

Recommendation system based on team data-set from: https://github.com/caserec/Datasets-for-Recommender-Systems/tree/master/Processed%20Datasets/Steam

The data set extended using API site for https://www.igdb.com/ to get more features and data about the games that inculded already in the data set.
All the relevant data convert to vectors and than used cosine similarity to find the closest vectors for recommendation.
This system features 3 recommendation models:
  1. Feature similarity recommendation
  2. User similarity recommendation
  3. Content recommendation

Using pySimpleGui library for gui interface.
