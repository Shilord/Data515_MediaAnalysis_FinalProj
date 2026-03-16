"""
test_game_logic.py
==================
Unit tests for core/game_logic.py functions.

Run with:
    pytest test_game_logic.py -v
"""

import pickle


import pytest

from core.game_logic import (
    _reconstruct_path,
    calculate_lowest_boxoffice_path,
    calculate_score_boxoffice,
    calculate_score_shortest,
    calculate_shortest_path,
    check_player_solution,
    generate_game,
    get_actor_names,
    get_actors_for_movie,
    get_movies_for_actor,
    get_random_actors,
    load_data,
)

# ---------------------------------------------------------------------------
# Minimal in-memory dataset used across most tests
#
# Graph layout:
#
#   actor_A ──(movie_1)── actor_B ──(movie_2)── actor_C
#                              └──(movie_3)── actor_D
#   actor_E  (isolated – no movies)
#
# Box office values:
#   movie_1 = 100.0
#   movie_2 = 50.0
#   movie_3 = 200.0
# ---------------------------------------------------------------------------

SAMPLE_DATA = {
    "movies": {
        "movie_1": {"title": "Movie One (2000)", "box_office": 100.0, "actor_ids": ["actor_A", "actor_B"]},
        "movie_2": {"title": "Movie Two (2001)", "box_office": 50.0,  "actor_ids": ["actor_B", "actor_C"]},
        "movie_3": {"title": "Movie Three (2002)", "box_office": 200.0, "actor_ids": ["actor_B", "actor_D"]},
    },
    "actors": {
        "actor_A": {"name": "Alice",  "movie_ids": ["movie_1"]},
        "actor_B": {"name": "Bob",    "movie_ids": ["movie_1", "movie_2", "movie_3"]},
        "actor_C": {"name": "Carol",  "movie_ids": ["movie_2"]},
        "actor_D": {"name": "Dave",   "movie_ids": ["movie_3"]},
    },
}

# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture()
def data():
    return SAMPLE_DATA


@pytest.fixture()
def pkl_file(tmp_path):
    """Write SAMPLE_DATA to a temporary pickle file and return its path."""
    path = tmp_path / "game_data.pkl"
    with open(path, "wb") as f:
        pickle.dump(SAMPLE_DATA, f)
    return str(path)


# ===========================================================================
# load_data
# ===========================================================================

class TestLoadData:
    def test_loads_pickle_successfully(self, pkl_file):
        result = load_data(pkl_file)
        assert "movies" in result
        assert "actors" in result

    def test_loaded_data_matches_original(self, pkl_file):
        result = load_data(pkl_file)
        assert result["movies"]["movie_1"]["title"] == "Movie One (2000)"
        assert result["actors"]["actor_A"]["name"] == "Alice"

    def test_raises_file_not_found(self, tmp_path):
        with pytest.raises(FileNotFoundError):
            load_data(str(tmp_path / "nonexistent.pkl"))


# ===========================================================================
# get_random_actors
# ===========================================================================

class TestGetRandomActors:
    def test_returns_two_distinct_actors(self, data):
        start, target = get_random_actors(data)
        assert start != target

    def test_both_ids_in_data(self, data):
        start, target = get_random_actors(data)
        assert start in data["actors"]
        assert target in data["actors"]

    def test_raises_with_fewer_than_two_actors(self):
        tiny_data = {"actors": {"actor_A": {"name": "Alice", "movie_ids": []}}, "movies": {}}
        with pytest.raises(ValueError, match="at least 2 actors"):
            get_random_actors(tiny_data)

    def test_raises_with_empty_actors(self):
        empty_data = {"actors": {}, "movies": {}}
        with pytest.raises(ValueError):
            get_random_actors(empty_data)


# ===========================================================================
# get_actor_names
# ===========================================================================

class TestGetActorNames:
    def test_returns_correct_names(self, data):
        names = get_actor_names(("actor_A", "actor_C"), data)
        assert names == ("Alice", "Carol")

    def test_same_actor_both_positions(self, data):
        names = get_actor_names(("actor_B", "actor_B"), data)
        assert names == ("Bob", "Bob")


# ===========================================================================
# get_movies_for_actor
# ===========================================================================

