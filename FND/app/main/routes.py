from datetime import datetime, timezone
import markdown
import nh3
import sqlalchemy as sa
from flask import redirect, render_template, request, url_for, current_app, flash, jsonify, url_for
from flask_login import current_user, login_required
from app.main.fnd import wordopt, manual_testing_link, manual_testing
from app import db
from app.main import bp
from app.main.forms import PostForm, ThreadForm, ReportForm, DeletePostForm
from app.models import User, Post, Thread, Report
from pymongo import MongoClient
from bs4 import BeautifulSoup
import requests, json


mongo_client = MongoClient('mongodb://localhost:27017/')
mongo_db = mongo_client['fake_news_detection']
subscriptions_collection = mongo_db['subscription']


md = markdown.Markdown(extensions=['mdx_math'],
                       extension_configs={
                           'mdx-math': {'enable_dollar_delimiter': True}
                       })    

@bp.before_request
def before_request():
    if current_user.is_authenticated:
        current_user.last_seen = datetime.now(timezone.utc)
        db.session.commit()


@bp.route('/explore')
@bp.route('/index')
@bp.route('/')
def index():
    page = request.args.get('page', 1, type=int)

    threads_query = sa.select(Thread)
    page = db.paginate(threads_query, page=page, per_page=current_app.config['THREADS_PER_PAGE'], error_out=True)

    return render_template('index.html', title='Home', page=page)


@bp.route('/new_thread', methods=['GET', 'POST'])
@login_required
def new_thread():
    form = ThreadForm()
    if form.validate_on_submit():
        thread = Thread(title=form.title.data, user_id=current_user.id)
        db.session.add(thread)
        db.session.commit()

        raw = form.body.data
        text = markdown_to_html(raw)
        post = Post(body=text, body_raw=raw, user_id=current_user.id, thread_id=thread.id)
        db.session.add(post)
        db.session.commit()
        return redirect(url_for('main.thread', id=thread.id))
    return render_template('new_thread.html', title='New Thread', form=form)


@bp.route('/thread/<int:id>/', methods=['GET'])
def thread(id):
    page = request.args.get('page', 1, type=int)
    thread = db.first_or_404(sa.select(Thread).where(Thread.id == id))
    posts_query = sa.select(Post).where(Post.thread_id == id).order_by(Post.timestamp.desc())
    page = db.paginate(posts_query, page=page, per_page=current_app.config['POSTS_PER_PAGE'], error_out=True)

    form = PostForm()

    return render_template('thread.html', title=thread.title,
                           thread=thread,
                           form=form,
                           page=page)


@bp.route('/user/<username>/', methods=['GET'])
def user(username):
    user = db.first_or_404(sa.select(User).where(User.username == username))
    return render_template('user.html', user=user)


@bp.route('/search', methods=['GET'])
def search():
    page = request.args.get('page', 1, type=int)
    query = request.args.get('query', '', type=str)

    keywords = query.split(' ')
    keyword_filters = [Thread.title.ilike(f'%{k}%') for k in keywords]
    threads_query = sa.select(Thread).where(sa.and_(*keyword_filters))
    page = db.paginate(threads_query, page=page, per_page=current_app.config['THREADS_PER_PAGE'], error_out=True)

    return render_template('search.html', title='Search', query=query, page=page)

@bp.route('/post/add/<int:thread>/', methods=['POST'])
@login_required
def new_post(thread):
    form = PostForm()

    if form.validate_on_submit():
        raw = form.body.data
        text = markdown_to_html(raw)
        post = Post(body=text, body_raw=raw, user_id=current_user.id, thread_id=thread)
        db.session.add(post)
        db.session.commit()
    return redirect(url_for('main.thread', id=thread))

@bp.route('/post/edit/<int:id>', methods=['GET', 'POST'])
def edit_post(id):
    post = Post.query.get_or_404(id)

    if current_user.id != post.author.id:
        flash('You are not authorized to edit that post!')
        return redirect(url_for('main.index'))

    form = PostForm()
    if form.validate_on_submit():
        text = markdown_to_html(form.body.data)
        post.body = text
        post.body_raw = form.body.data

        db.session.commit()
        flash('Your changes have been saved.')
        return redirect(url_for('main.thread', id=post.thread_id))
    elif request.method == 'GET':
        form.body.data = post.body_raw
    return render_template('edit_post.html', title='Edit Post', form=form)


