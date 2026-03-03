import streamlit as st

def render(name, label=None):
    box = st.container()
    with box:
        st.markdown(
            """
            <div style="
                width: 140px;
                height: 180px;
                border: 1px solid #ccc;
                border-radius: 8px;
                display: flex;
                align-items: center;
                justify-content: center;
                margin-bottom: 8px;
                background-color: #f7f7f7;
            ">
                <span style="color:#999;">No Image</span>
            </div>
            """,
            unsafe_allow_html=True,
        )
        st.write(name)
        if label:
            st.caption(label)