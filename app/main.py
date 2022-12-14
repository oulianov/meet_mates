import streamlit as st
import pandas as pd
import numpy as np
from deta import Deta
from typing import List, Dict
from geopy.distance import geodesic
import plotly.express as px
from functions import get_plotting_zoom_level_and_center_coordinates_from_lonlat_tuples

# Load database
deta = Deta(st.secrets["deta_key"])
db = deta.Base("mates")


# Load data
@st.cache()
def load_stops():
    stops = pd.read_csv("data_gathering/output_data/slim_stops.csv")
    return stops


stops = load_stops()


def get_coords(location_name: str) -> Dict[str, float]:
    """Find associated coordinates to a location name."""
    stop = stops[stops["stop_name"] == location_name]
    return {"lon": stop["stop_lon"].iloc[0], "lat": stop["stop_lat"].iloc[0]}


def find_mates(
    my_name: str,
    coords: Dict[str, float],
    min_mates=6,
) -> pd.DataFrame:
    """Find mates that indicated a location near coords."""
    coords_vec = np.array([coords["lat"], coords["lon"]])
    all_mates = db.fetch().items
    all_mates_df = pd.DataFrame(all_mates)
    # all_mates_df = all_mates_df[all_mates_df["name"] != my_name]
    mates_position = np.array(all_mates_df[["lat", "lon"]])
    # Compute L1 distance to every other mate
    # We can do that because every point is very close (approximately a plane)
    # Compute a proper geodesic otherwise.
    mates_distances = np.linalg.norm((mates_position - coords_vec), ord=1, axis=1)
    # Select all top 5 closest mates
    n = min(min_mates, all_mates_df.shape[0])
    min_indices = np.argpartition(mates_distances, n - 1)[:n]
    all_mates_df = all_mates_df.iloc[min_indices]
    # Compute proper meter distance for them
    all_mates_df["distance (km)"] = all_mates_df.apply(
        lambda x: geodesic(
            (x["lat"], x["lon"]),
            (coords["lat"], coords["lon"]),
        ).km,
        axis=1,
    )
    return all_mates_df


# Page

st.markdown(
    """# Meet mates & more!

This applet lets you discover mates that live near you."""
)

with st.form("form"):
    name = st.text_input(
        "Your full name",
        placeholder="Lowis Douglas",
        help="Other mates should be able to reach out to you by looking at your name",
    )
    st.info(
        "Click on the field below and type the name of a metro station near your home."
    )
    location_name = st.selectbox(
        "Public transport station close to your home",
        options=stops["stop_name"],
        help="Start typing to quickly find your station",
    )
    submitted = st.form_submit_button("Search mates")
    st.markdown(
        "*By clicking on search mate, you agree to share the above info with other users.*"
    )

if submitted and name.strip() == "":
    st.warning("Please enter your name!")

if submitted and name.strip() != "":
    coords = get_coords(location_name)
    # Push data to database
    # Mates are uniquely identified by their names. This allows impersonation, but the damages here are limited.
    db.put(
        {
            "name": name,
            "location_name": location_name,
            "lon": coords["lon"],
            "lat": coords["lat"],
        },
        key=name,
    )
    mates = find_mates(name, coords)
    st.markdown("## These mates live near you:")
    # Show a table with mates
    st.table(mates[mates["name"] != mates][["name", "location_name", "distance (km)"]])
    # Plot a map
    zoom, center = get_plotting_zoom_level_and_center_coordinates_from_lonlat_tuples(
        mates["lon"], mates["lat"]
    )
    fig = px.scatter_mapbox(
        mates,
        lat="lat",
        lon="lon",
        hover_name="name",
        hover_data=["location_name"],
        color_discrete_sequence=["black"],
        size=[6 for i in range(mates.shape[0])],
        zoom=zoom,
        center={"lat": center[1], "lon": center[0]},
    )
    fig.update_layout(mapbox_style="open-street-map")
    fig.update_layout(margin={"r": 0, "t": 0, "l": 0, "b": 0})
    st.plotly_chart(fig)

st.markdown(
    """---
*Made by [Nicolas O.](https://github.com/oulianov) with love and coffee ???*
"""
)
