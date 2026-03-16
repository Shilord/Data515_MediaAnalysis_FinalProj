import streamlit as st


def render():
    movie = st.text_input("Movie Name")
    actor = st.text_input("Next Actor Name")
    submit = st.button("Submit Step")
    return movie, actor, submit