"""
game_logic.py
=============
Core Python functions for the Reel Connections game.

This includes processing the raw data into efficient nested dictionaries, loading that data,
selecting random actors, retrieving movies/actors for a given actor/movie, calculating optimal
paths for both game, and scoring player solutions.

Saved/cached format
-------------------
game_data.pkl   – Python dict with keys:
    "movies"  : {movie_id: {"title": str, "box_office": float, "actor_ids": list}}
    "actors"  : {actor_id: {"name": str, "movie_ids": list}}
"""

import pickle
import random
import heapq
from collections import deque
from pathlib import Path
from typing import Optional

import pandas as pd

# ---------------------------------------------------------------------------
# 1. Build and pickle nested dictionaries from parquet files
# ---------------------------------------------------------------------------

# 16/15 local variables, mostly because of the nested loops and
# multiple dicts being built simultaneously.
# Could be refactored but it's not too bad and is clearer to keep it all in one function.
# pylint: disable=too-many-locals
def build_and_save(
    movies_parquet: str,
    actors_parquet: str,
    output_path: str = "game_data.pkl",
) -> dict:
    """
    Read parquet files, restructure them into nested dicts, and saves as file.

    Parameters
    ----------
    movies_parquet : str
        Path to movies.parquet.
    actors_parquet : str
        Path to actors.parquet.
    output_path : str
        Destination path for the pickled data (default: "game_data.pkl").

    Returns
    -------
    dict
        The structured game data that was saved.
    """
    movies_df = pd.read_parquet(movies_parquet)
    actors_df = pd.read_parquet(actors_parquet)

    # Build movie dict and simultaneously collect movie_ids per actor
    actor_to_movies: dict = {}  # nconst -> [tconst, ...]

    movies: dict = {}
    for _, row in movies_df.iterrows():
        year_str = f" ({int(row['startYear'])})" if pd.notna(row['startYear']) else ""
        title = f"{row['originalTitle']}{year_str}"

        actor_ids = [aid.strip() for aid in str(row["personIds"]).split(",") if aid.strip()]

        movies[row["tconst"]] = {
            "title": title,
            "box_office":
            float(row["adjusted_box_office"]) if row["adjusted_box_office"] is not None else 0.0,
            "actor_ids": actor_ids,
        }

        # Invert the relationship: track which movies each actor appears in
        for actor_id in actor_ids:
            actor_to_movies.setdefault(actor_id, []).append(row["tconst"])

    # Remove this chunk to include all movies even with no box office sales info (0 sales)
    # Remove movies with zero or missing box office values
    removed_movies = {mid for mid, info in movies.items() if info["box_office"] == 0.0}
    movies = {mid: info for mid, info in movies.items() if mid not in removed_movies}
    # Remove references to filtered movies from actor_to_movies
    for actor_id in actor_to_movies:
        actor_to_movies[actor_id] = [mid for mid in actor_to_movies[actor_id]
                                     if mid not in removed_movies]

    actors: dict = {}
    for _, row in actors_df.iterrows():
        actors[row["nconst"]] = {
            "name": row["primaryName"],
            "movie_ids": actor_to_movies.get(row["nconst"], []),
        }
    # Remove actors with no associated movies
    actors = {nconst: info for nconst, info in actors.items() if info["movie_ids"]}

    data = {"movies": movies, "actors": actors}

    with open(output_path, "wb") as f:
        pickle.dump(data, f, protocol=pickle.HIGHEST_PROTOCOL)

    print(f"[build_and_save] Saved {len(movies)} movies and {len(actors)} actors → {output_path}")
    return data

# ---------------------------------------------------------------------------
# 2. Load the pre-built pickled nested dictionaries
# ---------------------------------------------------------------------------

def load_data(path: str = "game_data.pkl") -> dict:
    """
    Load game data from a pickled file.

    Parameters
    ----------
    path : str
        Path to the pickled file created by build_and_save().

    Returns
    -------
    dict
        {"movies": {...}, "actors": {...}}
    """
    if not Path(path).exists():
        raise FileNotFoundError(
            f"Game data file '{path}' not found. "
            "Run build_and_save() first to generate it."
        )

    with open(path, "rb") as f:
        data = pickle.load(f)
    return data

