import os
import streamlit as st
from PIL import Image



def run():
    st.set_page_config(
        page_title="Hello",
        page_icon="👋",
    )


    st.write("# Welcome to GBIF project! 👋")
    image = Image.open('assets/home.png')
    st.image(image, caption=None)
    st.sidebar.success("Select a visualization")


if __name__ == "__main__":
    run()