import streamlit as st
import pandas as pd
import pickle
import requests
import os
import gdown
from io import BytesIO
import numpy as np

# ----------------------------------------------------
# MUST BE THE FIRST STREAMLIT COMMAND
# ----------------------------------------------------
st.set_page_config(page_title="Movie Recommender", layout="wide")

# ----------------------------------------------------
# CONFIGURATION
# ----------------------------------------------------
DRIVE_FILE_ID = "1ZD-AZVUFChqqz05PQ8vWicxv1F7ybdhv"
DRIVE_URL = f"https://drive.google.com/uc?id={DRIVE_FILE_ID}"
LOCAL_PKL = "movie_data.pkl"   # preferred for Streamlit Cloud


# ----------------------------------------------------
# LOAD DATA (LOCAL FIRST, THEN DRIVE)
# ----------------------------------------------------
@st.cache_resource
def load_data():
    # Use local file if exists
    if os.path.exists(LOCAL_PKL):
        pkl_path = LOCAL_PKL
    else:
        tmp_path = "/tmp/movie_data.pkl"
        if not os.path.exists(tmp_path):
            gdown.download(DRIVE_URL, tmp_path, quiet=False)
        pkl_path = tmp_path

    # Load
    with open(pkl_path, "rb") as f:
        movies, similarity = pickle.load(f)

    movies = movies.reset_index(drop=True)
    movies["title"] = movies["title"].astype(str).str.strip()

    similarity = np.array(similarity)
    return movies, similarity


movies, similarity = load_data()


# ----------------------------------------------------
# RECOMMENDATION ENGINE
# ----------------------------------------------------
def recommend(movie, top_k=10):
    movie = movie.strip()
    if movie not in movies["title"].values:
        st.error("Movie not found in database.")
        return []
    idx = int(movies[movies["title"] == movie].index[0])
    distances = similarity[idx]

    candidates = sorted(
        list(enumerate(distances)),
        key=lambda x: x[1],
        reverse=True
    )[1: top_k + 1]

    return [(movies.iloc[i].title, int(movies.iloc[i].movie_id)) for i, _ in candidates]


# ----------------------------------------------------
# POSTER FETCHER
# ----------------------------------------------------
def fetch_poster(movie_id):
    api_key = None
    
    # Streamlit secrets preferred
    try:
        api_key = st.secrets["TMDB_API_KEY"]
    except Exception:
        pass

    if not api_key:
        api_key = os.getenv("TMDB_API_KEY")

    if not api_key:
        return "https://via.placeholder.com/500x750?text=No+API+Key"

    try:
        url = f"https://api.themoviedb.org/3/movie/{movie_id}?api_key={api_key}"
        data = requests.get(url, timeout=8).json()
        poster = data.get("poster_path")

        if poster:
            return f"https://image.tmdb.org/t/p/w500{poster}"
        return "https://via.placeholder.com/500x750?text=No+Image"
    except Exception:
        return "https://via.placeholder.com/500x750?text=Error"


# ----------------------------------------------------
# STREAMLIT UI
# ----------------------------------------------------
st.title("Movie Recommendation System")

col1, col2 = st.columns([3, 1])

with col1:
    selected_movie = st.selectbox("Select a Movie:", movies["title"].values)

with col2:
    st.write("### Controls")
    top_k = st.slider("Recommendations", 5, 20, 10)
    st.write("Using local movie_data.pkl if available.")

if st.button("Recommend"):
    recs = recommend(selected_movie, top_k=top_k)

    if recs:
        st.subheader("Recommended Movies")
        for i in range(0, len(recs), 5):
            cols = st.columns(5)
            for idx, (title, movie_id) in enumerate(recs[i:i + 5]):
                with cols[idx]:
                    st.image(fetch_poster(movie_id), use_column_width=True)
                    st.caption(title)
