import pickle

# Load game data
with open("data/game_data.pkl", "rb") as f:
    data = pickle.load(f)

actors = data["actors"]
movies = data["movies"]

# Find Brad Pitt
brad_id = None
for aid, info in actors.items():
    if info["name"] == "Brad Pitt":
        brad_id = aid
        break

if brad_id is None:
    print("Brad Pitt not found in dataset.")
else:
    movie_ids = actors[brad_id]["movie_ids"]
    print("Brad Pitt actor_id:", brad_id)
    print("Number of movies:", len(movie_ids))

    print("\nMovies:")
    for mid in movie_ids:
        if mid in movies:
            print("-", movies[mid]["title"])