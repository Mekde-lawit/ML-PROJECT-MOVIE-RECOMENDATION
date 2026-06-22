from flask import Flask, request, jsonify
from flask_cors import CORS
import pandas as pd
from recommender import MovieRecommender

import warnings
warnings.filterwarnings('ignore')

app = Flask(__name__)
CORS(app)  # Allow React to call API

print("Loading data...")
movies = pd.read_csv('movies.csv')
ratings = pd.read_csv('ratings.csv')

# Initialize recommender
recommender = MovieRecommender(movies, ratings)

# API ENDPOINTS
@app.route('/')
def home():
    return jsonify({
        'message': '🎬 Movie Recommender API',
        'endpoints': {
            '/recommend': 'POST - Get recommendations',
            '/search': 'GET - Search movies',
            '/popular': 'GET - Get popular movies',
            '/user/<user_id>/history': 'GET - Get user history',
            '/health': 'GET - Check API health'
        }
    })

@app.route('/health')
def health():
    return jsonify({
        'status': 'healthy',
        'movies_count': len(movies),
        'ratings_count': len(ratings),
        'users_count': ratings['userId'].nunique()
    })

@app.route('/recommend', methods=['POST'])
def get_recommendations():
    """Get movie recommendations"""
    try:
        data = request.json
        user_id = data.get('user_id', 1)
        movie_title = data.get('movie_title', 'Toy Story (1995)')
        n = data.get('n_recommendations', 10)
        
        recommendations = recommender.hybrid_recommend(user_id, movie_title, n)
        
        if recommendations.empty:
            return jsonify({
                'success': False,
                'message': f'No recommendations found for "{movie_title}"'
            }), 404
        
        # Format for frontend
        rec_list = []
        for idx, row in recommendations.iterrows():
            rec_list.append({
                'title': row['title'],
                'genres': row.get('genres', 'Unknown'),
                'id': idx
            })
        
        # Get user's watch history
        watched_movies = []
        if user_id in recommender.user_movie_matrix.index:
            user_ratings = recommender.user_movie_matrix.loc[user_id]
            watched = user_ratings[user_ratings > 0].index.tolist()
            watched_movies = movies[movies['movieId'].isin(watched)]['title'].tolist()[:10]
        
        return jsonify({
            'success': True,
            'recommendations': rec_list,
            'user_id': user_id,
            'favorite_movie': movie_title,
            'watched_movies': watched_movies
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500

@app.route('/search')
def search_movies():
    """Search for movies by title"""
    query = request.args.get('q', '')
    limit = request.args.get('limit', 20, type=int)
    
    if len(query) < 2:
        return jsonify({
            'movies': [],
            'count': 0,
            'message': 'Search term too short (min 2 characters)'
        })
    
    results = movies[movies['title'].str.contains(query, case=False, na=False)]
    
    movie_list = []
    for idx, row in results.head(limit).iterrows():
        movie_list.append({
            'id': row['movieId'],
            'title': row['title'],
            'genres': row.get('genres', 'Unknown'),
            'year': row['title'].split('(')[-1].replace(')', '') if '(' in row['title'] else 'Unknown'
        })
    
    return jsonify({
        'movies': movie_list,
        'count': len(results),
        'query': query
    })

@app.route('/popular')
def get_popular_movies():
    """Get most popular movies"""
    n = request.args.get('n', 20, type=int)
    
    popular = ratings.groupby('movieId')['rating'].agg(['mean', 'count'])
    popular = popular[popular['count'] >= 10]  # At least 10 ratings
    popular = popular.sort_values('mean', ascending=False).head(n)
    
    popular_movies = movies[movies['movieId'].isin(popular.index)]
    popular_movies = popular_movies.merge(popular, on='movieId')
    popular_movies = popular_movies.sort_values('mean', ascending=False)
    
    movie_list = []
    for idx, row in popular_movies.iterrows():
        movie_list.append({
            'title': row['title'],
            'genres': row.get('genres', 'Unknown'),
            'rating': round(row['mean'], 2),
            'votes': int(row['count'])
        })
    
    return jsonify({
        'popular_movies': movie_list,
        'count': len(movie_list)
    })

@app.route('/user/<int:user_id>/history')
def get_user_history(user_id):
    """Get user's watched movies"""
    if user_id not in recommender.user_movie_matrix.index:
        return jsonify({
            'success': False,
            'message': f'User {user_id} not found'
        }), 404
    
    user_ratings = recommender.user_movie_matrix.loc[user_id]
    watched = user_ratings[user_ratings > 0].index.tolist()
    
    watched_movies = movies[movies['movieId'].isin(watched)]
    watched_movies = watched_movies.merge(
        ratings[ratings['userId'] == user_id][['movieId', 'rating']],
        on='movieId'
    )
    
    movie_list = []
    for idx, row in watched_movies.head(20).iterrows():
        movie_list.append({
            'title': row['title'],
            'genres': row.get('genres', 'Unknown'),
            'rating': row['rating']
        })
    
    return jsonify({
        'success': True,
        'user_id': user_id,
        'movies': movie_list,
        'total_watched': len(watched)
    })

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)