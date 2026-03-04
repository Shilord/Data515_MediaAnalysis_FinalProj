"""
test_game_logic.py
==================
Unit tests for game_logic.py (Reel Connections game).

Covers:
  - get_random_actors
  - get_actor_names
  - get_movies_for_actor
  - get_actors_for_movie
  - _reconstruct_path
  - calculate_shortest_path
  - calculate_lowest_boxoffice_path
  - calculate_score_shortest
  - calculate_score_boxoffice
  - generate_game
  - check_player_solution

All tests use small, hand-crafted in-memory data dicts so that no
parquet files or pickle files are required.
"""

import unittest
from unittest.mock import patch

from game_logic import (
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
)

# ---------------------------------------------------------------------------
# Shared test fixtures
# ---------------------------------------------------------------------------

def make_simple_data() -> dict:
    """
    Return a minimal game data dict.

    Graph (actor → movie → actor):

        A1 --m1--> A2 --m2--> A3
                   |
                  m3
                   |
                   A4

    Box-office weights:  m1=10, m2=5, m3=100
    """
    return {
        "movies": {
            "m1": {"title": "Movie 1", "box_office": 10.0, "actor_ids": ["A1", "A2"]},
            "m2": {"title": "Movie 2", "box_office": 5.0,  "actor_ids": ["A2", "A3"]},
            "m3": {"title": "Movie 3", "box_office": 100.0, "actor_ids": ["A2", "A4"]},
        },
        "actors": {
            "A1": {"name": "Alice",   "movie_ids": ["m1"]},
            "A2": {"name": "Bob",     "movie_ids": ["m1", "m2", "m3"]},
            "A3": {"name": "Carol",   "movie_ids": ["m2"]},
            "A4": {"name": "Dave",    "movie_ids": ["m3"]},
        },
    }


def make_disconnected_data() -> dict:
    """
    Return a data dict where A1/A2 are in one component and A3/A4 in another.
    No path exists between the two components.
    """
    return {
        "movies": {
            "m1": {"title": "Movie 1", "box_office": 10.0, "actor_ids": ["A1", "A2"]},
            "m2": {"title": "Movie 2", "box_office": 20.0, "actor_ids": ["A3", "A4"]},
        },
        "actors": {
            "A1": {"name": "Alice", "movie_ids": ["m1"]},
            "A2": {"name": "Bob",   "movie_ids": ["m1"]},
            "A3": {"name": "Carol", "movie_ids": ["m2"]},
            "A4": {"name": "Dave",  "movie_ids": ["m2"]},
        },
    }


# ===========================================================================
# get_random_actors
# ===========================================================================

class TestGetRandomActors(unittest.TestCase):

    def test_returns_two_distinct_actors(self):
        """Two returned actor IDs should be distinct."""
        data = make_simple_data()
        start, target = get_random_actors(data)
        self.assertNotEqual(start, target)

    def test_returned_actors_are_in_dataset(self):
        """Both returned IDs should exist in the actors dict."""
        data = make_simple_data()
        start, target = get_random_actors(data)
        self.assertIn(start, data["actors"])
        self.assertIn(target, data["actors"])

    def test_returns_tuple_of_two_strings(self):
        """Return value should be a tuple of exactly two strings."""
        data = make_simple_data()
        result = get_random_actors(data)
        self.assertIsInstance(result, tuple)
        self.assertEqual(len(result), 2)
        self.assertIsInstance(result[0], str)
        self.assertIsInstance(result[1], str)

    def test_raises_value_error_with_fewer_than_two_actors(self):
        """Should raise ValueError when the dataset has only one actor."""
        data = {
            "movies": {"m1": {"title": "X", "box_office": 1.0, "actor_ids": ["A1"]}},
            "actors": {"A1": {"name": "Solo", "movie_ids": ["m1"]}},
        }
        with self.assertRaises(ValueError):
            get_random_actors(data)

    def test_raises_value_error_with_empty_actors(self):
        """Should raise ValueError when the dataset has no actors."""
        data = {"movies": {}, "actors": {}}
        with self.assertRaises(ValueError):
            get_random_actors(data)


# ===========================================================================
# get_actor_names
# ===========================================================================

