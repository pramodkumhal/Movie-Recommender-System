import streamlit as st
import pickle
import pandas as pd
import requests

# --- Load similarity.pkl from Google Drive ---
def load_similarity_from_drive(file_id):
    url = f'https://drive.google.com/uc?id={file_id}'
    response = requests.get(url)
    return pickle.loads(response.content)

# ✅ Google Drive File ID (your actual file)
file_id = '1KBJC5uqYZK0nTJQDRoY9ZIGJdQk3Oi-a'
similarity = load_similarity_from_drive(file_id)

# --- Fetch movie poster from TMDB ---
def fetch_poster(movie_id):
    response = requests.get(
        f"https://api.themoviedb.org/3/movie/{movie_id}?api_key=a795623f41e9619b1a3a8aa65dfe92a0&language=en-US"
    )
    data = response.json()
    return "https://image.tmdb.org/t/p/w500/" + data['poster_path']

# --- Recommend similar movies ---
def recommend(movie):
    movie_index = movies[movies['title'] == movie].index[0]
    distances = similarity[movie_index]
    movie_list = sorted(
        list(enumerate(distances)), reverse=True, key=lambda x: x[1]
    )[1:6]

    recommended_movies = []
    recommended_posters = []
    for i in movie_list:
        movie_id = movies.iloc[i[0]].movie_id
        recommended_movies.append(movies.iloc[i[0]].title)
        recommended_posters.append(fetch_poster(movie_id))
    return recommended_movies, recommended_posters

# --- Load movies data (local file) ---
movies_dict = pickle.load(open('movie_dict.pkl', 'rb'))
movies = pd.DataFrame(movies_dict)

# --- Streamlit UI ---
st.title("🎬 Movie Recommender System")

selected_movie_name = st.selectbox(
    "Select a movie you like:",
    movies['title'].values
)

if st.button("Recommend"):
    names, posters = recommend(selected_movie_name)

    cols = st.columns(5)
    for i in range(5):
        with cols[i]:
            st.text(names[i])
            st.image(posters[i])
