# fake_influencer_final.py

import pandas as pd
import numpy as np
import os

from sklearn.model_selection import train_test_split, cross_val_score, StratifiedKFold
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, confusion_matrix, classification_report

from colorama import Fore, Style, init
from tabulate import tabulate
import matplotlib.pyplot as plt

init(autoreset=True)

# ===============================
# HELPER FUNCTION
# ===============================
def convert_to_number(value):
    if isinstance(value, str):
        value = value.lower().strip()
        if 'm' in value:
            return float(value.replace('m', '')) * 1_000_000
        elif 'k' in value:
            return float(value.replace('k', '')) * 1_000
        else:
            try:
                return float(value)
            except:
                return np.nan
    return value

# ===============================
# 1. LOAD DATA
# ===============================
dataset_path = os.path.join(
    os.path.dirname(__file__),
    "..",
    "dataset",
    "top-instagram-influencers-data-cleaned.csv"
)

df = pd.read_csv(dataset_path)

print(Fore.CYAN + "\n========== DATASET PREVIEW ==========")
print(tabulate(df.head(), headers='keys', tablefmt='fancy_grid'))

# ===============================
# 2. PREPROCESSING
# ===============================
df = df[['followers', 'posts', 'avg_likes', 'new_post_avg_like', '60_day_eng_rate']]
df.columns = ['followers', 'posts', 'avg_likes', 'new_post_avg_like', 'engagement_rate']

for col in ['followers', 'posts', 'avg_likes', 'new_post_avg_like']:
    df[col] = df[col].apply(convert_to_number)

df['engagement_rate'] = df['engagement_rate'].astype(str).str.replace('%', '').str.strip()
df['engagement_rate'] = pd.to_numeric(df['engagement_rate'], errors='coerce')

# ===============================
# 3. LABEL CREATION
# ===============================
df['likes_ratio'] = df['avg_likes'] / df['followers']
threshold = df['likes_ratio'].median()
df['label'] = (df['likes_ratio'] >= threshold).astype(int)

print(Fore.CYAN + "\n========== DATA WITH LABEL ==========")
print(tabulate(df.head(), headers='keys', tablefmt='fancy_grid'))

# ===============================
# 4. TRAIN TEST SPLIT
# ===============================
FEATURE_COLS = ['followers', 'posts', 'avg_likes', 'new_post_avg_like']

df = df.dropna(subset=FEATURE_COLS + ['label'])

X = df[FEATURE_COLS]
y = df['label']

X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.25, random_state=42, stratify=y
)

# ===============================
# 5. SCALING
# ===============================
scaler = StandardScaler()
X_train_scaled = scaler.fit_transform(X_train)
X_test_scaled = scaler.transform(X_test)

# ===============================
# 6. MODEL TRAINING
# ===============================
model = LogisticRegression(random_state=42)

cv = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)
cv_scores = cross_val_score(model, X_train_scaled, y_train, cv=cv)

model.fit(X_train_scaled, y_train)

import joblib

backend_dir = os.path.dirname(__file__)

joblib.dump(model, os.path.join(backend_dir, "model.pkl"))
joblib.dump(scaler, os.path.join(backend_dir, "scaler.pkl"))

print("Model saved successfully!")

print(Fore.GREEN + "\n========== MODEL TRAINING SUCCESSFUL ==========")

# ===============================
# 7. EVALUATION
# ===============================
y_pred = model.predict(X_test_scaled)

print(Fore.YELLOW + "\n========== CROSS VALIDATION ==========")
print("Scores:", cv_scores)
print("Mean Accuracy:", round(cv_scores.mean(), 4))

print(Fore.YELLOW + "\n========== TEST RESULTS ==========")
print("Accuracy:", round(accuracy_score(y_test, y_pred), 4))

print(Fore.YELLOW + "\nCONFUSION MATRIX:")
print(confusion_matrix(y_test, y_pred))

print(Fore.YELLOW + "\nCLASSIFICATION REPORT:")
print(classification_report(y_test, y_pred))

# ===============================
# 8. FAKE INFLUENCER ANALYSIS
# ===============================
print(Fore.RED + "\n========== FAKE INFLUENCER ANALYSIS ==========")

fake_acc = X_test[y_pred == 0].iloc[0]

followers = fake_acc['followers']
likes = fake_acc['avg_likes']
engagement = likes / followers

estimated_fake = int(followers * (1 - engagement))

print("ACCOUNT STATUS:", Fore.RED + "FAKE INFLUENCER ❌")
print("TOTAL FOLLOWERS:", int(followers))
print("ESTIMATED FAKE FOLLOWERS:", estimated_fake)

# ===============================
# 9. NEW ACCOUNT PREDICTION
# ===============================
print(Fore.GREEN + "\n========== NEW ACCOUNT PREDICTION ==========")

new_acc = pd.DataFrame([{
    'followers': 12000,
    'posts': 50,
    'avg_likes': 800,
    'new_post_avg_like': 600
}])

new_acc_scaled = scaler.transform(new_acc)
prediction = model.predict(new_acc_scaled)

if prediction[0] == 1:
    print("NEW ACCOUNT:", Fore.GREEN + "GENUINE INFLUENCER ✅")
else:
    print("NEW ACCOUNT:", Fore.RED + "FAKE INFLUENCER ❌")

# ===============================
# 10. GRAPH
# ===============================
print(Fore.CYAN + "\n========== VISUALIZATION ==========")

plt.bar(['Fake', 'Genuine'], [sum(y_pred==0), sum(y_pred==1)])
plt.title("Prediction Distribution")
plt.xlabel("Account Type")
plt.ylabel("Count")
plt.show()