@bp.route('/post/delete/<int:id>', methods=['GET', 'POST'])
@login_required
def delete_post(id):
    post_to_delete = Post.query.get_or_404(id)
    thread = post_to_delete.thread

    if current_user.id != post_to_delete.author.id and not current_user.admin:
        flash('You are not authorized to delete that post!')
        return redirect(url_for('main.index'))

    form = DeletePostForm()
    if form.validate_on_submit():
        if thread.posts_count() == 1:
            db.session.delete(post_to_delete)
            db.session.delete(thread)
            db.session.commit()
            flash('Post and thread deleted!')
            return redirect(url_for('main.index'))
        else:
            db.session.delete(post_to_delete)
            db.session.commit()
            flash('Post deleted!')
            return redirect(url_for('main.thread', id=thread.id))

    return render_template('delete_post.html', post=post_to_delete, form=form)

@bp.route('/fake-news-detection', methods=['GET', 'POST'])
def fake_news_detection():
    result = None
    if request.method == 'POST':
        # Get text and link inputs from the form
        news_text = request.form.get('news_text')
        news_link = request.form.get('news_link')
        
        # Determine which input was provided and process it
        if news_text:
            result = manual_testing(news_text)
        elif news_link:
            result = manual_testing_link(news_link)
        else:
            result = 'No text or link provided'
    
    return render_template('fake_news_detection.html', title='Fake News Detection', result=result)

@bp.route('/post/report/<int:id>', methods=['GET', 'POST'])
def report(id):
    post = Post.query.get_or_404(id)

    if current_user.is_authenticated and current_user.id == post.author.id:
        flash('You can not report your own post!')
        return redirect(url_for('main.index'))

    form = ReportForm()
    if form.validate_on_submit():
        report = Report(reason=form.reason.data, post_id=id)
        db.session.add(report)
        db.session.commit()

        flash('Post reported!')
        return redirect(url_for('main.index'))
    return render_template('report.html', post=post, form=form)

def markdown_to_html(markdown_text):
    return nh3.clean(md.convert(markdown_text))

# Paywall logic inside your project_x route
@bp.route('/project_x', methods=['GET'])
@login_required
def project_x():
    # Check if the user has a valid subscription
    subscription = subscriptions_collection.find_one({'user_id': current_user.id})
    
    if not subscription or not subscription.get('has_paid'):
        flash('You need to subscribe to access this content.')
        return redirect(url_for('main.paywall'))
    
    return redirect('http://127.0.0.1:1338/')

@bp.route('/paywall', methods=['GET', 'POST'])
def paywall():
    if request.method == 'POST':
        url = "https://a.khalti.com/api/v2/epayment/initiate/"
        payload = {
            "return_url": url_for('main.khalti_callback', _external=True),
            "website_url": "http://127.0.0.1:5000/",
            "amount": 1000,  # Amount in paisa (1000 paisa = 10 NPR)
            "purchase_order_id": "FND",
            "purchase_order_name": "Premium Access",
            "customer_info": {
                "name": current_user.username,  # Use actual user's name
                "email": current_user.email,
                "phone": "986942969"        
            }
        }
        
        headers = {
            'Authorization': 'Key 7be81d02fa6c45288a22c0cd0e92a6a1',  # Live secret key
            'Content-Type': 'application/json',
        }
        
        try:
            response = requests.post(url, headers=headers, data=json.dumps(payload))
            response.raise_for_status()
            data = response.json()
            
            print("Khalti API Response:", data)
            
            if response.status_code == 200 and 'payment_url' in data:
                return redirect(data['payment_url'])
            else:
                flash(f'Error initiating payment: {data.get("detail", "Unknown error")}')
        except requests.exceptions.RequestException as e:
            print(f'Request failed: {e}')
            flash('Error initiating payment. Please check the server logs for more details.')
        
        return redirect(url_for('main.paywall'))
    
    return render_template('paywall.html')

@bp.route('/khalti_callback')
def khalti_callback():
    pidx = request.args.get('pidx')
    status = request.args.get('status')
    
    if status == 'Completed':
        # Verify payment using the Lookup API
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
    
    flash('Payment not completed. Please try again.')
    return redirect(url_for('main.paywall'))
