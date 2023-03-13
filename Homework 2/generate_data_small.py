
import os
import numpy as np
import pandas as pd
import time

ROOT_DIR = os.path.dirname(__file__)
num_movies = 50


# Read in the relevant csv files
start_time = time.time()
print("Loading Data...", end = " ")
movies = pd.read_csv(os.path.join(ROOT_DIR, 'movie-lens-data', 'movies.csv'), header=0)
ratings = pd.read_csv(os.path.join(ROOT_DIR, 'movie-lens-data', 'ratings.csv'), header=0)
print("\t\t\t%s seconds" % (time.time() - start_time))

# Remove movies after index num_movies
start_time = time.time()
print("Processing Data...", end = " ")
# Delete movies
for i in range(movies.shape[0]):
    movies = movies[movies["movieId"] <= num_movies]
# Delete ratings
for i in range(ratings.shape[0]):
    ratings = ratings[ratings["movieId"] <= num_movies]
print("\t\t\t%s seconds" % (time.time() - start_time))

# Export CSV files
start_time = time.time()
print("Exporting CSV...", end = " ")
movies.to_csv(os.path.join(ROOT_DIR, 'movie-lens-data-small', 'movies.csv'), index=False)
ratings.to_csv(os.path.join(ROOT_DIR, 'movie-lens-data-small', 'ratings.csv'), index=False)
print("\t\t\t%s seconds" % (time.time() - start_time))