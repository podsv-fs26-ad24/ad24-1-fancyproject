import pandas as pd     
import numpy as np

df = pd.read_csv("../data/dataset.csv")

# clean up 
df = df.drop(columns=["Unnamed: 0"])
df = df.drop_duplicates(subset="track_id")

# define the audio features we care about
FEATURES = [
    "danceability", "energy", "valence", "acousticness",
    "instrumentalness", "speechiness", "liveness", "loudness", "tempo"
]

# QUESTION 1: Distribution of popularity
print("=" * 60)
print("Q1: POPULARITY DISTRIBUTION")
print("=" * 60)
print(df["popularity"].describe())
print(f"\nSongs with popularity = 0:     {(df['popularity'] == 0).sum():,}")
print(f"Songs with popularity 1–29:    {((df['popularity'] >= 1) & (df['popularity'] < 30)).sum():,}")
print(f"Songs with popularity 30–69:   {((df['popularity'] >= 30) & (df['popularity'] < 70)).sum():,}")
print(f"Songs with popularity 70–100:  {(df['popularity'] >= 70).sum():,}")
print(f"\nMedian popularity: {df['popularity'].median()}")
print(f"Mean popularity:   {df['popularity'].mean():.1f}")

# QUESTION 2: Which features correlate with popularity?
print("\n" + "=" * 60)
print("Q2: CORRELATION WITH POPULARITY")
print("=" * 60)
correlations = df[FEATURES + ["popularity"]].corr()["popularity"].drop("popularity")
correlations_sorted = correlations.abs().sort_values(ascending=False)
print("\nCorrelation with popularity (sorted by strength):")
for feat in correlations_sorted.index:
    r = correlations[feat]
    direction = "↑ more popular" if r > 0 else "↓ less popular"
    print(f"  {feat:<20} r = {r:+.3f}   ({direction})")

# feature-to-feature correlation matrix (for heatmap later)
feat_corr = df[FEATURES].corr().round(3)
print("\nFeature correlation matrix (top pairs):")
# Show only the strongest cross-correlations
pairs = []
for i, f1 in enumerate(FEATURES):
    for j, f2 in enumerate(FEATURES):
        if j > i:
            pairs.append((f1, f2, feat_corr.loc[f1, f2]))
pairs.sort(key=lambda x: abs(x[2]), reverse=True)
for f1, f2, r in pairs[:8]:
    print(f"  {f1} ↔ {f2}: r = {r:+.3f}")

# QUESTION 3: How do genres differ?
print("\n" + "=" * 60)
print("Q3: GENRE DIFFERENCES")
print("=" * 60)

# How many genres and songs per genre?
print(f"\nTotal genres: {df['track_genre'].nunique()}")
print(f"\nSongs per genre (sample):")
print(df["track_genre"].value_counts().head(10))

# pick 6 representative genres for the report
FOCUS_GENRES = ["pop", "rock", "hip-hop", "classical", "metal", "jazz"]
genre_df = df[df["track_genre"].isin(FOCUS_GENRES)]

print(f"\nMean audio features by genre:")
genre_means = genre_df.groupby("track_genre")[FEATURES].mean().round(3)
print(genre_means.to_string())

print(f"\nMean popularity by genre:")
pop_by_genre = df.groupby("track_genre")["popularity"].mean().sort_values(ascending=False)
print(pop_by_genre.head(15))
print("...")
print(pop_by_genre.tail(5))

# QUESTION 4: What do hits vs non-hits sound like?
print("\n" + "=" * 60)
print("Q4: HITS VS NON-HITS")
print("=" * 60)

p90 = df["popularity"].quantile(0.90)
p10 = df["popularity"].quantile(0.10)
print(f"\nTop 10% threshold (hits):     popularity >= {p90}")
print(f"Bottom 10% threshold (misses): popularity <= {p10}")

hits    = df[df["popularity"] >= p90]
nonhits = df[df["popularity"] <= p10]
print(f"Number of hits:     {len(hits):,}")
print(f"Number of non-hits: {len(nonhits):,}")

print(f"\nMean feature values — HITS vs NON-HITS:")
comparison = pd.DataFrame({
    "hits":     hits[FEATURES].mean(),
    "non_hits": nonhits[FEATURES].mean(),
})
comparison["difference"] = comparison["hits"] - comparison["non_hits"]
comparison["direction"]  = comparison["difference"].apply(
    lambda x: "hits HIGHER ↑" if x > 0 else "hits LOWER ↓"
)
print(comparison.round(3).to_string())

# QUESTION 4b: Mood map — valence + energy by genre
print("\n" + "=" * 60)
print("Q4b: MOOD MAP — VALENCE + ENERGY BY GENRE")
print("=" * 60)
mood = df.groupby("track_genre")[["valence", "energy"]].mean().round(3)
mood["mood_quadrant"] = mood.apply(lambda row:
    "Happy & Energetic" if row.valence >= 0.5 and row.energy >= 0.5 else
    "Happy & Calm"      if row.valence >= 0.5 and row.energy < 0.5  else
    "Sad & Energetic"   if row.valence < 0.5  and row.energy >= 0.5 else
    "Sad & Calm", axis=1
)
print("\nAll genres with their mood quadrant:")
print(mood.sort_values("valence", ascending=False).to_string())

print("\nQuadrant summary:")
print(mood["mood_quadrant"].value_counts())

print("\nFocus genres mood positions:")
print(mood.loc[mood.index.isin(FOCUS_GENRES)].to_string())