# ---------------------------------------------------------------------------
# 3. Select random starting and target actors
# ---------------------------------------------------------------------------

def get_random_actors(data: dict) -> tuple[str, str]:
    """
    Return two distinct, randomly chosen actor IDs.

    Parameters
    ----------
    data : dict
        Game data from load_data() or build_and_save().

    Returns
    -------
    (start_actor_id, target_actor_id) : tuple[str, str]
    """
    actor_ids = list(data["actors"].keys())
    if len(actor_ids) < 2:
        raise ValueError("Need at least 2 actors in the dataset.")

    start, target = random.sample(actor_ids, 2)
    return start, target

# Not actually needed if you access the names when generating the game with generate_game(),
# since that function already returns the names along with the IDs,
# but could be useful for other parts of the UI or debugging.
def get_actor_names(actor_ids: tuple, data: dict) -> tuple[str, str]:
    """
    Return the full names of two actors given their IDs.

    Parameters
    ----------
    actor_ids : tuple
        A (start_actor_id, target_actor_id) tuple as returned by get_random_actors().
    data : dict
        Game data from load_data() or build_and_save().

    Returns
    -------
    (start_actor_name, target_actor_name) : tuple[str, str]
    """
    return (
        data["actors"][actor_ids[0]]["name"],
        data["actors"][actor_ids[1]]["name"]
    )

# ---------------------------------------------------------------------------
# 4. Get all movies for an actor
# ---------------------------------------------------------------------------

# For Streamlit:
# The user selects based on a formatted string (movie title),
# but will actually be selecting an ID. So something like:
# selected_id = st.selectbox(
#     "Choose an movie:",
#     options=list(movies.keys()),
#     format_func=lambda x: f"{movies[x]['title']} ({movies[x]['year']})"
# )

def get_movies_for_actor(actor_id: str, data: dict) -> dict:
    """
    Return a dict of {movie_id: title} for every movie an actor appears in.

    Parameters
    ----------
    actor_id : str
    data : dict

    Returns
    -------
    dict  {movie_id: title}
    """
    if actor_id not in data["actors"]:
        raise KeyError(f"Actor ID '{actor_id}' not found.")

    movies_lookup = data["movies"]
    return {
        mid: movies_lookup[mid]["title"]
        for mid in data["actors"][actor_id]["movie_ids"]
        if mid in movies_lookup
    }

# ---------------------------------------------------------------------------
# 5. Get all actors for a movie
# ---------------------------------------------------------------------------

# For Streamlit:
# The user selects based on a formatted string (movie title),
# but will actually be selecting an ID. So something like:
# selected_id = st.selectbox(
#     "Choose an actor:",
#     options=list(actors.keys()),
#     format_func=lambda x: f"{actors[x]['name']} ({actors[x]['year']})"
# )

def get_actors_for_movie(movie_id: str, data: dict) -> dict:
    """
    Return a dict of {actor_id: actor_name} for every actor in a movie.

    Parameters
    ----------
    movie_id : str
    data : dict

    Returns
    -------
    dict  {actor_id: actor_name}
    """
    if movie_id not in data["movies"]:
        raise KeyError(f"Movie ID '{movie_id}' not found.")

    actors_lookup = data["actors"]
    return {
        aid: actors_lookup[aid]["name"]
        for aid in data["movies"][movie_id]["actor_ids"]
        if aid in actors_lookup
    }

# ---------------------------------------------------------------------------
# 6. Optimal shortest path – bidirectional BFS
# ---------------------------------------------------------------------------

