import requests
from flask import Flask, render_template

app = Flask(__name__)

def fetch_poster(movie_id):
    url = f"https://api.themoviedb.org/3/movie/{movie_id}?api_key=8265bd1679663a7ea12ac168da84d2e8&language=en-US"
    response = requests.get(url)
    data = response.json()
    poster_path = data.get('poster_path')
    if poster_path:
        return f"https://image.tmdb.org/t/p/w500/{poster_path}"
    return "https://via.placeholder.com/150"  # Image par défaut

@app.route('/')
def home():
    # Exemple d'IDs de films
    movies = [
        {"id": 27205, "title": "Inception"},      # Inception
        {"id": 603, "title": "The Matrix"},       # The Matrix
        {"id": 157336, "title": "Interstellar"}  # Interstellar
    ]

    # Ajouter les posters pour chaque film
    for movie in movies:
        movie['poster'] = fetch_poster(movie['id'])

    return render_template('index.html', movies=movies)

if __name__ == '__main__':
    app.run(debug=True)
