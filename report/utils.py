import pickle
from pathlib import Path


# Absolute path to the root of this project
project_root = Path(__file__).resolve().parent.parent


# Path to assets/model.pkl
model_path = project_root / "assets" / "model.pkl"


def load_model():
    with model_path.open("rb") as file:
        model = pickle.load(file)

    return model