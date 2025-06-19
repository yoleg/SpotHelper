import pandas as pd

url = "https://wingsuit.world/dropzones/"
tables = pd.read_html(url)

# Assuming the first table is the one we want
dz_table = tables[0]

# Clean the table by removing rows with NaN in the 'Latitude' or 'Longitude' columns
