import React, { useState, useEffect } from "react";
import axios from "axios";
import "./App.css";
import { FaFilm, FaSearch, FaStar, FaUser } from "react-icons/fa";
import { BiSolidMoviePlay } from "react-icons/bi";
import { MdError } from "react-icons/md";

// Components
const API_BASE_URL = "http://localhost:5000";

function App() {
  const [loading, setLoading] = useState(false);
  const [recommendations, setRecommendations] = useState([]);
  const [searchResults, setSearchResults] = useState([]);
  const [popularMovies, setPopularMovies] = useState([]);
  const [watchedMovies, setWatchedMovies] = useState([]);
  const [error, setError] = useState(null);
  const [userInput, setUserInput] = useState({
    userId: 1,
    movieTitle: "Toy Story (1995)",
    numRecs: 10,
  });
  const [searchQuery, setSearchQuery] = useState("");
  const [showSearch, setShowSearch] = useState(false);
  const [currentView, setCurrentView] = useState("home"); // home, search, popular

  // Load popular movies on initial load
  useEffect(() => {
    fetchPopularMovies();
  }, []);

  const fetchPopularMovies = async () => {
    try {
      const response = await axios.get(`${API_BASE_URL}/popular?n=10`);
      if (response.data.popular_movies) {
        setPopularMovies(response.data.popular_movies);
      }
    } catch (err) {
      console.error("Error fetching popular movies:", err);
    }
  };

  const getRecommendations = async () => {
    setLoading(true);
    setError(null);
    setCurrentView("home");

    try {
      const response = await axios.post(`${API_BASE_URL}/recommend`, {
        user_id: userInput.userId,
        movie_title: userInput.movieTitle,
        n_recommendations: userInput.numRecs,
      });

      if (response.data.success) {
        setRecommendations(response.data.recommendations);
        setWatchedMovies(response.data.watched_movies || []);
        setError(null);
      } else {
        setError(response.data.message);
        setRecommendations([]);
      }
    } catch (err) {
      setError(err.response?.data?.message || "Failed to get recommendations");
      setRecommendations([]);
    }

    setLoading(false);
  };

  const searchMovies = async () => {
    if (searchQuery.length < 2) return;

    setLoading(true);
    setCurrentView("search");

    try {
      const response = await axios.get(
        `${API_BASE_URL}/search?q=${searchQuery}&limit=20`,
      );
      setSearchResults(response.data.movies || []);
      setError(null);
    } catch (err) {
      setError("Search failed");
      setSearchResults([]);
    }

    setLoading(false);
  };

  const handleRecommend = (e) => {
    e.preventDefault();
    getRecommendations();
  };

  const handleSearch = (e) => {
    e.preventDefault();
    searchMovies();
  };

  const handleMovieClick = (movieTitle) => {
    setUserInput({ ...userInput, movieTitle });
    setShowSearch(false);
  };

  return (
    <div className="App">
      {/* Navigation Bar */}
      <nav className="navbar">
        <div className="nav-container">
          <div className="nav-logo">
            <FaFilm className="logo-icon" />
            <span className="logo-text">MovieMate</span>
          </div>
          <div className="nav-links">
            <button onClick={() => setCurrentView("home")} className="nav-link">
              Home
            </button>
            <button
              onClick={() => setCurrentView("popular")}
              className="nav-link"
            >
              Popular
            </button>
          </div>
        </div>
      </nav>

      {/* Hero Section */}
      <header className="hero">
        <div className="hero-content">
          <h1 className="hero-title">
            <BiSolidMoviePlay />
            <span> Discover Your Next Favorite Movie</span>
          </h1>
          <p className="hero-subtitle">
            Personalized recommendations powered by AI
          </p>
        </div>
      </header>

      <div className="container">
        {/* User Input Section */}
        {currentView === "home" && (
          <>
            <div className="input-card">
              <form onSubmit={handleRecommend}>
                <div className="input-row">
                  <div className="input-group">
                    <label className="input-label">
                      <FaUser className="input-icon" />
                      User ID
                    </label>
                    <input
                      placeholder="Enter your user ID"
                      type="number"
                      className="input-field"
                      value={userInput.userId}
                      onChange={(e) =>
                        setUserInput({
                          ...userInput,
                          userId: parseInt(e.target.value),
                        })
                      }
                      min="1"
                    />
                  </div>
                  <div className="input-group">
                    <label className="input-label">
                      <FaStar className="input-icon" />
                      Favorite Movie
                    </label>
                    <input
                      type="text"
                      className="input-field"
                      value={userInput.movieTitle}
                      onChange={(e) =>
                        setUserInput({
                          ...userInput,
                          movieTitle: e.target.value,
                        })
                      }
                      placeholder="Enter a movie you like"
                    />
                  </div>
                  <div className="input-group">
                    <label className="input-label">
                      <FaSearch className="input-icon" />
                      Number of Recommendations
                    </label>
                    <select
                      className="input-field"
                      value={userInput.numRecs}
                      onChange={(e) =>
                        setUserInput({
                          ...userInput,
                          numRecs: parseInt(e.target.value),
                        })
                      }
                    >
                      <option value={5}>5</option>
                      <option value={10}>10</option>
                      <option value={20}>20</option>
                      <option value={50}>50</option>
                    </select>
                  </div>
                </div>
                <button
                  type="submit"
                  className="recommend-btn"
                  disabled={loading}
                >
                  {loading ? "Finding Movies..." : "Get Recommendations"}
                </button>
              </form>
            </div>

            {/* Error Display */}
            {error && (
              <div className="error-card">
                <span className="error-icon">
                  <MdError />
                </span>
                {error}
              </div>
            )}

            {/* Recommendations Display */}
            {recommendations.length > 0 && (
              <div className="results-section">
                <div className="section-header">
                  <h2>Your Personalized Recommendations</h2>
                  <span className="rec-count">
                    {recommendations.length} movies
                  </span>
                </div>
                <div className="movie-grid">
                  {recommendations.map((movie, index) => (
                    <MovieCard key={index} movie={movie} rank={index + 1} />
                  ))}
                </div>

                {watchedMovies.length > 0 && (
                  <div className="watched-section">
                    <h3>📺 Based on movies you've watched:</h3>
                    <div className="watched-tags">
                      {watchedMovies.slice(0, 10).map((title, idx) => (
                        <span key={idx} className="watched-tag">
                          {title}
                        </span>
                      ))}
                    </div>
                  </div>
                )}
              </div>
            )}
          </>
        )}

        {/* Popular Movies View */}
        {currentView === "popular" && (
          <div className="results-section">
            <div className="section-header">
              <h2>⭐ Popular Movies</h2>
              <span className="rec-count">Top rated</span>
            </div>
            <div className="movie-grid">
              {popularMovies.map((movie, index) => (
                <MovieCard key={index} movie={movie} rank={index + 1} />
              ))}
            </div>
          </div>
        )}
      </div>
    </div>
  );
}

// Movie Card Component
function MovieCard({ movie, rank }) {
  return (
    <div className="movie-card">
      <div className="movie-rank">#{rank}</div>
      <div className="movie-content">
        <h3 className="movie-title">{movie.title}</h3>
        <p className="movie-genres">{movie.genres}</p>
        {movie.rating && (
          <div className="movie-rating">
            <FaStar className="star-icon" />
            <span>{movie.rating}</span>
            <span className="movie-votes">({movie.votes || "0"} votes)</span>
          </div>
        )}
      </div>
    </div>
  );
}

export default App;
