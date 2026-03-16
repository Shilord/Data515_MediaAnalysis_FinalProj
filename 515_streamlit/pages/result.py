import streamlit as st

from core.state import init_state, go_home
from core.game_logic import (
    calculate_score_shortest,
    calculate_score_boxoffice,
)

def render():
    init_state()

    st.title("Result")
    st.write(st.session_state.message)

    if not st.session_state.current_game:
        st.error("No active game found.")
        return

    data = st.session_state.game_data
    optimal_data = st.session_state.current_game["optimal_path"]

    if st.session_state.mode == "normal":

        player_steps = st.session_state.step_count
        optimal_steps = optimal_data["steps"]

        score = calculate_score_shortest(player_steps, optimal_steps)

        st.write("Steps Used:", player_steps)
        st.write("Optimal Steps:", optimal_steps)
        st.write("Score:", round(score, 2))

    elif st.session_state.mode == "challenge":

        player_sum = st.session_state.total_boxoffice
        optimal_sum = optimal_data["total_box_office"]

        score = calculate_score_boxoffice(player_sum, optimal_sum)

        st.write("Total Box Office:", player_sum)
        st.write("Optimal Minimum Box Office:", optimal_sum)
        st.write("Score:", round(score, 2))

    if score == 100:
        st.success("Perfect! You found the optimal path.")
    elif score >= 80:
        st.success("Great job!")
    elif score >= 50:
        st.info("Nice try!")
    else:
        st.warning("You can do better next time!")

    st.markdown("---")

    st.subheader("Your Path")

    for actor_a, movie, actor_b in st.session_state.history:

        actor_a_name = data["actors"][actor_a]["name"]
        actor_b_name = data["actors"][actor_b]["name"]

        st.write(f"{actor_a_name} → {movie} → {actor_b_name}")

    st.markdown("---")

    st.subheader("Optimal Path")

    optimal_path = optimal_data["path"]

    current_actor = st.session_state.current_game["start_actor_id"]

    for movie_id, actor_id in optimal_path:

        movie_title = data["movies"][movie_id]["title"]
        next_actor_name = data["actors"][actor_id]["name"]
        current_actor_name = data["actors"][current_actor]["name"]

        st.write(f"{current_actor_name} → {movie_title} → {next_actor_name}")

        current_actor = actor_id

    st.markdown("---")

    col1, col2 = st.columns(2)

    with col1:
        if st.button("Play Again"):
            st.session_state.current_view = "home"
            st.rerun()

    with col2:
        if st.button("Back to Home"):
            go_home()
            st.rerun()