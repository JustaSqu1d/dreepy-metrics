import streamlit as st

st.set_page_config(page_title="Dreepy Metrics", page_icon=":material/dynamic_form:", layout="wide")

home_page = st.Page("home.py", title="Home")
team_builder_page = st.Page("team_builder.py", title="Team Builder")

pg = st.navigation([home_page, team_builder_page], position="sidebar")
pg.run()