class TestGetMoviesForActor:
    def test_returns_correct_movies(self, data):
        result = get_movies_for_actor("actor_B", data)
        assert set(result.keys()) == {"movie_1", "movie_2", "movie_3"}

    def test_titles_are_strings(self, data):
        result = get_movies_for_actor("actor_A", data)
        for title in result.values():
            assert isinstance(title, str)

    def test_actor_with_single_movie(self, data):
        result = get_movies_for_actor("actor_A", data)
        assert list(result.keys()) == ["movie_1"]

    def test_raises_for_unknown_actor(self, data):
        with pytest.raises(KeyError):
            get_movies_for_actor("actor_UNKNOWN", data)


# ===========================================================================
# get_actors_for_movie
# ===========================================================================

class TestGetActorsForMovie:
    def test_returns_correct_actors(self, data):
        result = get_actors_for_movie("movie_1", data)
        assert set(result.keys()) == {"actor_A", "actor_B"}

    def test_actor_names_are_strings(self, data):
        result = get_actors_for_movie("movie_2", data)
        for name in result.values():
            assert isinstance(name, str)

    def test_raises_for_unknown_movie(self, data):
        with pytest.raises(KeyError):
            get_actors_for_movie("movie_UNKNOWN", data)


# ===========================================================================
# _reconstruct_path
# ===========================================================================

class TestReconstructPath:
    def test_direct_path_single_step(self):
        # A --movie_1--> B
        forward_parents = {
            "actor_A": None,
            "actor_B": ("movie_1", "actor_A"),
        }
        backward_parents = {"actor_B": None}
        path = _reconstruct_path(forward_parents, backward_parents, "actor_B", "actor_A", "actor_B")
        assert path == [("movie_1", "actor_B")]

    def test_two_step_path(self):
        # A --m1--> B --m2--> C
        forward_parents = {
            "actor_A": None,
            "actor_B": ("movie_1", "actor_A"),
        }
        backward_parents = {
            "actor_C": None,
            "actor_B": ("movie_2", "actor_C"),
        }
        path = _reconstruct_path(forward_parents, backward_parents, "actor_B", "actor_A", "actor_C")
        assert path == [("movie_1", "actor_B"), ("movie_2", "actor_C")]

    def test_path_starts_with_correct_movie(self):
        forward_parents = {
            "actor_A": None,
            "actor_B": ("movie_1", "actor_A"),
        }
        backward_parents = {"actor_B": None}
        path = _reconstruct_path(forward_parents, backward_parents, "actor_B", "actor_A", "actor_B")
        assert path[0][0] == "movie_1"


# ===========================================================================
# calculate_shortest_path
# ===========================================================================

class TestCalculateShortestPath:
    def test_same_actor_zero_steps(self, data):
        result = calculate_shortest_path("actor_A", "actor_A", data)
        assert result["steps"] == 0
        assert result["path"] == []
        assert result["is_successful"] is True

    def test_direct_neighbours_one_step(self, data):
        result = calculate_shortest_path("actor_A", "actor_B", data)
        assert result["is_successful"] is True
        assert result["steps"] == 1
        assert result["path"] == [("movie_1", "actor_B")]

    def test_two_step_path(self, data):
        result = calculate_shortest_path("actor_A", "actor_C", data)
        assert result["is_successful"] is True
        assert result["steps"] == 2
        movie_ids = [step[0] for step in result["path"]]
        actor_ids = [step[1] for step in result["path"]]
        assert "movie_1" in movie_ids
        assert "movie_2" in movie_ids
        assert "actor_B" in actor_ids
        assert "actor_C" in actor_ids

    def test_path_ends_at_target(self, data):
        result = calculate_shortest_path("actor_A", "actor_D", data)
        assert result["path"][-1][1] == "actor_D"

    def test_no_path_returns_unsuccessful(self, data):
        # Add an isolated actor with no movies
        isolated_data = {
            "movies": dict(data["movies"]),
            "actors": {**data["actors"], "actor_Z": {"name": "Zara", "movie_ids": []}},
        }
        result = calculate_shortest_path("actor_A", "actor_Z", isolated_data)
        assert result["is_successful"] is False
        assert result["steps"] == -1
        assert result["path"] == []

    def test_path_length_matches_steps(self, data):
        result = calculate_shortest_path("actor_A", "actor_C", data)
        assert len(result["path"]) == result["steps"]

    def test_symmetric_path_lengths(self, data):
        """Shortest path A→C and C→A should have the same length."""
        forward = calculate_shortest_path("actor_A", "actor_C", data)
        backward = calculate_shortest_path("actor_C", "actor_A", data)
        assert forward["steps"] == backward["steps"]


