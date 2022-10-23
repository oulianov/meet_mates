#%%

import pandas as pd

# %%

stops = pd.read_csv("data/fr-idf_ntfs/stops.txt")
# %%

lines = pd.read_csv("data/fr-idf_ntfs/lines.txt")
# %%

slim_stops = stops[["stop_name", "stop_lon", "stop_lat"]]
# %%
slim_stops.to_csv("output_data/slim_stops.csv")
# %%
