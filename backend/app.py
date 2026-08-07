from fastapi.middleware.cors import CORSMiddleware
from hashlib import new

from fastapi import FastAPI
from pydantic import BaseModel
import joblib
import os
import pandas as pd

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class UsernameInput(BaseModel):
    username: str

# Find the backend folder
backend_dir = os.path.dirname(__file__)

# Load the trained model and scaler
model = joblib.load(os.path.join(backend_dir, "model.pkl"))
scaler = joblib.load(os.path.join(backend_dir, "scaler.pkl"))

dataset = pd.read_csv(
    os.path.join(os.path.dirname(backend_dir),
                 "dataset",
                 "top-instagram-influencers-data-cleaned.csv")
)

@app.get("/")
def home():
    return {
        "message": "Fake Influencer Detection API is running!"
    }

@app.post("/predict")
def predict(data: UsernameInput):
    username = data.username.lower()

    row = dataset[
        dataset["channel_info"].str.lower() == username
    ]

    if row.empty:
        return {
    "prediction": "NOT FOUND",
    "username": username,
    "followers": "N/A",
    "posts": "N/A",
    "avg_likes": "N/A"
}

    followers = float(str(row.iloc[0]["followers"]).replace("m", "000000").replace("k", "000"))
    posts = float(str(row.iloc[0]["posts"]).replace("k", "000"))
    avg_likes = float(str(row.iloc[0]["avg_likes"]).replace("m", "000000").replace("k", "000"))
    new_post_avg_like = float(str(row.iloc[0]["new_post_avg_like"]).replace("m", "000000").replace("k", "000"))

    input_data = [[
        followers,
        posts,
        avg_likes,
        new_post_avg_like
    ]]

    input_scaled = scaler.transform(input_data)
    prediction = model.predict(input_scaled)[0]

    if prediction == 1:
        result = "Genuine Influencer"
    else:
        result = "Fake Influencer"

    return {
    "username": row.iloc[0]["channel_info"],
    "followers": row.iloc[0]["followers"],
    "posts": row.iloc[0]["posts"],
    "avg_likes": row.iloc[0]["avg_likes"],
    "prediction": result
}