class TestGetActorNames(unittest.TestCase):

    def test_returns_correct_names(self):
        """Should return the names matching the two IDs."""
        data = make_simple_data()
        names = get_actor_names(("A1", "A3"), data)
        self.assertEqual(names, ("Alice", "Carol"))

    def test_returns_tuple_of_two_strings(self):
        """Return value should be a tuple of exactly two strings."""
        data = make_simple_data()
        result = get_actor_names(("A1", "A2"), data)
        self.assertIsInstance(result, tuple)
        self.assertEqual(len(result), 2)

    def test_raises_key_error_for_unknown_actor(self):
        """Should raise KeyError when an actor ID is not in the dataset."""
        data = make_simple_data()
        with self.assertRaises(KeyError):
            get_actor_names(("A1", "UNKNOWN"), data)


# ===========================================================================
# get_movies_for_actor
# ===========================================================================

class TestGetMoviesForActor(unittest.TestCase):

    def test_returns_correct_movies(self):
        """Should return all movies associated with the given actor."""
        data = make_simple_data()
        result = get_movies_for_actor("A2", data)
        self.assertEqual(set(result.keys()), {"m1", "m2", "m3"})

    def test_returns_dict_of_id_to_title(self):
        """Values of the returned dict should be movie title strings."""
        data = make_simple_data()
        result = get_movies_for_actor("A1", data)
        self.assertIsInstance(result, dict)
        for title in result.values():
            self.assertIsInstance(title, str)

    def test_actor_with_single_movie(self):
        """An actor appearing in only one movie should return a single-entry dict."""
        data = make_simple_data()
        result = get_movies_for_actor("A1", data)
        self.assertEqual(result, {"m1": "Movie 1"})

    def test_raises_key_error_for_unknown_actor(self):
        """Should raise KeyError for an actor ID not in the dataset."""
        data = make_simple_data()
        with self.assertRaises(KeyError):
            get_movies_for_actor("UNKNOWN", data)

    def test_skips_movies_not_in_movies_dict(self):
        """Movie IDs referenced by an actor but absent from movies dict are ignored."""
        data = make_simple_data()
        data["actors"]["A1"]["movie_ids"].append("GHOST_MOVIE")
        result = get_movies_for_actor("A1", data)
        self.assertNotIn("GHOST_MOVIE", result)


# ===========================================================================
# get_actors_for_movie
# ===========================================================================

class TestGetActorsForMovie(unittest.TestCase):

    def test_returns_correct_actors(self):
        """Should return all actors associated with the given movie."""
        data = make_simple_data()
        result = get_actors_for_movie("m1", data)
        self.assertEqual(set(result.keys()), {"A1", "A2"})

    def test_returns_dict_of_id_to_name(self):
        """Values of the returned dict should be actor name strings."""
        data = make_simple_data()
        result = get_actors_for_movie("m1", data)
        self.assertIsInstance(result, dict)
        for name in result.values():
            self.assertIsInstance(name, str)

    def test_raises_key_error_for_unknown_movie(self):
        """Should raise KeyError for a movie ID not in the dataset."""
        data = make_simple_data()
        with self.assertRaises(KeyError):
            get_actors_for_movie("UNKNOWN", data)

    def test_skips_actors_not_in_actors_dict(self):
        """Actor IDs listed in a movie but absent from actors dict are ignored."""
        data = make_simple_data()
        data["movies"]["m1"]["actor_ids"].append("GHOST_ACTOR")
        result = get_actors_for_movie("m1", data)
        self.assertNotIn("GHOST_ACTOR", result)


# ===========================================================================
# _reconstruct_path  (internal helper)
# ===========================================================================

