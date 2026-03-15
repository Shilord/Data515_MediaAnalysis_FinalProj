import streamlit as st
from core.hints import get_realtime_hint
from core.state import init_state, submit_step, go_home, start_normal_mode
from core.game_logic import (
    calculate_shortest_path,
    calculate_lowest_boxoffice_path,
    get_movies_for_actor,
    get_actors_for_movie,
)


def render():
    init_state()

    data = st.session_state.game_data

    # ---------- session helpers ----------
    if "_cast_cache_movie" not in st.session_state:
        st.session_state._cast_cache_movie = None

    if "_cast_cache" not in st.session_state:
        st.session_state._cast_cache = {}

    # ---------- header + hint ----------
    col_title, col_hint = st.columns([4,2])

    with col_title:
        st.markdown(
            "<h1 style='text-align:center; margin-bottom:24px;'>Normal Mode</h1>",
            unsafe_allow_html=True,
        )

    with col_hint:
        with st.expander("💡 Hint", expanded=False):

            current_actor = st.session_state.current_actor
            target_actor = st.session_state.end_actor
            mode = st.session_state.mode

            if mode == "normal":
                hint_result = calculate_shortest_path(current_actor, target_actor, data)
            elif mode == "challenge":
                hint_result = calculate_lowest_boxoffice_path(current_actor, target_actor, data)
            else:
                hint_result = None

            if hint_result and hint_result["is_successful"] and hint_result["path"]:
                movie_id, actor_id = hint_result["path"][0]

                movie_title = data["movies"][movie_id]["title"]
                actor_name = data["actors"][actor_id]["name"]

                st.write("Best next move:")
                st.write(f"🎬 Movie: **{movie_title}**")
                st.write(f"🎭 Actor: **{actor_name}**")
            else:
                st.write("No hint available.")

    # ---------- actors ----------
    current_actor = st.session_state.current_actor
    target_actor = st.session_state.end_actor

    current_name = data["actors"][current_actor]["name"]
    target_name = data["actors"][target_actor]["name"]

    # ---------- actor cards ----------
    col_left, col_right = st.columns(2)

    with col_left:
        st.markdown(
            "<h4 style='text-align:center;'>Start Actor</h4>",
            unsafe_allow_html=True,
        )

        st.markdown(
            f"<h3 style='text-align:center; margin-top:12px;'>{current_name}</h3>",
            unsafe_allow_html=True,
        )

    with col_right:
        st.markdown(
            "<h4 style='text-align:center;'>Target Actor</h4>",
            unsafe_allow_html=True,
        )

        st.markdown(
            f"<h3 style='text-align:center; margin-top:12px;'>{target_name}</h3>",
            unsafe_allow_html=True,
        )

    st.markdown("---")

    # ---------- movie selection ----------
    valid_movies = get_movies_for_actor(current_actor, data)

    if not valid_movies:
        st.error("No movies found for this actor.")
        return

    # ---------- movie selection ----------
    valid_movies = get_movies_for_actor(current_actor, data)

    if not valid_movies:
        st.error("No movies found for this actor.")
        return

    # Show movie dropdown only if no movie has been confirmed yet
    if st.session_state._cast_cache_movie is None:

        with st.form("movie_confirm_form", clear_on_submit=False):

            selected_movie_id = st.selectbox(
                "Choose a Movie",
                options=list(valid_movies.keys()),
                format_func=lambda mid: valid_movies[mid],
                key="movie_select",
            )

            movie_confirmed = st.form_submit_button("Confirm Movie")

        if movie_confirmed:
            st.session_state._cast_cache_movie = selected_movie_id
            st.session_state._cast_cache = get_actors_for_movie(selected_movie_id, data)
            st.rerun()

    # After confirmation, hide dropdown and show fixed selected movie
    else:
        confirmed_movie_id = st.session_state._cast_cache_movie
        st.success(f"Selected Movie: {valid_movies[confirmed_movie_id]}")

    # ---------- actor selection ----------
    if st.session_state._cast_cache_movie:

        cast_dict = st.session_state._cast_cache

        cast_dict = {
            aid: name
            for aid, name in cast_dict.items()
            if aid != current_actor
        }

        if not cast_dict:
            st.error("No other actors found in this movie.")
            return

        with st.form("actor_confirm_form_normal", clear_on_submit=False):

            next_actor_id = st.selectbox(
                "Next Actor (type to search, or open the menu to select)",
                options=list(cast_dict.keys()),
                format_func=lambda aid: cast_dict[aid],
                key="next_actor_select",
            )

            confirmed = st.form_submit_button("Confirm Next Actor")

        if confirmed:

            movie_id = st.session_state._cast_cache_movie

            submit_step(
                valid_movies[movie_id],
                next_actor_id,
            )

            st.session_state._cast_cache_movie = None
            st.session_state._cast_cache = {}

            st.rerun()

    # ---------- bottom buttons ----------
    colA, colB = st.columns(2)

    if colA.button("Restart"):
        start_normal_mode()
        st.rerun()

    if colB.button("Back to Home"):
        go_home()
        st.rerun()