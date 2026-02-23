import streamlit as st


def init_state():
    if "current_view" not in st.session_state:
        st.session_state.current_view = "home"

    if "mode" not in st.session_state:
        st.session_state.mode = None

    if "start_actor" not in st.session_state:
        st.session_state.start_actor = None

    if "end_actor" not in st.session_state:
        st.session_state.end_actor = None

    if "current_actor" not in st.session_state:
        st.session_state.current_actor = None

    if "step_count" not in st.session_state:
        st.session_state.step_count = 0

    if "total_boxoffice" not in st.session_state:
        st.session_state.total_boxoffice = 0

    if "history" not in st.session_state:
        st.session_state.history = []

    if "game_over" not in st.session_state:
        st.session_state.game_over = False

    if "message" not in st.session_state:
        st.session_state.message = ""


def reset_game():
    st.session_state.start_actor = None
    st.session_state.end_actor = None
    st.session_state.current_actor = None
    st.session_state.step_count = 0
    st.session_state.total_boxoffice = 0
    st.session_state.history = []
    st.session_state.game_over = False
    st.session_state.message = ""


def go_home():
    st.session_state.current_view = "home"
    st.session_state.mode = None
    reset_game()


def start_normal_mode(start_actor, end_actor):
    reset_game()
    st.session_state.mode = "normal"
    st.session_state.start_actor = start_actor
    st.session_state.end_actor = end_actor
    st.session_state.current_actor = start_actor
    st.session_state.current_view = "game"


def start_challenge_mode(start_actor, end_actor):
    reset_game()
    st.session_state.mode = "challenge"
    st.session_state.start_actor = start_actor
    st.session_state.end_actor = end_actor
    st.session_state.current_actor = start_actor
    st.session_state.current_view = "game_challenge"


def submit_step(movie_name, next_actor, movie_boxoffice=0):
    st.session_state.history.append((st.session_state.current_actor, movie_name, next_actor))
    st.session_state.current_actor = next_actor

    if st.session_state.mode == "normal":
        st.session_state.step_count += 1
    elif st.session_state.mode == "challenge":
        st.session_state.total_boxoffice += int(movie_boxoffice or 0)

    if st.session_state.current_actor == st.session_state.end_actor:
        st.session_state.game_over = True
        st.session_state.current_view = "result"
        st.session_state.message = "🎉 You connected to the target actor!"


def end_game_with_fail(reason=""):
    st.session_state.game_over = True
    st.session_state.current_view = "result"
    st.session_state.message = reason or "Game ended"