def _reconstruct_path(
    forward_parents: dict,
    backward_parents: dict,
    meeting_actor: str,
    start: str,
    target: str,
) -> list:
    """
    Reconstruct the full ordered path of (movie_id, actor_id) pairs from the
    bidirectional BFS parent maps.

    Each "step" is a (movie_id, actor_id) tuple representing choosing that
    movie and then that actor. The starting actor itself is not a step.
    """
    # Build forward segment: start → meeting_actor
    forward_steps: list = []
    node = meeting_actor
    while node != start:
        movie_id, parent = forward_parents[node]
        forward_steps.append((movie_id, node))
        node = parent
    forward_steps.reverse()

    # Build backward segment: meeting_actor → target
    backward_steps: list = []
    node = meeting_actor
    while node != target:
        movie_id, child = backward_parents[node]
        backward_steps.append((movie_id, child))
        node = child

    return forward_steps + backward_steps


def calculate_shortest_path(start: str, target: str, data: dict) -> dict:
    """
    Bidirectional BFS to find the path with the fewest (movie, actor) steps.

    Parameters
    ----------
    start  : str  Actor ID of starting actor.
    target : str  Actor ID of target actor.
    data   : dict Game data.

    Returns
    -------
    dict with keys:
        "steps"       : int   - number of (movie, actor) selections.
        "path"        : list  - ordered list of (movie_id, actor_id) tuples.
        "is_successful": bool - True if a path exists, False if no path exists between the actors.
    """
    if start == target:
        return {"steps": 0, "path": [], "is_successful": True}

    actors = data["actors"]
    movies = data["movies"]

    # forward_parents[actor] = (via_movie, parent_actor)
    forward_parents: dict = {start: None}
    # backward_parents[actor] = (via_movie, child_actor)
    backward_parents: dict = {target: None}

    forward_queue: deque = deque([start])
    backward_queue: deque = deque([target])
    forward_visited: set = {start}
    backward_visited: set = {target}

    def expand_forward(queue, f_visited, f_parents, b_visited) -> Optional[str]:
        actor = queue.popleft()
        for mid in actors.get(actor, {}).get("movie_ids", []):
            for neighbor in movies.get(mid, {}).get("actor_ids", []):
                if neighbor not in f_visited:
                    f_visited.add(neighbor)
                    f_parents[neighbor] = (mid, actor)
                    queue.append(neighbor)
                if neighbor in b_visited:
                    return neighbor  # meeting point found
        return None

    def expand_backward(queue, b_visited, b_parents, f_visited) -> Optional[str]:
        actor = queue.popleft()
        for mid in actors.get(actor, {}).get("movie_ids", []):
            for neighbor in movies.get(mid, {}).get("actor_ids", []):
                if neighbor not in b_visited:
                    b_visited.add(neighbor)
                    b_parents[neighbor] = (mid, actor)
                    queue.append(neighbor)
                if neighbor in f_visited:
                    return neighbor
        return None

    while forward_queue or backward_queue:
        # Expand whichever direction is smaller
        if forward_queue and (not backward_queue or len(forward_queue) <= len(backward_queue)):
            if forward_queue:
                meeting = expand_forward(forward_queue, forward_visited,
                                         forward_parents, backward_visited)
                if meeting is not None:
                    path = _reconstruct_path(forward_parents, backward_parents,
                                             meeting, start, target)
                    return {"steps": len(path), "path": path, "is_successful": True}
        if backward_queue:
            meeting = expand_backward(backward_queue, backward_visited,
                                      backward_parents, forward_visited)
            if meeting is not None:
                path = _reconstruct_path(forward_parents, backward_parents, meeting, start, target)
                return {"steps": len(path), "path": path, "is_successful": True}

    return {"steps": -1, "path": [], "is_successful": False}

# ---------------------------------------------------------------------------
# 7. Optimal lowest box-office path – bidirectional Dijkstra's
# ---------------------------------------------------------------------------

