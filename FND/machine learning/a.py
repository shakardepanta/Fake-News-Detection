
import string
import numpy as np
import re
import joblib


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

    if result == "True News":
        pred_percent = avg_pred_proba[0][1] * 100  # Probability of being "Fake News"
    else:
        pred_percent = avg_pred_proba[0][0] * 100  # Probability of being "True News"

    return pred_LR[0], pred_DT[0], pred_GB[0], pred_RF[0]

print(manual_testing("""The Ministry of Home Affairs has asked transport entrepreneurs to implement the recommendations of the task force formed to investigate the Simaltal incident.

In a letter addressed to the Federation of Nepalese National Transport Entrepreneurs, the ministry has asked the transport operators to install GPS tracking systems and devices in all vehicles so as to control their speed.

Additionally, the ministry has urged them for regular vehicle maintenance and inspections, phasing out old and unfit vehicles, and installing CCTV cameras and transponders. As per the recommendations, drivers should receive regular training on safe driving practices, adhere to traffic rules, and prevent driving under the influence of alcohol.

The ministry has also asked that long-route buses have at least two drivers who can drive the vehicle by turn and that a code of conduct for transport operators and workers be developed and enforced. Furthermore, third-party insurance must be made mandatory for all vehicles operating in the country.

Public transport operators are urged to make sure that passengers travel only after purchasing a ticket and develop and implement an online ticketing system. They must also ensure that passengers carry identification documents for verification in case of any incidents.

On July 12, two buses carrying more than 60 passengers were caught in a landslide on the Narayanghat-Mugling road section and swept away by the Trishuli river. Three passengers managed to get out of the vehicle and swim to safety.

A five-member task force led by Joint Secretary Chhabi Rijal of the Ministry of Home Affairs investigated the incident and submitted its report with recommendations to Home Minister Ramesh Lekhak on August 6.  """))