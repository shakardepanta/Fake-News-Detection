from flask import Flask, render_template, request, jsonify
import re
import string
import joblib
from pymongo import MongoClient

app = Flask(__name__)

# Connect to MongoDB
client = MongoClient('mongodb://localhost:27017/')
db = client['fake_news_database']  
collection = db['classified_news']  

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

# Load machine learning models and vectorizer
LR = joblib.load('logistic_regression_model.pkl')
DT = joblib.load('decision_tree_model.pkl')
GB = joblib.load('gradient_boosting_model.pkl')
RF = joblib.load('random_forest_model.pkl')
vectorization = joblib.load('tfidf_vectorizer.pkl')

def manual_testing(text):
    # Preprocess input news
    text = wordopt(text)
    # Vectorize input news
    news_vectorized = vectorization.transform([text])
    # Make predictions
    pred_LR = LR.predict(news_vectorized)
    pred_DT = DT.predict(news_vectorized)
    pred_GB = GB.predict(news_vectorized)
    pred_RF = RF.predict(news_vectorized)

    sum = pred_LR[0] + pred_DT[0] + pred_GB[0] + pred_RF[0]

    if sum == 0 or sum == 1:
        result = "True News"
    else:
        result = "Fake News"

    return result

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/search-history')
def searchhistory():
    return render_template('search-history.html')

@app.route('/classify', methods=['POST'])
def classify_news():
    if request.method == "POST":  # Corrected method name

        data = request.form['news_text']
        result = manual_testing(data)
        # Save input text and classification result to MongoDB
        document = {'text': data, 'result': result}
        collection.insert_one(document)
        
        return jsonify({'result': result})
    
@app.route('/search-history', methods = ['GET'])
def get_search_history():
    page = int(request.args.get('page', 1))  # Get page number from query parameters (default to 1)
    page_size = int(request.args.get('page_size', 10))  # Get page size from query parameters (default to 10)

    skip = (page - 1) * page_size  # Calculate number of documents to skip
    search_history = list(collection.find({}, {'_id': 0}).skip(skip).limit(page_size))  # Fetch a subset of documents

    return jsonify(search_history)

if __name__ == '__main__':
    app.run(debug=True, port=8080)