# ===========================================================================
# calculate_lowest_boxoffice_path
# ===========================================================================

class TestCalculateLowestBoxofficePath:
    def test_same_actor_zero_cost(self, data):
        result = calculate_lowest_boxoffice_path("actor_A", "actor_A", data)
        assert result["total_box_office"] == 0.0
        assert result["is_successful"] is True

    def test_direct_path_cost(self, data):
        # actor_A → actor_B via movie_1 (cost 100)
        result = calculate_lowest_boxoffice_path("actor_A", "actor_B", data)
        assert result["is_successful"] is True
        assert result["total_box_office"] == 100.0

    def test_chooses_cheaper_path(self, data):
        # A → C: only path is A→B (100) → C (50) = 150 total
        # A → D: only path is A→B (100) → D (200) = 300 total
        result_c = calculate_lowest_boxoffice_path("actor_A", "actor_C", data)
        result_d = calculate_lowest_boxoffice_path("actor_A", "actor_D", data)
        assert result_c["total_box_office"] < result_d["total_box_office"]

    def test_no_path_returns_unsuccessful(self):
        isolated_data = {
            "movies": {"movie_1": {"title": "X", "box_office": 10.0, "actor_ids": ["a1", "a2"]}},
            "actors": {
                "a1": {"name": "Alpha", "movie_ids": ["movie_1"]},
                "a2": {"name": "Beta",  "movie_ids": ["movie_1"]},
                "a3": {"name": "Gamma", "movie_ids": []},
            },
        }
        result = calculate_lowest_boxoffice_path("a1", "a3", isolated_data)
        assert result["is_successful"] is False
        assert result["total_box_office"] == -1.0

    def test_path_last_actor_is_target(self, data):
        result = calculate_lowest_boxoffice_path("actor_A", "actor_C", data)
        assert result["path"][-1][1] == "actor_C"


# ===========================================================================
# calculate_score_shortest
# ===========================================================================

class TestCalculateScoreShortest:
    def test_perfect_score_when_equal(self):
        assert calculate_score_shortest(3, 3) == 100.0

    def test_half_score_for_double_steps(self):
        assert calculate_score_shortest(6, 3) == 50.0

    def test_score_above_100_if_player_beats_optimal(self):
        # This shouldn't happen in practice but the math still holds
        assert calculate_score_shortest(2, 4) == 200.0

    def test_raises_on_zero_player_steps(self):
        with pytest.raises(ValueError, match="player_steps"):
            calculate_score_shortest(0, 3)

    def test_raises_on_negative_player_steps(self):
        with pytest.raises(ValueError):
            calculate_score_shortest(-1, 3)

    def test_raises_on_zero_optimal_steps(self):
        with pytest.raises(ValueError, match="optimal_steps"):
            calculate_score_shortest(3, 0)

    def test_returns_float(self):
        result = calculate_score_shortest(4, 3)
        assert isinstance(result, float)


# ===========================================================================
# calculate_score_boxoffice
# ===========================================================================

class TestCalculateScoreBoxoffice:
    def test_perfect_score_when_equal(self):
        assert calculate_score_boxoffice(500.0, 500.0) == 100.0

    def test_half_score_for_double_spend(self):
        assert calculate_score_boxoffice(1000.0, 500.0) == 50.0

    def test_zero_optimal_gives_zero_score(self):
        assert calculate_score_boxoffice(500.0, 0.0) == 0.0

    def test_raises_on_zero_player_sum(self):
        with pytest.raises(ValueError, match="player_sum"):
            calculate_score_boxoffice(0.0, 100.0)

    def test_raises_on_negative_player_sum(self):
        with pytest.raises(ValueError):
            calculate_score_boxoffice(-10.0, 100.0)

    def test_raises_on_negative_optimal_sum(self):
        with pytest.raises(ValueError, match="optimal_sum"):
            calculate_score_boxoffice(100.0, -1.0)

    def test_returns_float(self):
        result = calculate_score_boxoffice(300.0, 200.0)
        assert isinstance(result, float)


