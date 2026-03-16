import sys
import os

sys.path.append(os.path.dirname(__file__))

import streamlit as st

from core.state import init_state
from pages.home import render as render_home
from pages.game import render as render_game
from pages.game_challenge import render as render_game_challenge
from pages.result import render as render_result

st.set_page_config(page_title="Movie Actor Link Game", layout="centered")

st.markdown(
    """
    <style>
        [data-testid="stSidebar"] { display: none; }
    </style>
    """,
    unsafe_allow_html=True,
)

init_state()

view = st.session_state.current_view

if view == "home":
    render_home()
elif view == "config_challenge":
    render_config_challenge()
elif view == "game":
    render_game()
elif view == "game_challenge":
    render_game_challenge()
elif view == "result":
    render_result()
else:
    render_home()