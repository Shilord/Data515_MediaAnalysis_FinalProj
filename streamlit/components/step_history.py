import streamlit as st


def render(history):
    st.subheader("History")
    if not history:
        st.write("No steps yet")
        return

    for i, (a, m, b) in enumerate(history, start=1):
        st.write(f"{i}. {a} -> {m} -> {b}")