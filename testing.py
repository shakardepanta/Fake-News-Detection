import numpy as np
import pandas as pd
import re
import string
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.tree import DecisionTreeClassifier
from sklearn.ensemble import GradientBoostingClassifier, RandomForestClassifier
from sklearn.metrics import classification_report
import joblib

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

# Load models and vectorizer
LR = joblib.load('logistic_regression_model.pkl')
DT = joblib.load('decision_tree_model.pkl')
GB = joblib.load('gradient_boosting_model.pkl')
RF = joblib.load('random_forest_model.pkl')
vectorization = joblib.load('tfidf_vectorizer.pkl')  


def manual_testing(news):
    # Preprocess input news
    news = wordopt(news)
    # Vectorize input news
    news_vectorized = vectorization.transform([news])
    # Make predictions
    pred_LR = LR.predict(news_vectorized)
    pred_DT = DT.predict(news_vectorized)
    pred_GB = GB.predict(news_vectorized)
    pred_RF = RF.predict(news_vectorized)


    sum = pred_LR[0] + pred_DT[0] + pred_GB[0] + pred_RF[0]

    if sum == 0 or 1:
        result = "True News"
    else:
        result = "Fake News"


    return result


news = input("Insert News Text here: ")
print(manual_testing(news))
