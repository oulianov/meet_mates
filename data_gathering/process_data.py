#%%

import pandas as pd

# %%

stops = pd.read_csv("data/emplacement-des-gares-idf.csv", sep=";")

# %%

stops["stop_lat"] = stops["Geo Point"].apply(lambda x: float(x.split(",")[0]))
stops["stop_lon"] = stops["Geo Point"].apply(lambda x: float(x.split(",")[1]))

# %%

slim_stops = stops.groupby("nom_lda").apply(lambda s: pd.Series({ 
    "stop_lon": s["stop_lon"].mean(), 
    "stop_lat": s["stop_lat"].mean(), 
    "lines": list(s["res_com"]), 
})).reset_index()

# %%
slim_stops["stop_name"] = slim_stops.apply(lambda x: f"{x['nom_lda']} ({' '.join(x['lines'])})", axis=1)

# %%

slim_stops = slim_stops[["stop_name", "stop_lon", "stop_lat"]]
slim_stops.drop_duplicates(subset=["stop_name"], inplace=True)
# %%
slim_stops.to_csv("output_data/slim_stops.csv")
# %%
