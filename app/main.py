import streamlit as st
from deta import Deta

# Load database
deta = Deta(st.secrets["deta_key"])
db = deta.Base("mates")

st.markdown("# Meet mates")

with st.form("form"):
    name = st.text_input("Your full name", placeholder="Lowis Douglas")
    location_name = st.text_input(
        "Public transport station close to your home", placeholder="Eg: Châtelet"
    )
    st.form_submit_button("Search mates")
    st.markdown(
        "**By clicking on search mate, you agree to share the above info with other users.**"
    )
