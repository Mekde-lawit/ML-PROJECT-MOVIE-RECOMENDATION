import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.cluster import KMeans
from sklearn.neighbors import NearestNeighbors
from sklearn.metrics.pairwise import cosine_similarity
import pandas as pd

class MovieRecommender:
    def __init__(self, movies_df, ratings_df):
        self.movies = movies_df
        self.ratings = ratings_df
        self._build_models()
        
    def _build_models(self):
        # Content-based model
        tfidf = TfidfVectorizer(stop_words='english')
        self.movies['genres'] = self.movies['genres'].fillna('')
        self.tfidf_matrix = tfidf.fit_transform(self.movies['genres'])
        self.content_similarity = cosine_similarity(self.tfidf_matrix)
        
        # Collaborative model
        self.user_movie_matrix = self.ratings.pivot_table(
            index='userId',
            columns='movieId',
            values='rating'
        ).fillna(0)
        
        kmeans = KMeans(n_clusters=5, random_state=42)
        user_clusters = kmeans.fit_predict(self.user_movie_matrix)
        self.user_movie_matrix['cluster'] = user_clusters
        
        self.knn = NearestNeighbors(metric='cosine', algorithm='brute')
        self.knn.fit(self.user_movie_matrix.drop('cluster', axis=1))
    
    def content_recommend(self, movie_title, n=10):
        if movie_title not in self.movies['title'].values:
            return pd.DataFrame(columns=['title', 'genres'])
        
        idx = self.movies[self.movies['title'] == movie_title].index[0]
        sim_scores = list(enumerate(self.content_similarity[idx]))
        sim_scores = sorted(sim_scores, key=lambda x: x[1], reverse=True)
        sim_scores = sim_scores[1:n+1]
        movie_indices = [i[0] for i in sim_scores]
        
        return self.movies.iloc[movie_indices][['title', 'genres']]
    
    def collaborative_recommend(self, user_id, n=10):
        if user_id not in self.user_movie_matrix.index:
            popular = self.ratings.groupby('movieId')['rating'].mean().sort_values(ascending=False).head(n)
            return self.movies[self.movies['movieId'].isin(popular.index)][['title', 'genres']]
        
        user_vector = self.user_movie_matrix.drop('cluster', axis=1).loc[user_id]
        
        if user_vector.sum() == 0:
            popular = self.ratings.groupby('movieId')['rating'].mean().sort_values(ascending=False).head(n)
            return self.movies[self.movies['movieId'].isin(popular.index)][['title', 'genres']]
        
        distances, indices = self.knn.kneighbors([user_vector], n_neighbors=min(6, len(self.user_movie_matrix)))
        neighbors = self.user_movie_matrix.index[indices.flatten()]
        
        neighbor_ratings = self.ratings[self.ratings['userId'].isin(neighbors)]
        
        top_movies = neighbor_ratings.groupby('movieId')['rating'].mean().sort_values(ascending=False).head(n)
        
        return self.movies[self.movies['movieId'].isin(top_movies.index)][['title', 'genres']]
    
    def hybrid_recommend(self, user_id, movie_title, n=10):
        content_recs = self.content_recommend(movie_title, n*2)
        collab_recs = self.collaborative_recommend(user_id, n*2)
        
        if content_recs.empty and collab_recs.empty:
            popular = self.ratings.groupby('movieId')['rating'].mean().sort_values(ascending=False).head(n)
            return self.movies[self.movies['movieId'].isin(popular.index)][['title', 'genres']]
        
        hybrid = pd.concat([content_recs, collab_recs])
        hybrid = hybrid.drop_duplicates(subset=['title'])
        
        return hybrid.head(n)
