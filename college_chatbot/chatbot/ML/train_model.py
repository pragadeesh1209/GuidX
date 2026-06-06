import pandas as pd
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.preprocessing import LabelEncoder
from sklearn.naive_bayes import MultinomialNB
import pickle
import os

# -------------------------------
# Step 1: Load CSVs
# -------------------------------
base_dir = os.path.dirname(__file__)
csv_files = [f for f in os.listdir(base_dir) if f.endswith('.csv')]
data_frames = []

for file in csv_files:
    file_path = os.path.join(base_dir, file)
    print(f"Loading {file}...")
    df = pd.read_csv(file_path)
    data_frames.append(df)

if not data_frames:
    raise FileNotFoundError("No CSV files found in ML directory!")

data = pd.concat(data_frames, ignore_index=True)

# -------------------------------
# Step 2: Check columns
# -------------------------------
print("Columns in CSV:", data.columns)

# Adjust column names here if needed:
# Example: your CSV might have 'tag' instead of 'tags'
if 'tags' in data.columns:
    label_col = 'tags'
elif 'tag' in data.columns:
    label_col = 'tag'
else:
    raise KeyError("CSV must have a 'tag' or 'tags' column")

# -------------------------------
# Step 3: Prepare data
# -------------------------------
X = data['patterns'].fillna('')  # text data
y = data[label_col]

# -------------------------------
# Step 4: Vectorize text
# -------------------------------
vectorizer = CountVectorizer()
X_vector = vectorizer.fit_transform(X)

# -------------------------------
# Step 5: Encode labels
# -------------------------------
label_encoder = LabelEncoder()
y_encoded = label_encoder.fit_transform(y)

# -------------------------------
# Step 6: Train model
# -------------------------------
model = MultinomialNB()
model.fit(X_vector, y_encoded)

# -------------------------------
# Step 7: Save model
# -------------------------------
model_file = os.path.join(os.path.dirname(__file__), 'chatbot_model.pkl')
with open(model_file, 'wb') as f:
    pickle.dump((vectorizer, label_encoder, model), f)

print("Model trained and saved successfully!")
print(f"Saved at: {model_file}")
