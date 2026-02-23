import random

_MOVIE_CAST = {
    "Forrest Gump": ["Tom Hanks", "Robin Wright", "Gary Sinise"],
    "Titanic": ["Leonardo DiCaprio", "Kate Winslet", "Billy Zane"],
    "Inception": ["Leonardo DiCaprio", "Joseph Gordon-Levitt", "Elliot Page", "Tom Hardy"],
    "Fight Club": ["Brad Pitt", "Edward Norton", "Helena Bonham Carter"],
    "Iron Man": ["Robert Downey Jr.", "Gwyneth Paltrow", "Jeff Bridges"],
    "The Avengers": ["Robert Downey Jr.", "Scarlett Johansson", "Chris Evans", "Mark Ruffalo"],
    "Black Swan": ["Natalie Portman", "Mila Kunis", "Vincent Cassel"],
    "La La Land": ["Emma Stone", "Ryan Gosling", "John Legend"],
    "The Shawshank Redemption": ["Morgan Freeman", "Tim Robbins"],
}

_MOVIE_BOXOFFICE = {
    "Forrest Gump": 677,
    "Titanic": 2264,
    "Inception": 837,
    "Fight Club": 101,
    "Iron Man": 586,
    "The Avengers": 1519,
    "Black Swan": 329,
    "La La Land": 472,
    "The Shawshank Redemption": 73,
}

_ALL_ACTORS = sorted({a for cast in _MOVIE_CAST.values() for a in cast})

def get_random_actor_pair():
    a, b = random.sample(_ALL_ACTORS, 2)
    return a, b

def validate_movie(actor_name, movie_name):
    movie = (movie_name or "").strip()
    if movie not in _MOVIE_CAST:
        return False
    return actor_name in _MOVIE_CAST[movie]

def validate_actor(movie_name, actor_name):
    movie = (movie_name or "").strip()
    actor = (actor_name or "").strip()
    if movie not in _MOVIE_CAST:
        return False
    return actor in _MOVIE_CAST[movie]

def get_cast_by_movie(movie_name):
    movie = (movie_name or "").strip()
    return list(_MOVIE_CAST.get(movie, []))

def get_movie_boxoffice(movie_name):
    movie = (movie_name or "").strip()
    return int(_MOVIE_BOXOFFICE.get(movie, 0))

def get_optimal_steps(start_actor, end_actor):
    return random.randint(2, 6)

def get_optimal_min_boxoffice(start_actor, end_actor):
    return random.randint(300, 1500)