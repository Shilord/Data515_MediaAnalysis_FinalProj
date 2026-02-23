import streamlit as st

from core.state import init_state, go_home
from core.mock_service import get_optimal_steps, get_optimal_min_boxoffice


def render():
    init_state()

    st.title("Result")
    st.write("Message:", st.session_state.message)

    if st.session_state.mode == "normal":
        st.write("Steps Used:", st.session_state.step_count)
        optimal = get_optimal_steps(st.session_state.start_actor, st.session_state.end_actor)
        st.write("Optimal Steps:", optimal)

    if st.session_state.mode == "challenge":
        st.write("Total Box Office:", st.session_state.total_boxoffice)
        optimal_min = get_optimal_min_boxoffice(st.session_state.start_actor, st.session_state.end_actor)
        st.write("Optimal Minimum Box Office:", optimal_min)

    st.subheader("Your Path")
    for a, m, b in st.session_state.history:
        st.write(f"{a} -> {m} -> {b}")

    col1, col2 = st.columns(2)

    with col1:
        if st.button("Play Again"):
            st.session_state.current_view = "home"

    with col2:
        if st.button("Back to Home"):
            go_home()