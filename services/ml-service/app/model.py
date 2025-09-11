import os
import joblib
import pandas as pd
from sklearn.pipeline import Pipeline
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split

MODEL_PATH = os.getenv("MODEL_PATH", "model.joblib")

# Compute absolute path to the sample data so it works in GitHub Actions too
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_FILE = os.path.normpath(os.path.join(BASE_DIR, "..", "data", "sample_expenses.csv"))

CATEGORIES = ["Coffee", "Groceries", "Transport", "Dining", "Shopping", "Bills", "Other"]

def load_or_train():
    if os.path.exists(MODEL_PATH):
        return joblib.load(MODEL_PATH)

    # Tiny sample dataset
    df = pd.read_csv(DATA_FILE)
    X = df["text"]
    y = df["label"]

    pipe = Pipeline([
        ("tfidf", TfidfVectorizer(ngram_range=(1, 2), min_df=1)),
        ("clf", LogisticRegression(max_iter=500)),
    ])
    pipe.fit(X, y)
    joblib.dump(pipe, MODEL_PATH)
    return pipe

MODEL = load_or_train()

def predict_category(text: str) -> str:
    try:
        cat = MODEL.predict([text])[0]
        if cat not in CATEGORIES:
            return "Other"
        return str(cat)
    except Exception:
        return "Other"

