import string, requests, joblib, re
import numpy as np
from bs4 import BeautifulSoup


def wordopt(text):
    if isinstance(text, float):  
        return str(text)  
    text = text.lower()
    text = re.sub('\[.*?\]', '', text)
    text = re.sub("\\W", " ", text)
    text = re.sub('https?://\S+|www\.\S+', '', text)
    text = re.sub('<.*?>+', '', text)
    text = re.sub('[%s]' % re.escape(string.punctuation), '', text)
    text = re.sub('\n', '', text)
    text = re.sub('\w*\d\w*', '', text)
    return text


def scrape_news_text(url):
    # Send a GET request to the URL
    response = requests.get(url)
    
    # Parse HTML content
    soup = BeautifulSoup(response.content, 'html.parser')
    
    # Find all paragraphs containing the news text
    paragraphs = soup.find_all('p')
    
    # Print out the text
    for index, paragraph in enumerate(paragraphs[1:-1], start=1):
        return(paragraph.text)

def manual_testing_link(news):
    # Load saved models
    LR = joblib.load('C:\\Users\\Asus\\College\\Final Year Project\\FND\\link_ml\\logistic_regression_model.pkl')
    DT = joblib.load('C:\\Users\\Asus\\College\\Final Year Project\\FND\link_ml\\decision_tree_model.pkl')
    GB = joblib.load('C:\\Users\\Asus\\College\\Final Year Project\\FND\\link_ml\\gradient_boosting_model.pkl')
    RF = joblib.load('C:\\Users\\Asus\\College\\Final Year Project\\FND\\link_ml\\random_forest_model.pkl')
    vectorization = joblib.load('C:\\Users\\Asus\\College\\Final Year Project\\FND\\link_ml\\tfidf_vectorizer.pkl')

    # Preprocess input news
    news = wordopt(news)

    # Vectorize input news
    news_vectorized = vectorization.transform([news])

    # Make predictions
    pred_LR = LR.predict(news_vectorized)
    pred_DT = DT.predict(news_vectorized)
    pred_GB = GB.predict(news_vectorized)
    pred_RF = RF.predict(news_vectorized)

    predp_LR = LR.predict_proba(news_vectorized)
    predp_DT = DT.predict_proba(news_vectorized)
    predp_GB = GB.predict_proba(news_vectorized)
    predp_RF = RF.predict_proba(news_vectorized)

    sum = pred_LR[0] + pred_DT[0] + pred_GB[0] + pred_RF[0]

    if sum == 0 or sum == 1:
        result = "Fake News"
    else:
        result = "True News"

    return result 

def manual_testing(news):
    # Load saved models
    LR = joblib.load('C:\\Users\\Asus\\College\\Final Year Project\\FND\\logistic_regression_model.pkl')
    DT = joblib.load('C:\\Users\\Asus\\College\\Final Year Project\\FND\\decision_tree_model.pkl')
    GB = joblib.load('C:\\Users\\Asus\\College\\Final Year Project\\FND\\gradient_boosting_model.pkl')
    RF = joblib.load('C:\\Users\\Asus\\College\\Final Year Project\\FND\\random_forest_model.pkl')
    vectorization = joblib.load('C:\\Users\\Asus\\College\\Final Year Project\\FND\\tfidf_vectorizer.pkl')

    # Preprocess input news
    news = wordopt(news)

    # Vectorize input news
    news_vectorized = vectorization.transform([news])

    # Make predictions
    pred_LR = LR.predict(news_vectorized)
    pred_DT = DT.predict(news_vectorized)
    pred_GB = GB.predict(news_vectorized)
    pred_RF = RF.predict(news_vectorized)

    # Aggregate predictions
    sum_predictions = np.sum([pred_LR[0], pred_DT[0], pred_GB[0], pred_RF[0]])
    
    # Determine the result based on the sum of predictions
    if sum_predictions >= 3:  
        result = "Fake News"
    else:
        result = "True News"

    # Calculate the average prediction probabilities for more precise accuracy reporting
    predp_LR = LR.predict_proba(news_vectorized)
    predp_DT = DT.predict_proba(news_vectorized)
    predp_GB = GB.predict_proba(news_vectorized)
    predp_RF = RF.predict_proba(news_vectorized)

    avg_pred_proba = (predp_LR + predp_DT + predp_GB + predp_RF) / 4

    if result == "Fake News":
        pred_percent = avg_pred_proba[0][1] * 100  
    else:
        pred_percent = avg_pred_proba[0][0] * 100  

    if pred_percent <= 50:
        return f"{result} with {pred_percent:.2f}% accuracy"
    else:
        return f"{result} with {pred_percent:.2f}% accuracy"
    