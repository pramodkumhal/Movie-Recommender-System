import streamlit as st
import pickle
import pandas as pd
import requests

# Fix Streamlit CORS warning on Render
st.set_page_config(page_title="Movie Recommender")

# Helper functions for Google Drive direct download
def get_confirm_token(response):
    for key, value in response.cookies.items():
        if key.startswith('download_warning'):
            return value
    return None

def load_pickle_from_gdrive(file_id):
    URL = "https://docs.google.com/uc?export=download"
    session = requests.Session()

    response = session.get(URL, params={'id': file_id}, stream=True)
    token = get_confirm_token(response)

    if token:
        params = {'id': file_id, 'confirm': token}
        response = session.get(URL, params=params, stream=True)

    content = response.content

    # Debug: check if content is HTML, which means not a raw pickle file
    if content.startswith(b'<'):
        st.error("Error: Downloaded content looks like an HTML page, not a pickle file. Check Google Drive sharing & file ID.")
        st.stop()  # stop app execution

    return pickle.loads(content)

# Your Google Drive file ID for similarity.pkl
file_id = '1KBJC5uqYZK0nTJQDRoY9ZIGJdQk3Oi-a'
similarity = load_pickle_from_gdrive(file_id)

# Function to fetch movie posters from TMDB API
def fetch_poster(movie_id):
    response = requests.get(
        f"https://api.themoviedb.org/3/movie/{movie_id}?api_key=a795623f41e9619b1a3a8aa65dfe92a0&language=en-US"
    )
    data = response.json()
    return "https://image.tmdb.org/t/p/w500/" + data['poster_path']

# Recommend function using similarity matrix
def recommend(movie):
    movie_index = movies[movies['title'] == movie].index[0]
    distances = similarity[movie_index]
    movie_list = sorted(list(enumerate(distances)), reverse=True, key=lambda x: x[1])[1:6]

    recommended_movies = []
    recommended_posters = []
    for i in movie_list:
        movie_id = movies.iloc[i[0]].movie_id
        recommended_movies.append(movies.iloc[i[0]].title)
        recommended_posters.append(fetch_poster(movie_id))
    return recommended_movies, recommended_posters

# Load movies dictionary from local pickle file (small file)
movies_dict = pickle.load(open('movie_dict.pkl', 'rb'))
movies = pd.DataFrame(movies_dict)

# Streamlit UI
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
