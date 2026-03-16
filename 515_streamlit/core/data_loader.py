import streamlit as st
from core.game_logic import load_data

@st.cache_data
def get_game_data():
    return load_data("515_streamlit/game_data/game_data.pkl")
