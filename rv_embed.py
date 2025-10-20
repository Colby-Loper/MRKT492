#imports
import pandas as pd
import numpy as np
import re
from sentence_transformers import SentenceTransformer
import hdbscan


#vars
file = "rv_rvws.csv"

df = pd.read_csv(file)
df_thor = df[df["make"].str.lower() == "thor motor coach"]

model = SentenceTransformer("all-MiniLM-L6-v2")

#preprocess and clean
def clean_rvw(text):
    text = text.lower()
    text = re.sub(r'[^a-z0-9\s\'.,!?-]', "", text )
    text = re.sub(r'\s+', ' ', text )
    return text

df_thor["clean_review"] = df_thor["review"].astype(str).apply(clean_rvw)
#embed
def embed(df):
    rvws = df["clean_review"].dropna().astype(str).tolist()
    embeddings = model.encode(rvws)

    return np.array(embeddings)

#cluster
def cluster(embeddings):
    c = hdbscan.HDBSCAN(
        min_cluster_size= 25,
        metric="euclidean",
        prediction_data= True,
    )
    c.fit(embeddings)

    probs = hdbscan.all_points_membership_vectors(c)

    df_prob = pd.DataFrame(probs, columns=[f"cluster {i}" for i in range([probs.shape[1]])])

    
    return None

#main
def main():
    embeddings = embed(df_thor)


if __name__ == "__main__":
    main()