# This is a complex function wih many statements, but it makes sense to keep it all
# together for clarity since the forward and backward relaxations are so intertwined.
# Refactoring would likely just move code around without reducing the overall complexity much.
# pylint: disable=too-many-statements
def calculate_lowest_boxoffice_path(start: str, target: str, data: dict) -> dict:
    """
    Bidirectional Dijkstra's to find the path with the lowest total
    box-office sales across all chosen movies.

    The edge weight between two actors is the box-office revenue of the
    movie connecting them.

    Parameters
    ----------
    start  : str  Actor ID of starting actor.
    target : str  Actor ID of target actor.
    data   : dict Game data.

    Returns
    -------
    dict with keys:
        "total_box_office" : float - sum of box office sales along optimal path.
        "path"             : list  - ordered list of (movie_id, actor_id) tuples.
        "is_successful"    : bool  - True if a path exists, false otherwise.
    """
    if start == target:
        return {"total_box_office": 0.0, "path": [], "is_successful": True}

    actors = data["actors"]
    movies = data["movies"]

    # dist_f[actor] = best cost from start so far
    dist_f: dict = {start: 0.0}
    dist_b: dict = {target: 0.0}

    # parents: actor -> (via_movie, parent_actor)
    fwd_parents: dict = {start: None}
    bwd_parents: dict = {target: None}

    # heaps: (cost, actor_id)
    heap_f = [(0.0, start)]
    heap_b = [(0.0, target)]
    settled_f: set = set()
    settled_b: set = set()

    best_total = float("inf")
    meeting_node: str | None = None

    def relax_forward():
        nonlocal best_total, meeting_node
        cost, u = heapq.heappop(heap_f)
        if u in settled_f:
            return
        settled_f.add(u)
        for mid in actors.get(u, {}).get("movie_ids", []):
            w = movies.get(mid, {}).get("box_office", 0.0)
            for v in movies.get(mid, {}).get("actor_ids", []):
                if v == u:
                    continue
                new_cost = cost + w
                if new_cost < dist_f.get(v, float("inf")):
                    dist_f[v] = new_cost
                    fwd_parents[v] = (mid, u)
                    heapq.heappush(heap_f, (new_cost, v))
                # Check if this creates a complete path
                if v in dist_b:
                    candidate = new_cost + dist_b[v]
                    if candidate < best_total:
                        best_total = candidate
                        meeting_node = v

    def relax_backward():
        nonlocal best_total, meeting_node
        cost, u = heapq.heappop(heap_b)
        if u in settled_b:
            return
        settled_b.add(u)
        for mid in actors.get(u, {}).get("movie_ids", []):
            w = movies.get(mid, {}).get("box_office", 0.0)
            for v in movies.get(mid, {}).get("actor_ids", []):
                if v == u:
                    continue
                new_cost = cost + w
                if new_cost < dist_b.get(v, float("inf")):
                    dist_b[v] = new_cost
                    bwd_parents[v] = (mid, u)
                    heapq.heappush(heap_b, (new_cost, v))
                if v in dist_f:
                    candidate = dist_f[v] + new_cost
                    if candidate < best_total:
                        best_total = candidate
                        meeting_node = v

    while heap_f or heap_b:
        # Termination condition: minimum of both heaps exceeds best known path
        top_f = heap_f[0][0] if heap_f else float("inf")
        top_b = heap_b[0][0] if heap_b else float("inf")
        if top_f + top_b >= best_total:
            break

        if top_f <= top_b:
            if heap_f:
                relax_forward()
        else:
            if heap_b:
                relax_backward()

    if meeting_node is None or best_total == float("inf"):
        return {"total_box_office": -1.0, "path": [], "is_successful": False}

    path = _reconstruct_path(fwd_parents, bwd_parents, meeting_node, start, target)
    return {"total_box_office": best_total, "path": path, "is_successful": True}

# ---------------------------------------------------------------------------
# 8. Score calculation – shortest path mode
# ---------------------------------------------------------------------------

def calculate_score_shortest(player_steps: int, optimal_steps: int) -> float:
    """
    Score for the shortest-path game mode.

    score = 100 * optimal_steps / player_steps

    Parameters
    ----------
    player_steps  : int - Number of (movie, actor) selections the player made.
    optimal_steps : int - Optimal number of steps from the algorithm.

    Returns
    -------
    float  Score as a percentage (0-100).
    """
    if player_steps <= 0:
        raise ValueError("player_steps must be a positive integer.")
    if optimal_steps <= 0:
        raise ValueError("optimal_steps must be a positive integer.")

    return 100.0 * optimal_steps / player_steps

