import streamlit as st
import pandas as pd
import numpy as np
from deta import Deta
from typing import List

# Load database
deta = Deta(st.secrets["deta_key"])
db = deta.Base("mates")


@st.cache()
def load_stops():
    stops = pd.read_csv("app/slim_stops.csv")


stops = load_stops()


def get_coords(location_name: str) -> List[float]:
    """Find associated coordinates to a location name."""
    return [0, 0]


def find_mates(coords: List[float]) -> List[dict]:
    """Find mates that indicated a location near coords."""
    return []


# Page

st.markdown("# Meet mates")

with st.form("form") as submitted:
    name = st.text_input("Your full name", placeholder="Lowis Douglas")
    location_name = st.selectbox(
        "Public transport station close to your home",
        placeholder="Eg: Châtelet",
        options=stops["stop_name"],
    )
    st.form_submit_button("Search mates")
    st.markdown(
        "***By clicking on search mate, you agree to share the above info with other users.***"
    )

if submitted:
    coords = get_coords(location_name)
    db.put({"name": name, "location_name": location_name, "coords": coords})
