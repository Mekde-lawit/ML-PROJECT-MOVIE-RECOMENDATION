# 🎬 Movie Recommender System

A comprhensiive movie recommendation engine that combines content-based filtering and collaborative filtering to provide personalized movie suggestions. Built with Flask API backend and React frontend.

## 📋 Table of Contents

- [Overview](#overview)
- [Features](#features)

## 🌟 Overview

This system uses a hybrid recommendation approach combining:

- **Content-Based Filtering**: Recommends movies similar to what a user likes based on genres and features
- **Collaborative Filtering**: Finds users with similar taste patterns and recommends movies they liked
- **Hybrid Approach**: Combines both methods for more accurate and diverse recommendations


## ✨ Features

### Backend (Flask API)

- ✅ RESTful API endpoints for recommendations
- ✅ Hybrid recommendation engine
- ✅ User-based collaborative filtering with KNN
- ✅ Content-based filtering with TF-IDF and cosine similarity
- ✅ K-Means clustering for user segmentation
- ✅ Fallback to popular movies for new users
- ✅ CORS support for frontend integration
- ✅ Input validation and error handling

### Frontend (React)

- ✅ Modern, responsive UI
- ✅ Search for movies by title ad userId
- ✅ View personalized recommendations
- ✅ Interactive movie cards
- ✅ Loading states and error handling

