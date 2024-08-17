
from flask import redirect, render_template, request, url_for, current_app, flash, jsonify, url_for
from flask_login import current_user, login_required
import requests, json
from pymongo import MongoClient

mongo_client = MongoClient('mongodb://localhost:27017/')
mongo_db = mongo_client['fake_news_detection']
subscriptions_collection = mongo_db['subscription']

def khalti_api():
    

    return 1    
    

def payment_complete():
      # Verify payment using the Lookup API
        pidx = request.args.get('pidx')
        lookup_url = "https://a.khalti.com/api/v2/epayment/lookup/"
        lookup_payload = {"pidx": pidx}
        headers = {
            'Authorization': 'Key 7be81d02fa6c45288a22c0cd0e92a6a1',
            'Content-Type': 'application/json',
        }
        
        response = requests.post(lookup_url, headers=headers, data=json.dumps(lookup_payload))
        data = response.json()
        
        if data['status'] == 'Completed':
            # Mark the user as paid
            subscriptions_collection.update_one(
                {'user_id': current_user.id},
                {'$set': {'has_paid': True}},
                upsert=True
            )
            flash('Payment successful! You now have access.')
            return redirect(url_for('main.project_x'))
        else:
            flash('Payment verification failed. Please contact support.')
            return redirect(url_for('main.paywall'))