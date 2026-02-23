import streamlit as st

from core.state import start_normal_mode, start_challenge_mode, init_state
from core.mock_service import get_random_actor_pair


def render():
    init_state()

    st.title("Movie Actor Link Game")

    col1, col2 = st.columns(2)

    with col1:
        if st.button("Normal Mode"):
            a, b = get_random_actor_pair()
            start_normal_mode(a, b)

    with col2:
        if st.button("Challenge Mode"):
            a, b = get_random_actor_pair()
            start_challenge_mode(a, b)