import sys
import threading
import random
import pandas as pd
from eventregistry import *
from threading import Lock

api_key = 'eda39267-9017-481a-860d-0b565c6d8bf3'
er = EventRegistry(apiKey=api_key)

global_df = pd.DataFrame()
mutex = Lock()

def get_articles(keywords):
    global global_df
    q = QueryArticlesIter(keywords=QueryItems.AND(keywords))
    q.setRequestedResult(RequestArticlesInfo(count=10, sortBy="sourceImportance"))

    local_df = pd.DataFrame()

    res = er.execQuery(q)
    for article in res['articles']['results']:
        data = {
            'source': article['source']['title'],
            'url': article['url']
        }
        local_df = pd.concat([local_df, pd.DataFrame(data, index=[0])])

    mutex.acquire()
    try:
        global_df = pd.concat([global_df, local_df])
    finally:
        mutex.release()

class MyThread(threading.Thread):
    def __init__(self, query):
        threading.Thread.__init__(self)
        self.query = query

    def run(self):
        get_articles(self.query)

def get_search_params(keywords):
    search_params = []
    while len(keywords) != 0:
        rm = random.sample(keywords, min(3, len(keywords)))
        search_params.append(rm)
        for word in rm:
            keywords.remove(word)
    return search_params

def get_keywords(user_url):
    url = user_url.decode('utf-8')
    article = article(url)
    article.download()
    article.parse()
    article.nlp()

    keywords = article.keywords
    kl = []
    for word in keywords:
        kl.append(word.encode('utf-8'))
    return kl

def web_scrape(url):
    global global_df
    kl = get_keywords(url)
    params = get_search_params(kl)

    threads = []

    for query in params:
        thread = MyThread(query)
        threads.append(thread)
        thread.start()

    for thread in threads:
        thread.join()

    global_df['id'] = range(len(global_df.index))
    global_df.to_csv('articles.csv', index=False)

def main(args):
    if len(args) < 2:
        print("Usage: python script.py <URL>")
        return
    web_scrape(args[1])

if __name__ == '__main__':
    main(sys.argv)