# ---------------------------------------------------------------------------
# 9. Score calculation – lowest box office mode
# ---------------------------------------------------------------------------

def calculate_score_boxoffice(player_sum: float, optimal_sum: float) -> float:
    """
    Score for the lowest-box-office game mode.

    score = 100 * optimal_sum / player_sum

    Parameters
    ----------
    player_sum  : float  - Sum of box office sales for the player's chosen movies.
    optimal_sum : float  - Optimal (minimum) sum from the algorithm.

    Returns
    -------
    float  Score as a percentage (0-100).
    """
    if player_sum <= 0:
        raise ValueError("player_sum must be a positive number.")
    if optimal_sum < 0:
        raise ValueError("optimal_sum cannot be negative.")

    return 100.0 * optimal_sum / player_sum

# ---------------------------------------------------------------------------
# 10. Generate a new game instance
# ---------------------------------------------------------------------------

def generate_game(game_mode: str, data: dict) -> dict:
    """
    Create a new game by selecting random start/target actors and pre-computing
    the optimal path for the chosen game mode.

    Parameters
    ----------
    game_mode : str
        "shortest"   – minimise number of (movie, actor) steps.
        "box_office"  – minimise total box office revenue across all chosen movies.
    data : dict
        Game data from load_data() or build_and_save().

    Returns
    -------
    dict with keys:
        "game_mode"        : str
        "start_actor_id"   : str
        "start_actor_name" : str
        "target_actor_id"  : str
        "target_actor_name": str
        "optimal_path"   : dict  (output of the relevant path algorithm)
        "is_valid"         : bool  (False if no path exists between the pair)

    Notes
    -----
    If no valid path is found the function retries with a new pair of actors
    (up to 20 attempts) before giving up and setting is_valid = False. This should
    not happen often given the size of the dataset, but it's a safeguard against edge cases.
    """
    supported_modes = {"shortest", "box_office"}
    if game_mode not in supported_modes:
        raise ValueError(f"game_mode must be one of {supported_modes}, got '{game_mode}'.")

    max_attempts = 20
    for _ in range(1, max_attempts + 1):
        start_id, target_id = get_random_actors(data)

        if game_mode == "shortest":
            result = calculate_shortest_path(start_id, target_id, data)
            success = result["is_successful"]
        elif game_mode == "box_office":
            result = calculate_lowest_boxoffice_path(start_id, target_id, data)
            success = result["is_successful"]
        else: # This should never happen due to the earlier check
            raise ValueError(f"Unsupported game mode: {game_mode}")

        if success:
            # print(f"Number of attempts: {_}") # For debugging
            return {
                "game_mode": game_mode,
                "start_actor_id": start_id,
                "start_actor_name": data["actors"][start_id]["name"],
                "target_actor_id": target_id,
                "target_actor_name": data["actors"][target_id]["name"],
                "optimal_path": result,
                "is_valid": True,
            }

    # All attempts failed
    # Have yet to decide what to do then – could return None or raise an exception,
    # but for now we'll return a dict with is_valid = False, and maybe reflect that
    # in the UI by showing a message and allowing the user to generate a new game.
    return {
        "game_mode": game_mode,
        "start_actor_id": start_id,
        "start_actor_name": data["actors"][start_id]["name"],
        "target_actor_id": target_id,
        "target_actor_name": data["actors"][target_id]["name"],
        "optimal_path": result,
        "is_valid": False,
    }

# ---------------------------------------------------------------------------
# 11. Check if player won
# ---------------------------------------------------------------------------

def check_player_solution(player_selection: str, target_actor_id: str) -> bool:
    """
    Check if the player's actor selection matches the target actor.

    Parameters
    ----------
    player_selection : str
        The actor ID selected by the player.
    target_actor_id : str
        The ID of the target actor in the current game.

    Returns
    -------
    bool       True if the player's selection matches the target actor (win), False otherwise.
    """
    if player_selection == target_actor_id:
        return True
    return False