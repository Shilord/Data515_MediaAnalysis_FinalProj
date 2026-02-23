import streamlit as st

from core.state import start_challenge_mode, init_state
from core.mock_service import get_random_actor_pair


def render():
    init_state()

    st.title("Challenge Mode Setup")

    min_boxoffice = st.number_input("Minimum Box Office", min_value=0, value=0, step=1000000)

    if st.button("Start Challenge"):
        a, b = get_random_actor_pair()
        start_challenge_mode(a, b, min_boxoffice)

    if st.button("Back to Home"):
        st.session_state.current_view = "home"