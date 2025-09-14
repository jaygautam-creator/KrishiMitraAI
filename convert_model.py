import pickle
from joblib import dump, load

with open("crop_model.pkl", "rb") as f:
    model = pickle.load(f)

# Save as joblib
dump(model, "crop_model.joblib")

# Load back
model = load("crop_model.joblib")
