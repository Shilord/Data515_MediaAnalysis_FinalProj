import streamlit as st

from core.state import start_normal_mode, start_challenge_mode, init_state

def render():
    init_state()

    st.title("Movie Actor Link Game")

    # Collapsible introduction
    with st.expander("🎮 How to Play", expanded=True):
        st.markdown(
            """
            Connect the **Start Actor** to the **Target Actor** by hopping through movies and co-stars.

            **How to play**
            1. Start from the current actor.
            2. Enter a movie that the actor appeared in.
            3. Pick a co-star from that movie to become your next actor.
            4. Repeat until you reach the target actor.

            **Game modes**
            - **Normal Mode**: win in as **few steps** as possible (each move counts as 1 step).
            - **Challenge Mode**: win with the **lowest total box office** (each chosen movie adds its box office to your total).

            **🏆**
            You win as soon as your current actor matches the target actor. Your score is compared to the algorithm’s optimal path.
            """
        )

    st.markdown("---")

    col1, col2 = st.columns(2)

    with col1:
        if st.button("Normal Mode"):
            start_normal_mode()
            st.rerun()

    with col2:
        if st.button("Challenge Mode"):
            start_challenge_mode()
            st.rerun()
    
    data = st.session_state.game_data