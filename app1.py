import streamlit as st
import pandas as pd
import requests
import pickle

# Load the processed data and similarity matrix
with open('movie_data.pkl', 'rb') as file:
    movies, cosine_sim = pickle.load(file)



def get_recommendations(title, cosine_sim=cosine_sim):
    idx = movies[movies['title'] == title].index[0]  # Find index of the selected movie
    sim_scores = list(enumerate(cosine_sim[idx]))  # Pair similarity scores with movie indices
    sim_scores = sorted(sim_scores, key=lambda x: x[1], reverse=True)  # Sort by similarity score
    sim_scores = sim_scores[1:11]  # Get top 10 similar movies (excluding the selected movie)
    movie_indices = [i[0] for i in sim_scores]  # Extract movie indices
    return movies['title'].iloc[movie_indices]  # Return movie titles


# Streamlit UI

st.title("Movie Recommendation System")

selected_movie = st.selectbox("Select a movie:", movies['title'].values)

if st.button('Recommend'):
    recommendations = get_recommendations(selected_movie)
    st.write("Top 10 recommended movies:")
    for movie_title in recommendations:
        st.write(movie_title)

