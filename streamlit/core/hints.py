from core.game_logic import (
    calculate_shortest_path,
    calculate_lowest_boxoffice_path,
)

def get_realtime_hint(mode, current_actor, target_actor, data):
    """
    Compute the optimal next step from the current actor to the target actor.

    Parameters
    ----------
    mode : str
        "normal" or "challenge"
    current_actor : str
        Actor ID where the player currently is.
    target_actor : str
        Target actor ID.
    data : dict
        game_data

    Returns
    -------
    (movie_title, actor_name) or (None, None)
    """

    # Choose correct algorithm
    if mode == "normal":
        result = calculate_shortest_path(current_actor, target_actor, data)

    elif mode == "challenge":
        result = calculate_lowest_boxoffice_path(current_actor, target_actor, data)

    else:
        return None, None

    # If no path
    if not result["is_successful"]:
        return None, None

    path = result["path"]

    if not path:
        return None, None

    movie_id, actor_id = path[0]

    movie_title = data["movies"][movie_id]["title"]
    actor_name = data["actors"][actor_id]["name"]

    return movie_title, actor_name