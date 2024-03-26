import numpy as np
import pandas as pd
import re
import string
from sklearn.model_selection import train_test_split
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.tree import DecisionTreeClassifier
from sklearn.ensemble import GradientBoostingClassifier, RandomForestClassifier
from sklearn.metrics import classification_report
import joblib

data1 = pd.read_csv("WELFake_Dataset.csv")

# Preprocessing
def wordopt(text):
    if isinstance(text, float):  # Check if the value is a float
        return str(text)  # Convert float to string
    text = text.lower()
    text = re.sub('\[.*?\]', '', text)
    text = re.sub("\\W", " ", text)
    text = re.sub('https?://\S+|www\.\S+', '', text)
    text = re.sub('<.*?>+', '', text)
    text = re.sub('[%s]' % re.escape(string.punctuation), '', text)
    text = re.sub('\n', '', text)
    text = re.sub('\w*\d\w*', '', text)
    return text

data1['text'] = data1['text'].apply(wordopt)

# Splitting data
data1.rename(columns={'label':'class'}, inplace=True)
data = data1.dropna().sample(frac=1).reset_index(drop=True)
X = data['text']
y = data['class']
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.25)

# Vectorization
vectorization = TfidfVectorizer()
Xv_train = vectorization.fit_transform(X_train)
Xv_test = vectorization.transform(X_test)

# Save the vectorizer
joblib.dump(vectorization, 'tfidf_vectorizer.pkl')

# Training models
LR = LogisticRegression()
LR.fit(Xv_train, y_train)
joblib.dump(LR, 'logistic_regression_model.pkl')

DT = DecisionTreeClassifier()
DT.fit(Xv_train, y_train)
joblib.dump(DT, 'decision_tree_model.pkl')

GB = GradientBoostingClassifier(random_state=0)
GB.fit(Xv_train, y_train)
joblib.dump(GB, 'gradient_boosting_model.pkl')

RF = RandomForestClassifier(random_state=0)
RF.fit(Xv_train, y_train)
joblib.dump(RF, 'random_forest_model.pkl')

def manual_testing(news):
    # Load saved models
    LR = joblib.load('logistic_regression_model.pkl')
    DT = joblib.load('decision_tree_model.pkl')
    GB = joblib.load('gradient_boosting_model.pkl')
    RF = joblib.load('random_forest_model.pkl')

    # Preprocess input news
    news = wordopt(news)

    # Vectorize input news
    news_vectorized = vectorization.transform([news])

    # Make predictions
    pred_LR = LR.predict(news_vectorized)
    pred_DT = DT.predict(news_vectorized)
    pred_GB = GB.predict(news_vectorized)
    pred_RF = RF.predict(news_vectorized)

    return {
        "Logistic Regression Prediction": pred_LR[0],
        "Decision Tree Prediction": pred_DT[0],
        "Gradient Boosting Prediction": pred_GB[0],
        "Random Forest Prediction": pred_RF[0]
    }
