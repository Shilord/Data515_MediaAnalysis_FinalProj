import streamlit as st
from core.data_loader import get_game_data  
from core.game_logic import generate_game

def init_state():
    # -----------------------------
    # Routing / global app state
    # -----------------------------
    if "current_view" not in st.session_state:
        st.session_state.current_view = "home"

    # Load the preprocessed dataset once (cached by Streamlit)
    if "game_data" not in st.session_state:
        st.session_state.game_data = get_game_data()

    # Stores the current generated game (start/target actors + optimal path, etc.)
    if "current_game" not in st.session_state:
        st.session_state.current_game = None

    # -----------------------------
    # Game state (existing fields)
    # -----------------------------
    if "mode" not in st.session_state:
        st.session_state.mode = None

    if "start_actor" not in st.session_state:
        st.session_state.start_actor = None

    if "end_actor" not in st.session_state:
        st.session_state.end_actor = None

    if "current_actor" not in st.session_state:
        st.session_state.current_actor = None

    # Used in normal mode (shortest steps)
    if "step_count" not in st.session_state:
        st.session_state.step_count = 0

    # Used in challenge mode (accumulated box office)
    if "total_boxoffice" not in st.session_state:
        st.session_state.total_boxoffice = 0

    # Step history, e.g. (current_actor, movie_title_or_id, next_actor)
    if "history" not in st.session_state:
        st.session_state.history = []

    # Game end flag
    if "game_over" not in st.session_state:
        st.session_state.game_over = False

    # UI message shown on result page
    if "message" not in st.session_state:
        st.session_state.message = ""

def reset_game():
    # Reset per-game state (does not clear loaded data)
    st.session_state.start_actor = None
    st.session_state.end_actor = None
    st.session_state.current_actor = None
    st.session_state.step_count = 0
    st.session_state.total_boxoffice = 0
    st.session_state.history = []
    st.session_state.game_over = False
    st.session_state.message = ""
    st.session_state.current_game = None  # Also clear the generated game object

def go_home():
    # Return to the home view and clear any active game
    st.session_state.current_view = "home"
    st.session_state.mode = None
    reset_game()

def start_normal_mode():
    reset_game()

    game = generate_game(
        "shortest",
        st.session_state.game_data
    )

    if not game["is_valid"]:
        st.session_state.message = "Could not generate a valid game. Try again."
        return

    st.session_state.mode = "normal"
    st.session_state.current_game = game

    st.session_state.start_actor = game["start_actor_id"]
    st.session_state.end_actor = game["target_actor_id"]
    st.session_state.current_actor = game["start_actor_id"]

    st.session_state.current_view = "game"

def start_challenge_mode():
    reset_game()

    game = generate_game(
        "box_office",
        st.session_state.game_data
    )

    if not game["is_valid"]:
        st.session_state.message = "Could not generate a valid challenge game."
        return

    st.session_state.mode = "challenge"
    st.session_state.current_game = game

    st.session_state.start_actor = game["start_actor_id"]
    st.session_state.end_actor = game["target_actor_id"]
    st.session_state.current_actor = game["start_actor_id"]

    st.session_state.current_view = "game_challenge"

def submit_step(movie_name, next_actor, movie_boxoffice=0):
    # Record a player step and advance the current actor
    st.session_state.history.append((st.session_state.current_actor, movie_name, next_actor))
    st.session_state.current_actor = next_actor

    # Update score counters depending on mode
    if st.session_state.mode == "normal":
        st.session_state.step_count += 1
    elif st.session_state.mode == "challenge":
        st.session_state.total_boxoffice += int(movie_boxoffice or 0)

    # Check win condition
    if st.session_state.current_actor == st.session_state.end_actor:
        st.session_state.game_over = True
        st.session_state.current_view = "result"
        st.session_state.message = "🎉 You connected to the target actor!"

def end_game_with_fail(reason=""):
    # Force-end the game and show the result page with a message
    st.session_state.game_over = True
    st.session_state.current_view = "result"
    st.session_state.message = reason or "Game ended"