class TestReconstructPath(unittest.TestCase):
    """Tests for the internal BFS path-reconstruction helper."""

    def test_direct_connection(self):
        """A path where start and target share one movie should produce one step."""
        # A1 → (m1) → A2
        forward_parents = {"A1": None, "A2": ("m1", "A1")}
        backward_parents = {"A2": None}
        path = _reconstruct_path(forward_parents, backward_parents, "A2", "A1", "A2")
        self.assertEqual(path, [("m1", "A2")])

    def test_two_step_path(self):
        """A two-hop path should produce two (movie, actor) tuples in order."""
        # A1 → (m1) → A2 → (m2) → A3
        forward_parents = {"A1": None, "A2": ("m1", "A1")}
        backward_parents = {"A3": None, "A2": ("m2", "A3")}
        path = _reconstruct_path(forward_parents, backward_parents, "A2", "A1", "A3")
        self.assertEqual(path, [("m1", "A2"), ("m2", "A3")])

    def test_start_equals_meeting_point(self):
        """When start IS the meeting actor the forward segment should be empty."""
        forward_parents = {"A1": None}
        backward_parents = {"A1": ("m1", "A2"), "A2": None}
        path = _reconstruct_path(forward_parents, backward_parents, "A1", "A1", "A2")
        self.assertEqual(path, [("m1", "A2")])


# ===========================================================================
# calculate_shortest_path
# ===========================================================================

class TestCalculateShortestPath(unittest.TestCase):

    def test_same_start_and_target_returns_zero_steps(self):
        """Start == target should immediately return 0 steps and an empty path."""
        data = make_simple_data()
        result = calculate_shortest_path("A1", "A1", data)
        self.assertEqual(result["steps"], 0)
        self.assertEqual(result["path"], [])
        self.assertTrue(result["is_successful"])

    def test_direct_one_hop(self):
        """Actors sharing a movie should be reachable in 1 step."""
        data = make_simple_data()
        result = calculate_shortest_path("A1", "A2", data)
        self.assertTrue(result["is_successful"])
        self.assertEqual(result["steps"], 1)

    def test_two_hop_path(self):
        """A1→A3 requires two hops (A1→A2→A3)."""
        data = make_simple_data()
        result = calculate_shortest_path("A1", "A3", data)
        self.assertTrue(result["is_successful"])
        self.assertEqual(result["steps"], 2)

    def test_path_contains_correct_tuples(self):
        """Each step in the path should be a (movie_id, actor_id) tuple."""
        data = make_simple_data()
        result = calculate_shortest_path("A1", "A3", data)
        for step in result["path"]:
            self.assertIsInstance(step, tuple)
            self.assertEqual(len(step), 2)

    def test_path_ends_at_target(self):
        """The last step in the path should reference the target actor."""
        data = make_simple_data()
        result = calculate_shortest_path("A1", "A3", data)
        self.assertEqual(result["path"][-1][1], "A3")

    def test_no_path_returns_unsuccessful(self):
        """Disconnected actors should produce is_successful=False and steps=-1."""
        data = make_disconnected_data()
        result = calculate_shortest_path("A1", "A3", data)
        self.assertFalse(result["is_successful"])
        self.assertEqual(result["steps"], -1)
        self.assertEqual(result["path"], [])

    def test_steps_matches_path_length(self):
        """'steps' should always equal len('path')."""
        data = make_simple_data()
        result = calculate_shortest_path("A1", "A4", data)
        self.assertEqual(result["steps"], len(result["path"]))

    def test_symmetric_path_length(self):
        """Path length from A to B should equal path length from B to A."""
        data = make_simple_data()
        fwd = calculate_shortest_path("A1", "A3", data)
        rev = calculate_shortest_path("A3", "A1", data)
        self.assertEqual(fwd["steps"], rev["steps"])


# ===========================================================================
# calculate_lowest_boxoffice_path
# ===========================================================================

