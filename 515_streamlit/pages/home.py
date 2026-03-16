import streamlit as st

from core.state import start_normal_mode, start_challenge_mode, init_state

def render():
    init_state()

    st.markdown(
        """
        <style>
        div.stButton > button {
            font-size: 28px !important;
            font-weight: 800 !important;
            padding: 0.9rem 1rem !important;
            border-radius: 14px !important;
            white-space: nowrap !important;
            line-height: 1.1 !important;
            min-height: 72px !important;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )

    st.markdown(
        "<h1 style='text-align:center;'>Movie Actor Link Game</h1>",
        unsafe_allow_html=True,
    )

    with st.expander("🎮 How to Play", expanded=True):
        st.markdown(
            """
            Connect the **Start Actor** to the **Target Actor** by hopping through movies and co-stars.

            **How to play**
            1. Start from the current actor.
            2. Choose a movie that the actor appeared in.
            3. Pick a co-star from that movie to become your next actor.
            4. Repeat until you reach the target actor.

            **Game modes**
            - **Normal Mode**: win in as **few steps** as possible (each move counts as 1 step).
            - **Challenge Mode**: win with the **lowest total box office** (each chosen movie adds its box office to your total).

            **🏆 Winning**
            You win as soon as your current actor matches the target actor. Your score is compared to the algorithm’s optimal path.
            """
        )

    st.markdown("---")

    _, col1, spacer, col2, _ = st.columns([1.2, 1.25, 0.4, 1.25, 1.2])

    with col1:
        if st.button("Normal Mode", use_container_width=True):
            start_normal_mode()
            st.rerun()

    with col2:
        if st.button("Challenge Mode", use_container_width=True):
            start_challenge_mode()
            st.rerun()