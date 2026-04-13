import pandas as pd
import numpy as np

df = pd.read_csv("../data/dataset.csv")
df = df.drop(columns=["Unnamed: 0"])
df = df.drop_duplicates(subset="track_id")

FEATURES = [
    "danceability", "energy", "valence", "acousticness",
    "instrumentalness", "speechiness", "liveness", "loudness", "tempo"
]

# output folder — saves all CSV files into the project
OUT = "/Users/charlottewindlin/4.Semester/PODSV/ad24-1-fancyproject/data/"

import os
os.makedirs(OUT, exist_ok=True)

# Chart 1: Popularity histogram
pop_counts = df["popularity"].value_counts().sort_index().reset_index()
pop_counts.columns = ["popularity_score", "number_of_songs"]
pop_counts.to_csv(OUT + "chart1_popularity_distribution.csv", index=False)
print("Chart 1 saved — popularity distribution")
print(pop_counts.head())

# Chart 2: Correlation with popularity
correlations = df[FEATURES + ["popularity"]].corr()["popularity"].drop("popularity")
corr_df = correlations.reset_index()
corr_df.columns = ["feature", "correlation_with_popularity"]
corr_df = corr_df.sort_values("correlation_with_popularity", ascending=False)
corr_df.to_csv(OUT + "chart2_correlations.csv", index=False)
print("\n Chart 2 saved — correlations")
print(corr_df)

# Chart 3: Genre radar — mean features per genre
# Normalize loudness to 0-1 scale so all features are comparable on radar
df["loudness_norm"] = (df["loudness"] - df["loudness"].min()) / (df["loudness"].max() - df["loudness"].min())
df["tempo_norm"]    = (df["tempo"] - df["tempo"].min()) / (df["tempo"].max() - df["tempo"].min())

RADAR_FEATURES = [
    "danceability", "energy", "valence", "acousticness",
    "instrumentalness", "speechiness", "liveness", "loudness_norm", "tempo_norm"
]

FOCUS_GENRES = ["pop", "rock", "hip-hop", "classical", "metal", "jazz"]
genre_df = df[df["track_genre"].isin(FOCUS_GENRES)]
radar = genre_df.groupby("track_genre")[RADAR_FEATURES].mean().round(3)
radar.to_csv(OUT + "chart3_genre_radar.csv")
print("\n Chart 3 saved — genre radar")
print(radar)

 
# Chart 4: Hits vs non-hits
p90 = df["popularity"].quantile(0.90)
p10 = df["popularity"].quantile(0.10)

hits    = df[df["popularity"] >= p90]
nonhits = df[df["popularity"] <= p10]

hits_means    = hits[FEATURES].mean().round(3)
nonhits_means = nonhits[FEATURES].mean().round(3)

hits_vs = pd.DataFrame({
    "group": ["hits (top 10%)", "non-hits (bottom 10%)"],
    **{feat: [hits_means[feat], nonhits_means[feat]] for feat in FEATURES}
})
hits_vs.to_csv(OUT + "chart4_hits_vs_nonhits.csv", index=False)
print("\n Chart 4 saved — hits vs non-hits")
print(hits_vs.to_string())

# Chart 5: Mood map — valence + energy per genre (all genres)
mood = df.groupby("track_genre")[["valence", "energy", "popularity"]].mean().round(3)
mood = mood.reset_index()
mood.columns = ["genre", "valence", "energy", "mean_popularity"]
mood.to_csv(OUT + "chart5_mood_map.csv", index=False)
print("\n Chart 5 saved — mood map")
print(mood.head(10))

print("\n All chart data saved to", OUT)