class TestCalculateLowestBoxofficePath(unittest.TestCase):

    def test_same_start_and_target(self):
        """Start == target should return 0.0 total box office and empty path."""
        data = make_simple_data()
        result = calculate_lowest_boxoffice_path("A1", "A1", data)
        self.assertEqual(result["total_box_office"], 0.0)
        self.assertEqual(result["path"], [])
        self.assertTrue(result["is_successful"])

    def test_direct_one_hop_cost(self):
        """A1→A2 via m1 should cost exactly m1's box office (10.0)."""
        data = make_simple_data()
        result = calculate_lowest_boxoffice_path("A1", "A2", data)
        self.assertTrue(result["is_successful"])
        self.assertAlmostEqual(result["total_box_office"], 10.0)

    def test_prefers_cheaper_path(self):
        """
        A1→A3 can go A1→(m1,10)→A2→(m2,5)→A3 = 15, which is cheaper than any
        path through m3 (100). The algorithm must find the 15.0 path.
        """
        data = make_simple_data()
        result = calculate_lowest_boxoffice_path("A1", "A3", data)
        self.assertTrue(result["is_successful"])
        self.assertAlmostEqual(result["total_box_office"], 15.0)

    def test_no_path_returns_unsuccessful(self):
        """Disconnected actors should return is_successful=False."""
        data = make_disconnected_data()
        result = calculate_lowest_boxoffice_path("A1", "A3", data)
        self.assertFalse(result["is_successful"])
        self.assertAlmostEqual(result["total_box_office"], -1.0)
        self.assertEqual(result["path"], [])

    def test_path_ends_at_target(self):
        """The last (movie_id, actor_id) step must reference the target actor."""
        data = make_simple_data()
        result = calculate_lowest_boxoffice_path("A1", "A3", data)
        self.assertEqual(result["path"][-1][1], "A3")

    def test_total_box_office_matches_path_movies(self):
        """Sum of box-office values along the returned path must equal total_box_office."""
        data = make_simple_data()
        result = calculate_lowest_boxoffice_path("A1", "A3", data)
        path_cost = sum(data["movies"][mid]["box_office"] for mid, _ in result["path"])
        self.assertAlmostEqual(result["total_box_office"], path_cost)


# ===========================================================================
# calculate_score_shortest
# ===========================================================================

class TestCalculateScoreShortest(unittest.TestCase):

    def test_perfect_score_when_equal_steps(self):
        """Player matching the optimal path should score exactly 100."""
        self.assertAlmostEqual(calculate_score_shortest(5, 5), 100.0)

    def test_score_decreases_with_extra_steps(self):
        """More player steps than optimal should produce a score below 100."""
        score = calculate_score_shortest(10, 5)
        self.assertAlmostEqual(score, 50.0)

    def test_score_formula(self):
        """Verify score = 100 * optimal / player."""
        self.assertAlmostEqual(calculate_score_shortest(4, 2), 50.0)
        self.assertAlmostEqual(calculate_score_shortest(2, 1), 50.0)
        self.assertAlmostEqual(calculate_score_shortest(3, 3), 100.0)

    def test_raises_value_error_for_zero_player_steps(self):
        """Zero player_steps is invalid and should raise ValueError."""
        with self.assertRaises(ValueError):
            calculate_score_shortest(0, 5)

    def test_raises_value_error_for_negative_player_steps(self):
        """Negative player_steps should raise ValueError."""
        with self.assertRaises(ValueError):
            calculate_score_shortest(-1, 5)

    def test_raises_value_error_for_zero_optimal_steps(self):
        """Zero optimal_steps is invalid and should raise ValueError."""
        with self.assertRaises(ValueError):
            calculate_score_shortest(5, 0)

    def test_raises_value_error_for_negative_optimal_steps(self):
        """Negative optimal_steps should raise ValueError."""
        with self.assertRaises(ValueError):
            calculate_score_shortest(5, -1)


# ===========================================================================
# calculate_score_boxoffice
# ===========================================================================

class TestCalculateScoreBoxoffice(unittest.TestCase):

    def test_perfect_score_when_equal_sums(self):
        """Player matching optimal box office should score exactly 100."""
        self.assertAlmostEqual(calculate_score_boxoffice(200.0, 200.0), 100.0)

    def test_score_decreases_with_higher_player_sum(self):
        """Higher player total than optimal should produce a score below 100."""
        score = calculate_score_boxoffice(400.0, 200.0)
        self.assertAlmostEqual(score, 50.0)

    def test_score_formula(self):
        """Verify score = 100 * optimal / player."""
        self.assertAlmostEqual(calculate_score_boxoffice(500.0, 250.0), 50.0)
        self.assertAlmostEqual(calculate_score_boxoffice(1000.0, 100.0), 10.0)

    def test_raises_value_error_for_zero_player_sum(self):
        """Zero player_sum is invalid and should raise ValueError."""
        with self.assertRaises(ValueError):
            calculate_score_boxoffice(0.0, 100.0)

    def test_raises_value_error_for_negative_player_sum(self):
        """Negative player_sum should raise ValueError."""
        with self.assertRaises(ValueError):
            calculate_score_boxoffice(-50.0, 100.0)

    def test_raises_value_error_for_negative_optimal_sum(self):
        """Negative optimal_sum should raise ValueError."""
        with self.assertRaises(ValueError):
            calculate_score_boxoffice(100.0, -1.0)

    def test_zero_optimal_sum_gives_zero_score(self):
        """An optimal sum of 0 (no movies to traverse) gives a score of 0."""
        score = calculate_score_boxoffice(100.0, 0.0)
        self.assertAlmostEqual(score, 0.0)


