import streamlit as st

from core.state import init_state, submit_step, reset_game, go_home
from core.mock_service import (
    validate_movie,
    validate_actor,
    get_cast_by_movie,
    get_random_actor_pair,
)


def render():
    init_state()

    if "_clear_inputs" not in st.session_state:
        st.session_state._clear_inputs = False
    if "_cast_cache_movie" not in st.session_state:
        st.session_state._cast_cache_movie = None
    if "_cast_cache" not in st.session_state:
        st.session_state._cast_cache = []

    if st.session_state._clear_inputs:
        st.session_state._clear_inputs = False
        for k in ["movie_name", "next_actor_select"]:
            if k in st.session_state:
                del st.session_state[k]
        st.session_state._cast_cache_movie = None
        st.session_state._cast_cache = []

    st.markdown("<h1 style='text-align:center;'>Normal Mode</h1>", unsafe_allow_html=True)

    col_left, _, col_right = st.columns([1, 0.2, 1])

    with col_left:
        st.markdown(
            """
            <div style="width:200px;height:260px;border:2px solid #ddd;border-radius:12px;
                        display:flex;align-items:center;justify-content:center;
                        margin:auto;background:#fff;">
                <span style="color:#bbb;">No Image</span>
            </div>
            """,
            unsafe_allow_html=True,
        )
        st.markdown(
            f"<h3 style='text-align:center;'>{st.session_state.current_actor}</h3>",
            unsafe_allow_html=True,
        )

    with col_right:
        st.markdown(
            """
            <div style="width:200px;height:260px;border:2px solid #ddd;border-radius:12px;
                        display:flex;align-items:center;justify-content:center;
                        margin:auto;background:#fff;">
                <span style="color:#bbb;">No Image</span>
            </div>
            """,
            unsafe_allow_html=True,
        )
        st.markdown(
            f"<h3 style='text-align:center;'>{st.session_state.end_actor}</h3>",
            unsafe_allow_html=True,
        )

    st.markdown("---")

    movie = st.text_input("Movie Name", key="movie_name")
    movie = (movie or "").strip()

    if movie and movie != st.session_state._cast_cache_movie:
        st.session_state._cast_cache_movie = None
        st.session_state._cast_cache = []
        if "next_actor_select" in st.session_state:
            del st.session_state["next_actor_select"]

    if movie:
        movie_ok = validate_movie(st.session_state.current_actor, movie)
        if not movie_ok:
            st.error("Invalid movie for the current actor. Try another movie.")
        else:
            if st.session_state._cast_cache_movie != movie:
                st.session_state._cast_cache_movie = movie
                st.session_state._cast_cache = get_cast_by_movie(movie)

            cast_options = st.session_state._cast_cache

            if not cast_options:
                st.error("No cast found for this movie.")
            else:
                with st.form("actor_confirm_form_normal", clear_on_submit=False):
                    next_actor = st.selectbox(
                        "Next Actor (type to search, or open the menu to select)",
                        cast_options,
                        key="next_actor_select",
                    )
                    confirmed = st.form_submit_button("Confirm Next Actor")

                if confirmed:
                    actor_ok = validate_actor(movie, next_actor)
                    if not actor_ok:
                        st.error("Invalid actor for this movie. Please select another actor.")
                    else:
                        submit_step(movie, next_actor)
                        st.session_state._clear_inputs = True
                        st.rerun()

    colA, colB = st.columns(2)

    if colA.button("Restart"):
        a, b = get_random_actor_pair()
        reset_game()
        st.session_state.mode = "normal"
        st.session_state.start_actor = a
        st.session_state.end_actor = b
        st.session_state.current_actor = a
        st.session_state.current_view = "game"
        for k in ["movie_name", "next_actor_select", "_cast_cache_movie", "_cast_cache", "_clear_inputs"]:
            if k in st.session_state:
                del st.session_state[k]
        st.rerun()

    if colB.button("Back to Home"):
        go_home()
        st.rerun()