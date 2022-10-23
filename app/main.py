import streamlit as st
import pandas as pd
import numpy as np
from deta import Deta
from typing import List, Dict
from geopy.distance import geodesic

# Load database
deta = Deta(st.secrets["deta_key"])
db = deta.Base("mates")


@st.cache()
def load_stops():
    stops = pd.read_csv("data_gathering/output_data/slim_stops.csv")
    return stops


stops = load_stops()


def get_coords(location_name: str) -> Dict[str, float]:
    """Find associated coordinates to a location name."""
    stop = stops[stops["stop_name"] == location_name]
    return {"lon": stop["stop_lon"].iloc[0], "lat": stop["stop_lat"].iloc[0]}


def find_mates(coords: Dict[str, float], min_mates=5) -> pd.DataFrame:
    """Find mates that indicated a location near coords."""
    coords_vec = np.array([coords["lat"], coords["lon"]])
    all_mates = db.fetch().items
    all_mates_df = pd.DataFrame(all_mates)
    mates_position = np.array(all_mates_df[["lat", "lon"]])
    # Compute L1 distance to every other mate
    # We can do that because every point is very close (approximately a plane)
    # Compute a proper geodesic otherwise.
    mates_distances = np.linalg.norm((mates_position - coords_vec), ord=1, axis=1)
    # Select all top 5 closest mates
    min_indices = np.argpartition(mates_distances, min_mates - 1)[:min_mates]
    all_mates_df = all_mates_df.iloc[min_indices]
    # Compute proper meter distance for them
    all_mates_df["distance (km)"] = all_mates_df.apply(
        lambda x: geodesic(
            (x["lat"], x["lon"]),
            (coords["lat"], coords["lon"]),
            axis=1,
        ).km
    )
    return all_mates_df.iloc[min_indices][["name", "location_name", "distance (km)"]]


# Page

st.markdown("# Meet mates")

with st.form("form"):
    name = st.text_input("Your full name", placeholder="Lowis Douglas")
    location_name = st.selectbox(
        "Public transport station close to your home",
        options=stops["stop_name"],
    )
    submitted = st.form_submit_button("Search mates")
    st.markdown(
        "***By clicking on search mate, you agree to share the above info with other users.***"
    )

if submitted:
    has_data = True
    coords = get_coords(location_name)
    db.put(
        {
            "name": name,
            "location_name": location_name,
            "lon": coords["lon"],
            "lat": coords["lat"],
        }
    )
    mates = find_mates(coords)
    st.table(mates)
