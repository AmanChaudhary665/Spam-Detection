import pandas as pd
import pickle
import nltk
import string

from nltk.corpus import stopwords
from nltk.stem import PorterStemmer

from sklearn.model_selection import train_test_split
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.naive_bayes import MultinomialNB
from sklearn.metrics import accuracy_score, classification_report


# --------------------------------------------------
# Download NLTK stopwords
# --------------------------------------------------
nltk.download("stopwords")

stop_words = set(stopwords.words("english"))
stemmer = PorterStemmer()


# --------------------------------------------------
# Text preprocessing
# --------------------------------------------------
def preprocess(text):
    text = str(text).lower()

    # Remove punctuation
    cleaned = ""

    for char in text:
        if char not in string.punctuation:
            cleaned += char

    # Split into words
    words = cleaned.split()

    # Remove stopwords
    words = [
        word for word in words
        if word not in stop_words
    ]

    # Apply stemming
    words = [
        stemmer.stem(word)
        for word in words
    ]

    return " ".join(words)


# --------------------------------------------------
# Load Dataset
# --------------------------------------------------

# This assumes the dataset looks like:
# ham    Hello, how are you?
# spam   Congratulations! You won a prize.
#
# where label and message are separated by a TAB.

df = pd.read_csv(
    "spam.csv",
    sep="\t",
    names=["label", "text"]
)


# --------------------------------------------------
# Clean Dataset
# --------------------------------------------------

df.dropna(subset=["label", "text"], inplace=True)

df["label"] = (
    df["label"]
    .astype(str)
    .str.strip()
    .str.lower()
)

# Keep only valid labels
df = df[df["label"].isin(["ham", "spam"])].copy()

# Convert labels to numbers
df["label"] = df["label"].map({
    "ham": 0,
    "spam": 1
})

print("\nDataset loaded successfully.")
print("Total messages:", len(df))
print("\nClass distribution:")
print(df["label"].value_counts())


# --------------------------------------------------
# Preprocess Messages
# --------------------------------------------------

print("\nPreprocessing messages...")

df["processed_text"] = df["text"].apply(preprocess)


# --------------------------------------------------
# Split Before TF-IDF
# --------------------------------------------------

X_train_text, X_test_text, y_train, y_test = train_test_split(
    df["processed_text"],
    df["label"],
    test_size=0.20,
    random_state=42,
    stratify=df["label"]
)


# --------------------------------------------------
# TF-IDF
# --------------------------------------------------

vectorizer = TfidfVectorizer()

X_train = vectorizer.fit_transform(X_train_text)
X_test = vectorizer.transform(X_test_text)


# --------------------------------------------------
# Train Model
# --------------------------------------------------

model = MultinomialNB()

model.fit(
    X_train,
    y_train
)


# --------------------------------------------------
# Evaluate Model
# --------------------------------------------------

predictions = model.predict(X_test)

accuracy = accuracy_score(
    y_test,
    predictions
)

print("\n--------------------------------")
print("MODEL EVALUATION")
print("--------------------------------")

print(f"Accuracy: {accuracy * 100:.2f}%")

print("\nClassification Report:")
print(
    classification_report(
        y_test,
        predictions,
        target_names=["Ham", "Spam"],
        zero_division=0
    )
)


# --------------------------------------------------
# Save Model
# --------------------------------------------------

with open("model.pkl", "wb") as file:
    pickle.dump(model, file)

with open("vectorizer.pkl", "wb") as file:
    pickle.dump(vectorizer, file)


print("--------------------------------")
print("Model saved successfully!")
print("--------------------------------")
print("Created: model.pkl")
print("Created: vectorizer.pkl")