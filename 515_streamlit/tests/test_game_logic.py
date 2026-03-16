"""
test_game_logic.py
==================
Unit tests for core/game_logic.py functions.

Run with:
    coverage run -m unittest discover -s tests -t tests
    coverage report
    coverage lcov
"""

import os
import pickle
import tempfile
import unittest

from core.game_logic import (
    _reconstruct_path,
    build_and_save,
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
# Minimal in-memory dataset used across all tests
#
# Graph layout:
#
#   actor_A ──(movie_1)── actor_B ──(movie_2)── actor_C
#                              └──(movie_3)── actor_D
#
# Box office values:
#   movie_1 = 100.0
#   movie_2 = 50.0
#   movie_3 = 200.0
# ---------------------------------------------------------------------------

SAMPLE_DATA = {
    "movies": {
        "movie_1": {
            "title": "Movie One (2000)",
            "box_office": 100.0,
            "actor_ids": ["actor_A", "actor_B"],
        },
        "movie_2": {
            "title": "Movie Two (2001)",
            "box_office": 50.0,
            "actor_ids": ["actor_B", "actor_C"],
        },
        "movie_3": {
            "title": "Movie Three (2002)",
            "box_office": 200.0,
            "actor_ids": ["actor_B", "actor_D"],
        },
    },
    "actors": {
        "actor_A": {"name": "Alice", "movie_ids": ["movie_1"]},
        "actor_B": {"name": "Bob",   "movie_ids": ["movie_1", "movie_2", "movie_3"]},
        "actor_C": {"name": "Carol", "movie_ids": ["movie_2"]},
        "actor_D": {"name": "Dave",  "movie_ids": ["movie_3"]},
    },
}


# ===========================================================================
# load_data
# ===========================================================================

class TestLoadData(unittest.TestCase):
    """Tests for the load_data function."""

    def setUp(self):
        """Write SAMPLE_DATA to a temp pickle file before each test."""
        self.tmp = tempfile.NamedTemporaryFile(  # pylint: disable=consider-using-with
            delete=False, suffix=".pkl"
        )
        pickle.dump(SAMPLE_DATA, self.tmp)
        self.tmp.close()

    def tearDown(self):
        """Remove the temp file after each test."""
        os.unlink(self.tmp.name)

    def test_loads_pickle_successfully(self):
        """Loaded dict should contain movies and actors keys."""
        result = load_data(self.tmp.name)
        self.assertIn("movies", result)
        self.assertIn("actors", result)

    def test_loaded_data_matches_original(self):
        """Loaded values should match what was pickled."""
        result = load_data(self.tmp.name)
        self.assertEqual(result["movies"]["movie_1"]["title"], "Movie One (2000)")
        self.assertEqual(result["actors"]["actor_A"]["name"], "Alice")

    def test_raises_file_not_found(self):
        """Should raise FileNotFoundError for a missing path."""
        with self.assertRaises(FileNotFoundError):
            load_data("/nonexistent/path/game_data.pkl")


# ===========================================================================
# get_random_actors
# ===========================================================================

class TestGetRandomActors(unittest.TestCase):
    """Tests for the get_random_actors function."""

    def test_returns_two_distinct_actors(self):
        """The two returned actor IDs should not be the same."""
        start, target = get_random_actors(SAMPLE_DATA)
        self.assertNotEqual(start, target)

    def test_both_ids_in_data(self):
        """Both returned IDs should exist in the actors dict."""
        start, target = get_random_actors(SAMPLE_DATA)
        self.assertIn(start, SAMPLE_DATA["actors"])
        self.assertIn(target, SAMPLE_DATA["actors"])

    def test_raises_with_fewer_than_two_actors(self):
        """Should raise ValueError when fewer than two actors exist."""
        tiny = {"actors": {"actor_A": {"name": "Alice", "movie_ids": []}}, "movies": {}}
        with self.assertRaises(ValueError):
            get_random_actors(tiny)

    def test_raises_with_empty_actors(self):
        """Should raise ValueError when the actors dict is empty."""
        empty = {"actors": {}, "movies": {}}
        with self.assertRaises(ValueError):
            get_random_actors(empty)


# ===========================================================================
# get_actor_names
# ===========================================================================

class TestGetActorNames(unittest.TestCase):
    """Tests for the get_actor_names function."""

    def test_returns_correct_names(self):
        """Should return the names matching the given actor IDs."""
        self.assertEqual(
            get_actor_names(("actor_A", "actor_C"), SAMPLE_DATA),
            ("Alice", "Carol")
        )

    def test_same_actor_both_positions(self):
        """Should return the same name twice when both IDs are identical."""
        self.assertEqual(
            get_actor_names(("actor_B", "actor_B"), SAMPLE_DATA),
            ("Bob", "Bob")
        )


# ===========================================================================
# get_movies_for_actor
# ===========================================================================

class TestGetMoviesForActor(unittest.TestCase):
    """Tests for the get_movies_for_actor function."""

    def test_returns_correct_movies(self):
        """Should return all movies associated with the given actor."""
        result = get_movies_for_actor("actor_B", SAMPLE_DATA)
        self.assertEqual(set(result.keys()), {"movie_1", "movie_2", "movie_3"})

    def test_titles_are_strings(self):
        """All returned movie titles should be strings."""
        result = get_movies_for_actor("actor_A", SAMPLE_DATA)
        for title in result.values():
            self.assertIsInstance(title, str)

    def test_actor_with_single_movie(self):
        """An actor with one movie should return exactly that movie."""
        result = get_movies_for_actor("actor_A", SAMPLE_DATA)
        self.assertEqual(list(result.keys()), ["movie_1"])

    def test_raises_for_unknown_actor(self):
        """Should raise KeyError for an actor ID not in the dataset."""
        with self.assertRaises(KeyError):
            get_movies_for_actor("actor_UNKNOWN", SAMPLE_DATA)


# ===========================================================================
# get_actors_for_movie
# ===========================================================================

class TestGetActorsForMovie(unittest.TestCase):
    """Tests for the get_actors_for_movie function."""

    def test_returns_correct_actors(self):
        """Should return all actors associated with the given movie."""
        result = get_actors_for_movie("movie_1", SAMPLE_DATA)
        self.assertEqual(set(result.keys()), {"actor_A", "actor_B"})

    def test_actor_names_are_strings(self):
        """All returned actor names should be strings."""
        result = get_actors_for_movie("movie_2", SAMPLE_DATA)
        for name in result.values():
            self.assertIsInstance(name, str)

    def test_raises_for_unknown_movie(self):
        """Should raise KeyError for a movie ID not in the dataset."""
        with self.assertRaises(KeyError):
            get_actors_for_movie("movie_UNKNOWN", SAMPLE_DATA)


# ===========================================================================
# _reconstruct_path
# ===========================================================================

class TestReconstructPath(unittest.TestCase):
    """Tests for the internal _reconstruct_path helper."""

    def test_direct_path_single_step(self):
        """A one-hop path should produce a single (movie, actor) tuple."""
        forward_parents = {
            "actor_A": None,
            "actor_B": ("movie_1", "actor_A"),
        }
        backward_parents = {"actor_B": None}
        path = _reconstruct_path(
            forward_parents, backward_parents, "actor_B", "actor_A", "actor_B"
        )
        self.assertEqual(path, [("movie_1", "actor_B")])

    def test_two_step_path(self):
        """A two-hop path should produce two (movie, actor) tuples in order."""
        forward_parents = {
            "actor_A": None,
            "actor_B": ("movie_1", "actor_A"),
        }
        backward_parents = {
            "actor_C": None,
            "actor_B": ("movie_2", "actor_C"),
        }
        path = _reconstruct_path(
            forward_parents, backward_parents, "actor_B", "actor_A", "actor_C"
        )
        self.assertEqual(path, [("movie_1", "actor_B"), ("movie_2", "actor_C")])

    def test_path_starts_with_correct_movie(self):
        """The first step should use the movie connecting start to the next actor."""
        forward_parents = {
            "actor_A": None,
            "actor_B": ("movie_1", "actor_A"),
        }
        backward_parents = {"actor_B": None}
        path = _reconstruct_path(
            forward_parents, backward_parents, "actor_B", "actor_A", "actor_B"
        )
        self.assertEqual(path[0][0], "movie_1")


# ===========================================================================
# calculate_shortest_path
# ===========================================================================

class TestCalculateShortestPath(unittest.TestCase):
    """Tests for the calculate_shortest_path function."""

    def test_same_actor_zero_steps(self):
        """Path from an actor to themselves should have zero steps."""
        result = calculate_shortest_path("actor_A", "actor_A", SAMPLE_DATA)
        self.assertEqual(result["steps"], 0)
        self.assertEqual(result["path"], [])
        self.assertTrue(result["is_successful"])

    def test_direct_neighbours_one_step(self):
        """Two actors sharing a movie should be one step apart."""
        result = calculate_shortest_path("actor_A", "actor_B", SAMPLE_DATA)
        self.assertTrue(result["is_successful"])
        self.assertEqual(result["steps"], 1)
        self.assertEqual(result["path"], [("movie_1", "actor_B")])

    def test_two_step_path(self):
        """Actors connected through an intermediary should be two steps apart."""
        result = calculate_shortest_path("actor_A", "actor_C", SAMPLE_DATA)
        self.assertTrue(result["is_successful"])
        self.assertEqual(result["steps"], 2)
        movie_ids = [step[0] for step in result["path"]]
        actor_ids = [step[1] for step in result["path"]]
        self.assertIn("movie_1", movie_ids)
        self.assertIn("movie_2", movie_ids)
        self.assertIn("actor_B", actor_ids)
        self.assertIn("actor_C", actor_ids)

    def test_path_ends_at_target(self):
        """The last actor in the path should be the target."""
        result = calculate_shortest_path("actor_A", "actor_D", SAMPLE_DATA)
        self.assertTrue(result["is_successful"])
        self.assertEqual(result["path"][-1][1], "actor_D")

    def test_no_path_returns_unsuccessful(self):
        """An isolated actor should produce an unsuccessful result."""
        isolated = {
            "movies": dict(SAMPLE_DATA["movies"]),
            "actors": {**SAMPLE_DATA["actors"], "actor_Z": {"name": "Zara", "movie_ids": []}},
        }
        result = calculate_shortest_path("actor_A", "actor_Z", isolated)
        self.assertFalse(result["is_successful"])
        self.assertEqual(result["steps"], -1)
        self.assertEqual(result["path"], [])

    def test_path_length_matches_steps(self):
        """The length of the path list should equal the reported step count."""
        result = calculate_shortest_path("actor_A", "actor_C", SAMPLE_DATA)
        self.assertEqual(len(result["path"]), result["steps"])

    def test_symmetric_path_lengths(self):
        """The shortest path length should be the same in both directions."""
        forward = calculate_shortest_path("actor_A", "actor_C", SAMPLE_DATA)
        backward = calculate_shortest_path("actor_C", "actor_A", SAMPLE_DATA)
        self.assertEqual(forward["steps"], backward["steps"])


# ===========================================================================
# calculate_lowest_boxoffice_path
# ===========================================================================

class TestCalculateLowestBoxofficePath(unittest.TestCase):
    """Tests for the calculate_lowest_boxoffice_path function."""

    def test_same_actor_zero_cost(self):
        """Path from an actor to themselves should cost zero."""
        result = calculate_lowest_boxoffice_path("actor_A", "actor_A", SAMPLE_DATA)
        self.assertEqual(result["total_box_office"], 0.0)
        self.assertTrue(result["is_successful"])

    def test_direct_path_cost(self):
        """Direct path cost should equal the connecting movie's box office."""
        result = calculate_lowest_boxoffice_path("actor_A", "actor_B", SAMPLE_DATA)
        self.assertTrue(result["is_successful"])
        self.assertEqual(result["total_box_office"], 100.0)

    def test_chooses_cheaper_path(self):
        """Should prefer the path with lower total box office."""
        # A→C costs 150 (movie_1=100 + movie_2=50)
        # A→D costs 300 (movie_1=100 + movie_3=200)
        result_c = calculate_lowest_boxoffice_path("actor_A", "actor_C", SAMPLE_DATA)
        result_d = calculate_lowest_boxoffice_path("actor_A", "actor_D", SAMPLE_DATA)
        self.assertLess(result_c["total_box_office"], result_d["total_box_office"])

    def test_no_path_returns_unsuccessful(self):
        """An isolated actor should produce an unsuccessful result."""
        isolated = {
            "movies": {"movie_1": {"title": "X", "box_office": 10.0, "actor_ids": ["a1", "a2"]}},
            "actors": {
                "a1": {"name": "Alpha", "movie_ids": ["movie_1"]},
                "a2": {"name": "Beta",  "movie_ids": ["movie_1"]},
                "a3": {"name": "Gamma", "movie_ids": []},
            },
        }
        result = calculate_lowest_boxoffice_path("a1", "a3", isolated)
        self.assertFalse(result["is_successful"])
        self.assertEqual(result["total_box_office"], -1.0)

    def test_path_last_actor_is_target(self):
        """The last actor in the path should be the target."""
        result = calculate_lowest_boxoffice_path("actor_A", "actor_C", SAMPLE_DATA)
        self.assertEqual(result["path"][-1][1], "actor_C")


# ===========================================================================
# calculate_score_shortest
# ===========================================================================

class TestCalculateScoreShortest(unittest.TestCase):
    """Tests for the calculate_score_shortest scoring function."""

    def test_perfect_score_when_equal(self):
        """Matching optimal steps exactly should return 100."""
        self.assertEqual(calculate_score_shortest(3, 3), 100.0)

    def test_half_score_for_double_steps(self):
        """Taking twice the optimal steps should return 50."""
        self.assertEqual(calculate_score_shortest(6, 3), 50.0)

    def test_score_above_100_if_player_beats_optimal(self):
        """Fewer steps than optimal should return a score above 100."""
        self.assertEqual(calculate_score_shortest(2, 4), 200.0)

    def test_raises_on_zero_player_steps(self):
        """Should raise ValueError when player_steps is zero."""
        with self.assertRaises(ValueError):
            calculate_score_shortest(0, 3)

    def test_raises_on_negative_player_steps(self):
        """Should raise ValueError when player_steps is negative."""
        with self.assertRaises(ValueError):
            calculate_score_shortest(-1, 3)

    def test_raises_on_zero_optimal_steps(self):
        """Should raise ValueError when optimal_steps is zero."""
        with self.assertRaises(ValueError):
            calculate_score_shortest(3, 0)

    def test_returns_float(self):
        """Score should always be returned as a float."""
        self.assertIsInstance(calculate_score_shortest(4, 3), float)


# ===========================================================================
# calculate_score_boxoffice
# ===========================================================================

class TestCalculateScoreBoxoffice(unittest.TestCase):
    """Tests for the calculate_score_boxoffice scoring function."""

    def test_perfect_score_when_equal(self):
        """Matching optimal box office exactly should return 100."""
        self.assertEqual(calculate_score_boxoffice(500.0, 500.0), 100.0)

    def test_half_score_for_double_spend(self):
        """Spending twice the optimal amount should return 50."""
        self.assertEqual(calculate_score_boxoffice(1000.0, 500.0), 50.0)

    def test_zero_optimal_gives_zero_score(self):
        """An optimal sum of zero should produce a score of zero."""
        self.assertEqual(calculate_score_boxoffice(500.0, 0.0), 0.0)

    def test_raises_on_zero_player_sum(self):
        """Should raise ValueError when player_sum is zero."""
        with self.assertRaises(ValueError):
            calculate_score_boxoffice(0.0, 100.0)

    def test_raises_on_negative_player_sum(self):
        """Should raise ValueError when player_sum is negative."""
        with self.assertRaises(ValueError):
            calculate_score_boxoffice(-10.0, 100.0)

    def test_raises_on_negative_optimal_sum(self):
        """Should raise ValueError when optimal_sum is negative."""
        with self.assertRaises(ValueError):
            calculate_score_boxoffice(100.0, -1.0)

    def test_returns_float(self):
        """Score should always be returned as a float."""
        self.assertIsInstance(calculate_score_boxoffice(300.0, 200.0), float)


# ===========================================================================
# check_player_solution
# ===========================================================================

class TestCheckPlayerSolution(unittest.TestCase):
    """Tests for the check_player_solution function."""

    def test_correct_selection_returns_true(self):
        """Matching the target actor should return True."""
        self.assertTrue(check_player_solution("actor_C", "actor_C"))

    def test_wrong_selection_returns_false(self):
        """A non-matching selection should return False."""
        self.assertFalse(check_player_solution("actor_A", "actor_C"))

    def test_empty_strings_match(self):
        """Two empty strings should be considered a match."""
        self.assertTrue(check_player_solution("", ""))

    def test_case_sensitive(self):
        """Comparison should be case-sensitive."""
        self.assertFalse(check_player_solution("Actor_C", "actor_C"))


# ===========================================================================
# generate_game
# ===========================================================================

class TestGenerateGame(unittest.TestCase):
    """Tests for the generate_game function."""

    REQUIRED_KEYS = (
        "game_mode", "start_actor_id", "start_actor_name",
        "target_actor_id", "target_actor_name", "optimal_path", "is_valid",
    )

    def test_returns_required_keys_shortest(self):
        """Shortest mode result should contain all required keys."""
        game = generate_game("shortest", SAMPLE_DATA)
        for key in self.REQUIRED_KEYS:
            self.assertIn(key, game)

    def test_returns_required_keys_boxoffice(self):
        """Box office mode result should contain all required keys."""
        game = generate_game("box_office", SAMPLE_DATA)
        for key in self.REQUIRED_KEYS:
            self.assertIn(key, game)

    def test_game_mode_is_recorded_shortest(self):
        """game_mode field should reflect the requested mode."""
        game = generate_game("shortest", SAMPLE_DATA)
        self.assertEqual(game["game_mode"], "shortest")

    def test_game_mode_is_recorded_boxoffice(self):
        """game_mode field should reflect the requested mode."""
        game = generate_game("box_office", SAMPLE_DATA)
        self.assertEqual(game["game_mode"], "box_office")

    def test_start_and_target_differ(self):
        """Start and target actor IDs should not be the same."""
        game = generate_game("shortest", SAMPLE_DATA)
        if game["is_valid"]:
            self.assertNotEqual(game["start_actor_id"], game["target_actor_id"])

    def test_actor_names_are_non_empty_strings(self):
        """Actor names in the result should be non-empty strings."""
        game = generate_game("shortest", SAMPLE_DATA)
        self.assertIsInstance(game["start_actor_name"], str)
        self.assertTrue(game["start_actor_name"])
        self.assertIsInstance(game["target_actor_name"], str)
        self.assertTrue(game["target_actor_name"])

    def test_raises_on_invalid_game_mode(self):
        """Should raise ValueError for an unrecognised game mode."""
        with self.assertRaises(ValueError):
            generate_game("invalid_mode", SAMPLE_DATA)

    def test_valid_game_has_successful_path(self):
        """A valid game should always have a successful optimal path."""
        game = generate_game("shortest", SAMPLE_DATA)
        if game["is_valid"]:
            self.assertTrue(game["optimal_path"]["is_successful"])

    def test_all_attempts_fail_returns_is_valid_false(self):
        """Should return is_valid=False when no path can be found."""
        disconnected = {
            "movies": {},
            "actors": {
                "a1": {"name": "Alpha", "movie_ids": []},
                "a2": {"name": "Beta",  "movie_ids": []},
            },
        }
        game = generate_game("shortest", disconnected)
        self.assertFalse(game["is_valid"])


# ===========================================================================
# Integration: round-trip path → score
# ===========================================================================

class TestIntegration(unittest.TestCase):
    """Integration tests combining path finding and scoring."""

    def test_optimal_shortest_path_scores_100(self):
        """Following the optimal shortest path exactly should score 100."""
        game = generate_game("shortest", SAMPLE_DATA)
        if not game["is_valid"]:
            self.skipTest("No valid game generated.")
        optimal_steps = game["optimal_path"]["steps"]
        self.assertEqual(calculate_score_shortest(optimal_steps, optimal_steps), 100.0)

    def test_optimal_boxoffice_path_scores_100(self):
        """Following the optimal box office path exactly should score 100."""
        game = generate_game("box_office", SAMPLE_DATA)
        if not game["is_valid"]:
            self.skipTest("No valid game generated.")
        optimal_bo = game["optimal_path"]["total_box_office"]
        if optimal_bo == 0.0:
            self.skipTest("Zero box office — division undefined.")
        self.assertEqual(calculate_score_boxoffice(optimal_bo, optimal_bo), 100.0)

    def test_suboptimal_player_scores_below_100(self):
        """Taking more steps than optimal should produce a score below 100."""
        result = calculate_shortest_path("actor_A", "actor_C", SAMPLE_DATA)
        self.assertTrue(result["is_successful"])
        score = calculate_score_shortest(result["steps"] + 1, result["steps"])
        self.assertLess(score, 100.0)

    def test_shortest_path_all_actors_exist_in_data(self):
        """Every actor ID in the path should exist in the dataset."""
        result = calculate_shortest_path("actor_A", "actor_C", SAMPLE_DATA)
        for _, actor_id in result["path"]:
            self.assertIn(actor_id, SAMPLE_DATA["actors"])

    def test_shortest_path_all_movies_exist_in_data(self):
        """Every movie ID in the path should exist in the dataset."""
        result = calculate_shortest_path("actor_A", "actor_C", SAMPLE_DATA)
        for movie_id, _ in result["path"]:
            self.assertIn(movie_id, SAMPLE_DATA["movies"])


# ===========================================================================
# build_and_save helpers
# ===========================================================================

def _write_parquets(movies_rows, actors_rows, tmp_dir):
    """
    Write movies and actors DataFrames to parquet files.

    Parameters
    ----------
    movies_rows : list of dict
        Each dict must have: tconst, originalTitle, startYear,
        adjusted_box_office, personIds.
    actors_rows : list of dict
        Each dict must have: nconst, primaryName.
    tmp_dir : str
        Directory to write the parquet files into.

    Returns
    -------
    (movies_path, actors_path) : tuple of str
    """
    import pandas as pd  # pylint: disable=import-outside-toplevel
    movies_path = os.path.join(tmp_dir, "movies.parquet")
    actors_path = os.path.join(tmp_dir, "actors.parquet")
    pd.DataFrame(movies_rows).to_parquet(movies_path, index=False)
    pd.DataFrame(actors_rows).to_parquet(actors_path, index=False)
    return movies_path, actors_path


_MOVIES_ROWS = [
    {
        "tconst": "tt0001",
        "originalTitle": "Alpha Movie",
        "startYear": 2000.0,
        "adjusted_box_office": 100.0,
        "personIds": "nm0001, nm0002",
    },
    {
        "tconst": "tt0002",
        "originalTitle": "Beta Movie",
        "startYear": 2001.0,
        "adjusted_box_office": 200.0,
        "personIds": "nm0002, nm0003",
    },
]

_ACTORS_ROWS = [
    {"nconst": "nm0001", "primaryName": "Alice"},
    {"nconst": "nm0002", "primaryName": "Bob"},
    {"nconst": "nm0003", "primaryName": "Carol"},
]


# ===========================================================================
# build_and_save
# ===========================================================================

class TestBuildAndSaveReturnStructure(unittest.TestCase):
    """Tests that the returned dict has the correct top-level structure."""

    def setUp(self):
        """Create temp directory and write parquet fixtures."""
        self.tmp_dir = tempfile.mkdtemp()
        self.movies_path, self.actors_path = _write_parquets(
            _MOVIES_ROWS, _ACTORS_ROWS, self.tmp_dir
        )
        self.output_path = os.path.join(self.tmp_dir, "game_data.pkl")
        self.data = build_and_save(self.movies_path, self.actors_path, self.output_path)

    def test_returns_dict(self):
        """Return value should be a dict."""
        self.assertIsInstance(self.data, dict)

    def test_has_movies_key(self):
        """Returned dict should contain a 'movies' key."""
        self.assertIn("movies", self.data)

    def test_has_actors_key(self):
        """Returned dict should contain an 'actors' key."""
        self.assertIn("actors", self.data)


class TestBuildAndSavePickleFile(unittest.TestCase):
    """Tests that the pickle file is written correctly."""

    def setUp(self):
        """Create temp directory and write parquet fixtures."""
        self.tmp_dir = tempfile.mkdtemp()
        self.movies_path, self.actors_path = _write_parquets(
            _MOVIES_ROWS, _ACTORS_ROWS, self.tmp_dir
        )
        self.output_path = os.path.join(self.tmp_dir, "game_data.pkl")
        self.data = build_and_save(self.movies_path, self.actors_path, self.output_path)

    def test_pickle_file_is_created(self):
        """A pickle file should exist at the specified output path."""
        self.assertTrue(os.path.exists(self.output_path))

    def test_pickle_file_contains_same_data(self):
        """Loading the pickle file should return the same data as the return value."""
        with open(self.output_path, "rb") as f:
            loaded = pickle.load(f)
        self.assertEqual(loaded, self.data)

    def test_default_output_path(self):
        """When no output_path is given, game_data.pkl should be written to cwd."""
        original_dir = os.getcwd()
        try:
            os.chdir(self.tmp_dir)
            build_and_save(self.movies_path, self.actors_path)
            self.assertTrue(os.path.exists("game_data.pkl"))
        finally:
            os.chdir(original_dir)


class TestBuildAndSaveMovies(unittest.TestCase):
    """Tests for the movies dict built by build_and_save."""

    def setUp(self):
        """Create temp directory and write parquet fixtures."""
        self.tmp_dir = tempfile.mkdtemp()
        self.movies_path, self.actors_path = _write_parquets(
            _MOVIES_ROWS, _ACTORS_ROWS, self.tmp_dir
        )
        self.output_path = os.path.join(self.tmp_dir, "game_data.pkl")
        self.data = build_and_save(self.movies_path, self.actors_path, self.output_path)

    def test_movie_ids_present(self):
        """Both movie IDs from the parquet should appear in the result."""
        self.assertIn("tt0001", self.data["movies"])
        self.assertIn("tt0002", self.data["movies"])

    def test_movie_title_includes_year(self):
        """Title should be formatted as 'Original Title (year)'."""
        self.assertEqual(self.data["movies"]["tt0001"]["title"], "Alpha Movie (2000)")

    def test_movie_box_office_is_float(self):
        """box_office value should be a float."""
        self.assertIsInstance(self.data["movies"]["tt0001"]["box_office"], float)

    def test_movie_box_office_value(self):
        """box_office should match the adjusted_box_office from the parquet."""
        self.assertEqual(self.data["movies"]["tt0001"]["box_office"], 100.0)

    def test_movie_actor_ids_parsed(self):
        """actor_ids should be a list parsed from the comma-separated personIds."""
        self.assertEqual(
            sorted(self.data["movies"]["tt0001"]["actor_ids"]),
            ["nm0001", "nm0002"]
        )

    def test_movie_actor_ids_whitespace_stripped(self):
        """Whitespace around actor IDs in personIds should be stripped."""
        for actor_id in self.data["movies"]["tt0001"]["actor_ids"]:
            self.assertEqual(actor_id, actor_id.strip())

    def test_movie_with_no_year(self):
        """A movie with no startYear should have a title without a year suffix."""
        rows = [{
            "tconst": "tt0099",
            "originalTitle": "No Year Movie",
            "startYear": None,
            "adjusted_box_office": 50.0,
            "personIds": "nm0001",
        }]
        movies_path, actors_path = _write_parquets(rows, _ACTORS_ROWS, self.tmp_dir)
        data = build_and_save(
            movies_path, actors_path, os.path.join(self.tmp_dir, "no_year.pkl")
        )
        self.assertEqual(data["movies"]["tt0099"]["title"], "No Year Movie")

    def test_zero_box_office_movie_excluded(self):
        """Movies with adjusted_box_office of 0.0 should be filtered out."""
        rows = [{
            "tconst": "tt0010",
            "originalTitle": "Zero Movie",
            "startYear": 2005.0,
            "adjusted_box_office": 0.0,
            "personIds": "nm0001",
        }]
        movies_path, actors_path = _write_parquets(rows, _ACTORS_ROWS, self.tmp_dir)
        data = build_and_save(
            movies_path, actors_path, os.path.join(self.tmp_dir, "zero_bo.pkl")
        )
        self.assertNotIn("tt0010", data["movies"])

    def test_none_box_office_excluded(self):
        """Movies with None adjusted_box_office should be treated as 0.0 and excluded."""
        rows = [{
            "tconst": "tt0011",
            "originalTitle": "None BO Movie",
            "startYear": 2005.0,
            "adjusted_box_office": None,
            "personIds": "nm0001",
        }]
        movies_path, actors_path = _write_parquets(rows, _ACTORS_ROWS, self.tmp_dir)
        data = build_and_save(
            movies_path, actors_path, os.path.join(self.tmp_dir, "none_bo.pkl")
        )
        self.assertNotIn("tt0011", data["movies"])


class TestBuildAndSaveActors(unittest.TestCase):
    """Tests for the actors dict built by build_and_save."""

    def setUp(self):
        """Create temp directory and write parquet fixtures."""
        self.tmp_dir = tempfile.mkdtemp()
        self.movies_path, self.actors_path = _write_parquets(
            _MOVIES_ROWS, _ACTORS_ROWS, self.tmp_dir
        )
        self.output_path = os.path.join(self.tmp_dir, "game_data.pkl")
        self.data = build_and_save(self.movies_path, self.actors_path, self.output_path)

    def test_actor_ids_present(self):
        """All three actor IDs should appear in the result."""
        for actor_id in ("nm0001", "nm0002", "nm0003"):
            self.assertIn(actor_id, self.data["actors"])

    def test_actor_name_correct(self):
        """Actor name should match primaryName from the parquet."""
        self.assertEqual(self.data["actors"]["nm0001"]["name"], "Alice")

    def test_actor_movie_ids_is_list(self):
        """movie_ids for each actor should be a list."""
        self.assertIsInstance(self.data["actors"]["nm0001"]["movie_ids"], list)

    def test_actor_single_movie(self):
        """nm0001 appears only in tt0001."""
        self.assertEqual(self.data["actors"]["nm0001"]["movie_ids"], ["tt0001"])

    def test_actor_in_multiple_movies(self):
        """nm0002 appears in both tt0001 and tt0002."""
        self.assertCountEqual(
            self.data["actors"]["nm0002"]["movie_ids"],
            ["tt0001", "tt0002"]
        )

    def test_actor_with_no_movies_excluded(self):
        """Actors not linked to any movie should be excluded from the result."""
        actors_with_extra = _ACTORS_ROWS + [{"nconst": "nm9999", "primaryName": "Nobody"}]
        movies_path, actors_path = _write_parquets(
            _MOVIES_ROWS, actors_with_extra, self.tmp_dir
        )
        data = build_and_save(
            movies_path, actors_path, os.path.join(self.tmp_dir, "no_movies.pkl")
        )
        self.assertNotIn("nm9999", data["actors"])

    def test_actor_excluded_when_only_movie_has_zero_box_office(self):
        """An actor whose only movie has zero box office should be excluded."""
        rows = [{
            "tconst": "tt0020",
            "originalTitle": "Flop",
            "startYear": 2000.0,
            "adjusted_box_office": 0.0,
            "personIds": "nm9998",
        }]
        actors = [{"nconst": "nm9998", "primaryName": "Flop Actor"}]
        movies_path, actors_path = _write_parquets(rows, actors, self.tmp_dir)
        data = build_and_save(
            movies_path, actors_path, os.path.join(self.tmp_dir, "flop.pkl")
        )
        self.assertNotIn("nm9998", data["actors"])


class TestBuildAndSaveEdgeCases(unittest.TestCase):
    """Edge case tests for build_and_save."""

    def setUp(self):
        """Create a temp directory for output files."""
        self.tmp_dir = tempfile.mkdtemp()

    def test_empty_parquets_produce_empty_dicts(self):
        """Empty input parquets should produce empty movies and actors dicts."""
        movies_path, actors_path = _write_parquets([], [], self.tmp_dir)
        data = build_and_save(
            movies_path, actors_path, os.path.join(self.tmp_dir, "empty.pkl")
        )
        self.assertEqual(data["movies"], {})
        self.assertEqual(data["actors"], {})

    def test_single_movie_single_actor(self):
        """A single movie with a single actor should produce one movie and one actor."""
        rows = [{
            "tconst": "tt0001",
            "originalTitle": "Solo",
            "startYear": 1999.0,
            "adjusted_box_office": 10.0,
            "personIds": "nm0001",
        }]
        actors = [{"nconst": "nm0001", "primaryName": "Solo Actor"}]
        movies_path, actors_path = _write_parquets(rows, actors, self.tmp_dir)
        data = build_and_save(
            movies_path, actors_path, os.path.join(self.tmp_dir, "solo.pkl")
        )
        self.assertEqual(len(data["movies"]), 1)
        self.assertEqual(len(data["actors"]), 1)

    def test_all_movies_zero_box_office_produces_empty_result(self):
        """If every movie has zero box office, both dicts should be empty."""
        rows = [
            {
                "tconst": "tt0001",
                "originalTitle": "Flop One",
                "startYear": 2000.0,
                "adjusted_box_office": 0.0,
                "personIds": "nm0001",
            },
            {
                "tconst": "tt0002",
                "originalTitle": "Flop Two",
                "startYear": 2001.0,
                "adjusted_box_office": 0.0,
                "personIds": "nm0002",
            },
        ]
        actors = [
            {"nconst": "nm0001", "primaryName": "Alice"},
            {"nconst": "nm0002", "primaryName": "Bob"},
        ]
        movies_path, actors_path = _write_parquets(rows, actors, self.tmp_dir)
        data = build_and_save(
            movies_path, actors_path, os.path.join(self.tmp_dir, "all_flop.pkl")
        )
        self.assertEqual(data["movies"], {})
        self.assertEqual(data["actors"], {})


if __name__ == "__main__":
    unittest.main()
