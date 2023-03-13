# Code (c) Andrew Balaschak, 2023
# Run program on 'movie-lens-data-small' folder to process a 50 movie dataset

import os
import numpy as np
import pandas as pd
import time
from scipy.spatial.distance import cosine

# Supress warning
from warnings import simplefilter
simplefilter(action="ignore", category=pd.errors.PerformanceWarning)

ROOT_DIR = os.path.dirname(__file__)
USE_SMALL_DATA = False

####################################################################################################
# a) Construct the profile of each item (i.e., movie). At the minimum, you should use the ratings given by each user for a given item (i.e., movie).
# Optionally, you can use other information (e.g., genre information for each movie and tag information given by user for each movie) creatively.
# If you use this additional information, you should explain your methodology in the submitted report.
start_time = time.time()
print("Loading Data...", end = " ")

# Read in the relevant csv files
if(USE_SMALL_DATA):
    movies = pd.read_csv(os.path.join(ROOT_DIR, 'movie-lens-data-small', 'movies.csv'), header=0, usecols=["movieId", "title"])
    ratings = pd.read_csv(os.path.join(ROOT_DIR, 'movie-lens-data-small', 'ratings.csv'), header=0)
else:
    movies = pd.read_csv(os.path.join(ROOT_DIR, 'movie-lens-data', 'movies.csv'), header=0, usecols=["movieId", "title"])
    ratings = pd.read_csv(os.path.join(ROOT_DIR, 'movie-lens-data', 'ratings.csv'), header=0)

# Merge the movies table with the ratings table
merged_movies = pd.merge(movies, ratings, on="movieId")

# Create table of userId and movie title with rating as value
movie_ratings = merged_movies.pivot_table(index='userId', columns='movieId', values='rating')
print("\t\t\t%s seconds" % (time.time() - start_time))


####################################################################################################
# b) Compute similarity score for all item-item (i.e., movie-movie) pairs.
# You will employ the centered cosine similarity metric that we discussed in class.
start_time = time.time()
print("Calculating Similarity...", end = " ")

# Center user's ratings
for i in range(movie_ratings.shape[0]):
    average_rating = np.nanmean(movie_ratings.iloc[i,:])
    movie_ratings.iloc[i,:] = movie_ratings.iloc[i,:] - average_rating
    movie_ratings.iloc[i,:] = movie_ratings.iloc[i,:].fillna(0)

# New dataframe for item-item similarity
movie_similarity = pd.DataFrame(index=movie_ratings.columns, columns=movie_ratings.columns)
movie_similarity = movie_similarity.fillna(0)

# Calculate cosine similarity
for i in range(0, movie_ratings.columns.size):
    for j in range(i, movie_ratings.columns.size):
        dot = np.dot(movie_ratings.iloc[:,i], movie_ratings.iloc[:,j])
        magnitude = np.linalg.norm(movie_ratings.iloc[:,i]) * np.linalg.norm(movie_ratings.iloc[:,j])
        movie_similarity.at[i+1,j+1] = dot/magnitude
        movie_similarity.at[j+1,i+1] = dot/magnitude

print("\t\t%s seconds" % (time.time() - start_time))
movie_similarity.to_csv(os.path.join(ROOT_DIR, 'similarity.csv'))


####################################################################################################
# c) Compute the neighborhood set N for each item (i.e. movie). You will select the movies that have highest similarity score for the given movie.
# Please employ a neigborhood of size 5. Break ties using lexicographic ordering over movie-ids.
start_time = time.time()
print("Calculating Neighborhood...", end = " ")

# New dataframe for neighborhood set
neighborhood_movieId = pd.DataFrame(index=movie_similarity.columns, columns=range(6))
neighborhood_similarity = pd.DataFrame(index=movie_similarity.columns, columns=range(6))

for i in range(0, movie_similarity.columns.size):
    neighborhood_movieId.iloc[i] = movie_similarity.iloc[0:,i].sort_values(ascending=False)[:6].index
    neighborhood_similarity.iloc[i] = movie_similarity.iloc[0:,i].sort_values(ascending=False)[:6]

# Since each movie is most similar to itself, drop the first column
neighborhood_movieId.drop(columns=neighborhood_movieId.columns[0], axis=1, inplace=True)
neighborhood_similarity.drop(columns=neighborhood_similarity.columns[0], axis=1, inplace=True)

print("\t\t%s seconds" % (time.time() - start_time))


####################################################################################################
# d) Estimate the ratings of other users who didn’t rate this item (i.e., movie) using the neighborhood set. Repeat for each item (i.e., movie).
start_time = time.time()
print("Estimating Ratings...", end = " ")

# Index = userId
# Column = movieId
# Value = estimated rating
estimated_ratings = pd.DataFrame(index=range(671), columns=range(1, movie_similarity.columns.size+1))
estimated_ratings.index.name = 'userId'
estimated_ratings.columns.name = 'movieId'
estimated_ratings = estimated_ratings.fillna(0)

print()
print(movie_ratings)

for i in range(0, movie_ratings.shape[0]):
    for j in range(0, movie_ratings.columns.size):
        if(movie_ratings.iloc[i,j] == 0):
            # Estimate rating for user i rating movie j
            numerator = 0
            denominator = 0
            for k in range(5):
                temp_movieId = neighborhood_movieId.at[j+1, k+1]
                numerator += movie_ratings.at[i+1, temp_movieId]
            denominator = neighborhood_similarity.iloc[[j]].sum(axis=1)[1]
            estimated_ratings.at[i,j] = numerator / denominator

print("\t\t\t%s seconds" % (time.time() - start_time))


####################################################################################################
# e) Compute the recommended items (movies) for each user. Pick the top-5 movies with highest estimated ratings.
# Break ties using lexicographic ordering over movie-ids.
# Your program should output top-5 recommendations for each user.
start_time = time.time()
print("Computing Recommendations...", end = " ")

# Now all we have to do here is sort the user's movie ratings and pick the top 5, just like with the neighborhood
for i in range(0, estimated_ratings.shape[0]):
    estimated_ratings.iloc[i] = estimated_ratings.iloc[0:,i].sort_values(ascending=False)[:6].index

print("\t\t%s seconds" % (time.time() - start_time))