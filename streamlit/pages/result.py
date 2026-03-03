import streamlit as st

from core.state import init_state, go_home
from core.game_logic import (
    calculate_score_shortest,
    calculate_score_boxoffice,
)


def render():
    init_state()

    st.title("Result")
    st.write("Message:", st.session_state.message)

    # Safety check
    if not st.session_state.current_game:
        st.error("No active game found.")
        return

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

    st.subheader("Your Path")

    for a, m, b in st.session_state.history:
        st.write(f"{a} -> {m} -> {b}")

    col1, col2 = st.columns(2)

    with col1:
        if st.button("Play Again"):
            st.session_state.current_view = "home"
            st.rerun()

    with col2:
        if st.button("Back to Home"):
            go_home()
            st.rerun()