# ===========================================================================
# generate_game
# ===========================================================================

class TestGenerateGame(unittest.TestCase):

    def test_raises_value_error_for_invalid_mode(self):
        """An unrecognised game_mode string should raise ValueError."""
        data = make_simple_data()
        with self.assertRaises(ValueError):
            generate_game("invalid_mode", data)

    def test_shortest_mode_returns_expected_keys(self):
        """Result dict must contain all required keys for 'shortest' mode."""
        data = make_simple_data()
        # Pin get_random_actors so the test is deterministic
        with patch("game_logic.get_random_actors", return_value=("A1", "A3")):
            result = generate_game("shortest", data)

        required = {
            "game_mode", "start_actor_id", "start_actor_name",
            "target_actor_id", "target_actor_name", "optimal_path", "is_valid",
        }
        self.assertEqual(required, required & result.keys())

    def test_box_office_mode_returns_expected_keys(self):
        """Result dict must contain all required keys for 'box_office' mode."""
        data = make_simple_data()
        with patch("game_logic.get_random_actors", return_value=("A1", "A3")):
            result = generate_game("box_office", data)

        required = {
            "game_mode", "start_actor_id", "start_actor_name",
            "target_actor_id", "target_actor_name", "optimal_path", "is_valid",
        }
        self.assertEqual(required, required & result.keys())

    def test_game_mode_stored_correctly(self):
        """The returned dict's game_mode should match the argument."""
        data = make_simple_data()
        with patch("game_logic.get_random_actors", return_value=("A1", "A3")):
            result = generate_game("shortest", data)
        self.assertEqual(result["game_mode"], "shortest")

    def test_valid_game_has_is_valid_true(self):
        """A connected actor pair should produce is_valid=True."""
        data = make_simple_data()
        with patch("game_logic.get_random_actors", return_value=("A1", "A3")):
            result = generate_game("shortest", data)
        self.assertTrue(result["is_valid"])

    def test_actor_names_match_ids(self):
        """Returned names should correspond to the returned actor IDs."""
        data = make_simple_data()
        with patch("game_logic.get_random_actors", return_value=("A1", "A3")):
            result = generate_game("shortest", data)
        self.assertEqual(result["start_actor_name"],
                         data["actors"][result["start_actor_id"]]["name"])
        self.assertEqual(result["target_actor_name"],
                         data["actors"][result["target_actor_id"]]["name"])

    def test_disconnected_pair_eventually_sets_is_valid_false(self):
        """
        If every attempt returns an unsuccessful path, generate_game must
        return is_valid=False after exhausting all retries.
        """
        data = make_disconnected_data()
        # Always hand back a disconnected pair
        with patch("game_logic.get_random_actors", return_value=("A1", "A3")):
            result = generate_game("shortest", data)
        self.assertFalse(result["is_valid"])


# ===========================================================================
# check_player_solution
# ===========================================================================

class TestCheckPlayerSolution(unittest.TestCase):

    def test_correct_selection_returns_true(self):
        """Matching actor IDs should return True."""
        self.assertTrue(check_player_solution("A3", "A3"))

    def test_incorrect_selection_returns_false(self):
        """Non-matching actor IDs should return False."""
        self.assertFalse(check_player_solution("A1", "A3"))

    def test_case_sensitive(self):
        """Actor ID comparison should be case-sensitive."""
        self.assertFalse(check_player_solution("a3", "A3"))

    def test_empty_strings_match(self):
        """Two empty strings are equal, so the function should return True."""
        self.assertTrue(check_player_solution("", ""))

    def test_empty_vs_nonempty_returns_false(self):
        """An empty selection against a real ID should return False."""
        self.assertFalse(check_player_solution("", "A3"))


if __name__ == "__main__":
    unittest.main()
