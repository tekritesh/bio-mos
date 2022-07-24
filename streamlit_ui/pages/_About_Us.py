import streamlit as st
st.set_page_config(layout="wide",
                   page_title="Land Cover",
                   page_icon="🐸")

f = open('assets/about.md', 'r')

st.markdown(f.read())
