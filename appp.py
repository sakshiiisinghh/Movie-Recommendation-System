import streamlit as st
import pandas as pd
import pickle
import requests
import os

# ============================
# Load Data
# ============================
@st.cache_resource
def load_data():
    with open("movie_data.pkl", "rb") as f:
        movies, similarity = pickle.load(f)
    movies = movies.reset_index(drop=True)
    movies["title"] = movies["title"].astype(str).str.strip()
    return movies, similarity

movies, similarity = load_data()

# ============================
# Recommendation Engine
# ============================
def recommend(movie):
    movie = movie.strip()
    if movie not in movies["title"].values:
        st.error("Movie not found in database.")
        return []
    index = movies[movies["title"] == movie].index[0]
    distances = similarity[index]
    movie_list = sorted(list(enumerate(distances)), key=lambda x: x[1], reverse=True)[1:11]
    return [(movies.iloc[i].title, movies.iloc[i].movie_id) for i, _ in movie_list]

# ============================
# Fetch Poster Safely
# ============================
def fetch_poster(movie_id):
    # Try secrets.toml first
    api_key = None
    try:
        api_key = st.secrets["TMDB_API_KEY"]
    except Exception:
        pass
    
    # Fallback to environment variable
    if not api_key:
        api_key = os.getenv("TMDB_API_KEY")
    
    # If still missing, show placeholder
    if not api_key:
        return "https://via.placeholder.com/500x750?text=API+Key+Missing"
    
    try:
        url = f"https://api.themoviedb.org/3/movie/{movie_id}?api_key={api_key}"
        data = requests.get(url).json()
        poster = data.get("poster_path")
        if poster:
            return f"https://image.tmdb.org/t/p/w500{poster}"
        else:
            return "https://via.placeholder.com/500x750?text=No+Image"
    except:
        return "https://via.placeholder.com/500x750?text=Error"

# ============================
# Streamlit UI
# ============================
st.title("Movie Recommendation System")

selected_movie = st.selectbox("Select a Movie:", movies["title"].values)

if st.button("Recommend"):
    recs = recommend(selected_movie)
    if recs:
        st.subheader("Recommended Movies")
        # Display in two rows of 5 columns
        for i in range(0, len(recs), 5):
            cols = st.columns(5)
            for idx, (title, movie_id) in enumerate(recs[i:i+5]):
                with cols[idx]:
                    st.image(fetch_poster(movie_id), use_column_width=True)
                    st.caption(title)
