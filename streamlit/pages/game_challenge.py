import streamlit as st

from core.state import (
    init_state,
    submit_step,
    reset_game,
    go_home,
    start_challenge_mode,
)
from core.game_logic import (
    get_movies_for_actor,
    get_actors_for_movie,
)

def render():
    init_state()

    data = st.session_state.game_data

    if "_clear_inputs" not in st.session_state:
        st.session_state._clear_inputs = False
    if "_cast_cache_movie" not in st.session_state:
        st.session_state._cast_cache_movie = None
    if "_cast_cache" not in st.session_state:
        st.session_state._cast_cache = {}

    if st.session_state._clear_inputs:
        st.session_state._clear_inputs = False
        for k in ["movie_name", "next_actor_select"]:
            if k in st.session_state:
                del st.session_state[k]
        st.session_state._cast_cache_movie = None
        st.session_state._cast_cache = {}

    st.markdown("<h1 style='text-align:center;'>Challenge Mode</h1>", unsafe_allow_html=True)
    st.markdown(
        f"<p style='text-align:center;'>Total Box Office: {st.session_state.total_boxoffice}</p>",
        unsafe_allow_html=True,
    )

    current_actor = st.session_state.current_actor
    target_actor = st.session_state.end_actor

    current_name = data["actors"][current_actor]["name"]
    target_name = data["actors"][target_actor]["name"]

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
            f"<h3 style='text-align:center;'>{current_name}</h3>",
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
            f"<h3 style='text-align:center;'>{target_name}</h3>",
            unsafe_allow_html=True,
        )

    st.markdown("---")

    movie_input = st.text_input("Movie Name", key="movie_name")
    movie_input = (movie_input or "").strip()

    valid_movies = get_movies_for_actor(current_actor, data)

    if movie_input and movie_input != st.session_state._cast_cache_movie:
        st.session_state._cast_cache_movie = None
        st.session_state._cast_cache = {}
        if "next_actor_select" in st.session_state:
            del st.session_state["next_actor_select"]

    if movie_input:
        matched_movie_id = None
        for mid, title in valid_movies.items():
            if movie_input.lower() in title.lower():
                matched_movie_id = mid
                break

        if not matched_movie_id:
            st.error("Invalid movie for the current actor. Try another movie.")
        else:
            if st.session_state._cast_cache_movie != matched_movie_id:
                st.session_state._cast_cache_movie = matched_movie_id
                st.session_state._cast_cache = get_actors_for_movie(
                    matched_movie_id, data
                )

            cast_dict = st.session_state._cast_cache

            if not cast_dict:
                st.error("No cast found for this movie.")
            else:
                cast_names = list(cast_dict.values())

                with st.form("actor_confirm_form_challenge", clear_on_submit=False):
                    next_actor_name = st.selectbox(
                        "Next Actor (type to search, or open the menu to select)",
                        cast_names,
                        key="next_actor_select",
                    )
                    confirmed = st.form_submit_button("Confirm Next Actor")

                if confirmed:
                    next_actor_id = None
                    for aid, name in cast_dict.items():
                        if name == next_actor_name:
                            next_actor_id = aid
                            break

                    if not next_actor_id:
                        st.error("Invalid actor selection.")
                    else:
                        boxoffice = data["movies"][matched_movie_id]["box_office"]
                        submit_step(
                            valid_movies[matched_movie_id],
                            next_actor_id,
                            movie_boxoffice=boxoffice,
                        )
                        st.session_state._clear_inputs = True
                        st.rerun()

    colA, colB = st.columns(2)

    if colA.button("Restart"):
        start_challenge_mode()
        for k in [
            "movie_name",
            "next_actor_select",
            "_cast_cache_movie",
            "_cast_cache",
            "_clear_inputs",
        ]:
            if k in st.session_state:
                del st.session_state[k]
        st.rerun()

    if colB.button("Back to Home"):
        go_home()
        st.rerun()