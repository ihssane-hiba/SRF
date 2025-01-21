# -*- coding: utf-8 -*-
import pandas as pd
import numpy as np
from surprise import SVD, Dataset, Reader
from surprise.model_selection import cross_validate
import streamlit as st
import requests
from concurrent.futures import ThreadPoolExecutor

# Load custom CSS for styling
def load_css():
    st.markdown(
        """
        <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        body {
            background-color: #6A1B9A; /* Mauve theme for entire background */
            font-family: 'Arial', sans-serif;
            color: #FFFFFF;
        }
        .title {
            color: purple; /* Soft lavender for title */
            text-align: center;
            font-size: 2.5rem;
            font-weight: bold;
            margin-bottom: 20px;
            text-shadow: 2px 2px 4px rgba(0, 0, 0, 0.3);
        }
        .description {
            text-align: center;
            font-size: 1.2rem;
            color: #D1C4E9; /* Light purple */
            margin-bottom: 40px;
        }
        .poster-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 20px;
            padding: 20px;
        }
        .poster {
            text-align: center;
            border: 2px solid #9575CD; /* Light purple border */
            border-radius: 10px;
            overflow: hidden;
            background-color: #7E57C2; /* Deeper mauve */
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.3);
            transition: transform 0.3s ease, box-shadow 0.3s ease;
        }
        .poster:hover {
            transform: scale(1.05);
            box-shadow: 0 6px 10px rgba(0, 0, 0, 0.5);
        }
        .poster img {
            width: 100%;
            height: auto;
            border-bottom: 2px solid #9575CD;
        }
        .poster-title {
            font-size: 1rem;
            font-weight: bold;
            margin-top: 10px;
            margin-bottom: 10px;
            color: #FFFFFF;
        }
        input[type="text"] {
            width: 100%;
            padding: 10px;
            border-radius: 5px;
            border: none;
            outline: none;
            font-size: 1rem;
            color: #6A1B9A;
            background-color: #F3E5F5; /* Soft lavender input background */
            box-shadow: 0 2px 4px rgba(0, 0, 0, 0.2);
        }
        input[type="text"]:focus {
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.4);
        }
        </style>
        """,
        unsafe_allow_html=True,
    )

# Function to fetch movie poster with error handling
def fetch_poster(movie_id):
    try:
        url = f"https://api.themoviedb.org/3/movie/{movie_id}?api_key=8265bd1679663a7ea12ac168da84d2e8&language=en-US"
        data = requests.get(url).json()

        # Retrieve the poster and title, with defaults in case of missing values
        poster_path = data.get('poster_path', None)
        title = data.get('title', "Title not available")  # Default title if missing

        # If a poster path is found, return the full URL
        if poster_path:
            poster_url = f"https://image.tmdb.org/t/p/w500/{poster_path}"
        else:
            poster_url = None  # No poster if not found

        return poster_url, title
    except Exception as e:
        # Return None for both poster and title in case of an error
        return None, None

# Function to fetch movies with posters and handle missing data
@st.cache_data
def get_movies_with_posters(genre, limit=8):
    filtered_movies = movies[movies['genres'].str.contains(genre, case=False, na=False)].head(limit)
    movie_list = []

    # Fetch movie data and ignore those without posters
    with ThreadPoolExecutor() as executor:
        for movie in filtered_movies.iterrows():
            poster_url, title = fetch_movie_data(movie[1])
            if poster_url:  # Only append movies with valid posters
                movie_list.append({"title": title, "poster": poster_url})

    return movie_list

def fetch_movie_data(movie_row):
    poster_url, title = fetch_poster(movie_row['movie_id'])
    return poster_url, title

# Load data from CSV
@st.cache_data
def load_data():
    movies = pd.read_csv('movies.dat', sep='::', engine='python', encoding='ISO-8859-1',
                         names=['movie_id', 'title', 'genres'], dtype={'movie_id': int, 'title': str, 'genres': str})
    return movies

movies = load_data()

# Streamlit app
load_css()

# App Header
st.markdown("<h1 class='title'>🎥 Recommender System</h1>", unsafe_allow_html=True)
st.markdown("<p class='description'>Search for movies by genre and view their posters below!</p>", unsafe_allow_html=True)

# User input for genre
genre_input = st.text_input("Enter a genre (e.g., Action, Comedy, Drama)")

# Fetch and display movies based on user input
if genre_input:
    with st.spinner("Fetching movies..."):
        genre_movies_with_posters = get_movies_with_posters(genre_input, limit=8)
        if genre_movies_with_posters:
            st.markdown(f"<h2 class='title'>Movies in {genre_input}</h2>", unsafe_allow_html=True)
            st.markdown("<div class='poster-grid'>", unsafe_allow_html=True)
            for movie in genre_movies_with_posters:
                # Display movie poster and title
                st.markdown(
                    f"""
                    <div class='poster'>
                        <img src='{movie['poster']}' alt='{movie['title']}'>
                        <div class='poster-title'>{movie['title']}</div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )
            st.markdown("</div>", unsafe_allow_html=True)
        else:
            st.markdown("<p class='description'>No movies with posters available for this genre.</p>", unsafe_allow_html=True)