# ===========================================================================
# check_player_solution
# ===========================================================================

class TestCheckPlayerSolution:
    def test_correct_selection_returns_true(self):
        assert check_player_solution("actor_C", "actor_C") is True

    def test_wrong_selection_returns_false(self):
        assert check_player_solution("actor_A", "actor_C") is False

    def test_empty_strings_match(self):
        assert check_player_solution("", "") is True

    def test_case_sensitive(self):
        assert check_player_solution("Actor_C", "actor_C") is False


# ===========================================================================
# generate_game
# ===========================================================================

class TestGenerateGame:
    def test_returns_required_keys_shortest(self, data):
        game = generate_game("shortest", data)
        for key in ("game_mode", "start_actor_id", "start_actor_name",
                    "target_actor_id", "target_actor_name", "optimal_path", "is_valid"):
            assert key in game

    def test_returns_required_keys_boxoffice(self, data):
        game = generate_game("box_office", data)
        for key in ("game_mode", "start_actor_id", "target_actor_id", "is_valid"):
            assert key in game

    def test_game_mode_is_recorded(self, data):
        game = generate_game("shortest", data)
        assert game["game_mode"] == "shortest"

    def test_start_and_target_differ(self, data):
        game = generate_game("shortest", data)
        if game["is_valid"]:
            assert game["start_actor_id"] != game["target_actor_id"]

    def test_actor_names_are_non_empty_strings(self, data):
        game = generate_game("shortest", data)
        assert isinstance(game["start_actor_name"], str) and game["start_actor_name"]
        assert isinstance(game["target_actor_name"], str) and game["target_actor_name"]

    def test_raises_on_invalid_game_mode(self, data):
        with pytest.raises(ValueError, match="game_mode"):
            generate_game("invalid_mode", data)

    def test_valid_game_has_successful_path(self, data):
        game = generate_game("shortest", data)
        if game["is_valid"]:
            assert game["optimal_path"]["is_successful"] is True

    def test_all_attempts_fail_returns_is_valid_false(self):
        """When every actor pair has no path, is_valid should be False."""
        disconnected_data = {
            "movies": {},
            "actors": {
                "a1": {"name": "Alpha", "movie_ids": []},
                "a2": {"name": "Beta",  "movie_ids": []},
            },
        }
        game = generate_game("shortest", disconnected_data)
        assert game["is_valid"] is False


# ===========================================================================
# Integration: round-trip path → score
# ===========================================================================

class TestIntegration:
    def test_optimal_path_scores_100_shortest(self, data):
        """Following the optimal path exactly should give score 100."""
        game = generate_game("shortest", data)
        if not game["is_valid"]:
            pytest.skip("No valid game generated for this dataset.")
        optimal_steps = game["optimal_path"]["steps"]
        score = calculate_score_shortest(optimal_steps, optimal_steps)
        assert score == 100.0

    def test_optimal_path_scores_100_boxoffice(self, data):
        game = generate_game("box_office", data)
        if not game["is_valid"]:
            pytest.skip("No valid game generated for this dataset.")
        optimal_bo = game["optimal_path"]["total_box_office"]
        if optimal_bo == 0.0:
            pytest.skip("Zero box office — division undefined.")
        score = calculate_score_boxoffice(optimal_bo, optimal_bo)
        assert score == 100.0

    def test_suboptimal_player_scores_below_100(self, data):
        result = calculate_shortest_path("actor_A", "actor_C", data)
        assert result["is_successful"]
        optimal = result["steps"]  # 2
        player_steps = optimal + 1   # simulate one extra step
        score = calculate_score_shortest(player_steps, optimal)
        assert score < 100.0

    def test_shortest_path_actor_chain_is_valid(self, data):
        """Every actor in the path should exist in the data."""
        result = calculate_shortest_path("actor_A", "actor_C", data)
        for _, actor_id in result["path"]:
            assert actor_id in data["actors"]

    def test_shortest_path_movie_chain_is_valid(self, data):
        """Every movie in the path should exist in the data."""
        result = calculate_shortest_path("actor_A", "actor_C", data)
        for movie_id, _ in result["path"]:
            assert movie_id in data["movies"]