import os
os.system("playwright install chromium")
import streamlit as st
from playwright.sync_api import sync_playwright
import requests
import json
import re
from requests import session
from bs4 import BeautifulSoup
import pandas as pd
from datetime import datetime, timedelta
from latest_user_agents import get_random_user_agent
from sqlalchemy import create_engine, text
import cloudscraper
from dateutil import tz
import dateutil.parser
from dateutil import tz, parser
import pytz
eastern_tz = pytz.timezone('US/Eastern')

hostname=st.secrets['hostname']
dbname=st.secrets['dbname']
uname=st.secrets['uname']
pwd=st.secrets['pwd']

post_item_list =[]
item_list = []

def remove_period(text):
    # Split the text into words
    words = text.split()
    
    # Remove any periods between the first 5 words
    for i in range(min(len(words), 5)):
        words[i] = words[i].replace('.', '')
    
    # Join the modified words back into a string
    return ' '.join(words)

def add_up(data, url, link, header, sentence, my_date, image_url='None', author_name=None, author_number = 1):
    if author_name is not None:
        author_twitter = str(data.loc[(data['Author Name'] == author_name), 'Author Twitter'].iloc[0]).replace('"', '')
        pub_twitter = str(data.loc[(data['Author Name'] == author_name), 'Publication Twitter'].iloc[0]).replace('"', '')
        author_fb = str(data.loc[(data['Author Name'] == author_name), 'Author FB'].iloc[0]).replace('"', '')
        pub_fb = str(data.loc[(data['Author Name'] == author_name), 'Publication FB'].iloc[0]).replace('"', '')
        author_ig = str(data.loc[(data['Author Name'] == author_name), 'Author IG'].iloc[0]).replace('"', '')
        pub_ig = str(data.loc[(data['Author Name'] == author_name), 'Publication IG'].iloc[0]).replace('"', '')
        author_linkedin = str(data.loc[(data['Author Name'] == author_name), 'Author LinkedIn'].iloc[0]).replace('"', '')
        pub_linkedin = str(data.loc[(data['Author Name'] == author_name), 'Publication LinkedIn'].iloc[0]).replace('"', '')
        paywall = str(data.loc[(data['Author Name'] == author_name), 'Default Paywall  (Y/N)'].iloc[0]).replace('"', '')
        pub_name = str(data.loc[(data['Author Name'] == author_name), 'Publication Name'].iloc[0]).replace('"', '')

        if 'None' in author_twitter:
            author_twitter = author_name
        if 'None' in pub_twitter:
            pub_twitter = pub_name
        if 'None' in author_fb:
            author_fb = author_name
        if 'None' in pub_fb:
            pub_fb = pub_name
        if 'None' in author_ig:
            author_ig = author_name
        if 'None' in pub_ig:
            pub_ig = pub_name
        if 'None' in author_linkedin:
            author_linkedin = author_name
        if 'None' in pub_linkedin:
            pub_linkedin = pub_name
    else:
        author_twitter = str(data.loc[data['Article URL'] == url, 'Author Twitter'].iloc[0]).replace('"', '')
        pub_twitter = str(data.loc[data['Article URL'] == url, 'Publication Twitter'].iloc[0]).replace('"', '')
        author_fb = str(data.loc[data['Article URL'] == url, 'Author FB'].iloc[0]).replace('"', '')
        pub_fb = str(data.loc[data['Article URL'] == url, 'Publication FB'].iloc[0]).replace('"', '')
        author_ig = str(data.loc[data['Article URL'] == url, 'Author IG'].iloc[0]).replace('"', '')
        pub_ig = str(data.loc[data['Article URL'] == url, 'Publication IG'].iloc[0]).replace('"', '')
        author_linkedin = str(data.loc[data['Article URL'] == url, 'Author LinkedIn'].iloc[0]).replace('"', '')
        pub_linkedin = str(data.loc[data['Article URL'] == url, 'Publication LinkedIn'].iloc[0]).replace('"', '')
        paywall = str(data.loc[data['Article URL'] == url, 'Default Paywall  (Y/N)'].iloc[0]).replace('"', '')  
        pub_name = str(data.loc[(data['Article URL'] == url), 'Publication Name'].iloc[0]).replace('"', '')     

        if 'None' in author_twitter:
            author_twitter = str(data.loc[data['Article URL'] == url, 'Author Name'].iloc[0]).replace('"', '')
        if 'None' in pub_twitter:
            pub_twitter = str(data.loc[data['Article URL'] == url, 'Publication Name'].iloc[0]).replace('"', '')

        if 'None' in author_fb:
            author_fb = str(data.loc[data['Article URL'] == url, 'Author Name'].iloc[0]).replace('"', '')
        if 'None' in pub_fb:
            pub_fb = str(data.loc[data['Article URL'] == url, 'Publication Name'].iloc[0]).replace('"', '')

        if 'None' in author_ig:
            author_ig = str(data.loc[data['Article URL'] == url, 'Author Name'].iloc[0]).replace('"', '')
        if 'None' in pub_ig:
            pub_ig = str(data.loc[data['Article URL'] == url, 'Publication Name'].iloc[0]).replace('"', '')

        if 'None' in author_linkedin:
            author_linkedin = str(data.loc[data['Article URL'] == url, 'Author Name'].iloc[0]).replace('"', '')
        if 'None' in pub_linkedin:
            pub_linkedin = str(data.loc[data['Article URL'] == url, 'Publication Name'].iloc[0]).replace('"', '')

    if 'N' in paywall:
        paywall = ' '
    elif 'Y' in paywall:
        paywall = '<$>'
        
    sentence = sentence.encode('utf-8').decode('utf-8').replace('“', '').replace('”', '').replace('$', '')

    post = f'''
    '{header}' by {author_twitter} for {pub_twitter}: {sentence}... {paywall} {link} Twit($)ter
    '''
    post_key = f'Post {link} for Twit($)ter'
    post_item = {
        'Text': post.strip(),
        'Date': my_date,
        'Post Link': link,
        'Post key': post_key,
        'Number of Bylines': author_number,
        'Image url': image_url
    }
    post_item_list.append(post_item)

    post = f'''
    '{header}' by {author_fb} for {pub_fb}: {sentence}... {paywall} {link} Face($)book
    '''
    post_key = f'Post {link} for Face($)book'
    post_item = {
        'Text': post.strip(),
        'Date': my_date,
        'Post Link': link,
        'Post key': post_key,
        'Number of Bylines': author_number,
        'Image url': image_url
    }
    post_item_list.append(post_item)

    post = f'''
    '{header}' by {author_ig} for {pub_ig}: {sentence}... {paywall} {link} I($)G

👉VISIT THE LINK IN OUR BIO TO READ THIS ARTICLE⚾️
    '''
    post_key = f'Post {link} for I($)G'
    if image_url == None:
        post_item = {
        'Text': 'None',
        'Date': 'None',
        'Post Link': 'None',
        'Post key': 'None',
        'Number of Bylines': 0,
        'Image url': 'None'
        }
    else:
        post_item = {
            'Text': post.strip(),
            'Date': my_date,
            'Post Link': link,
            'Post key': post_key,
            'Number of Bylines': author_number,
            'Image url': image_url
        }
    post_item_list.append(post_item)

    post = f'''
    '{header}' by {author_linkedin} for {pub_linkedin}: {sentence}... {paywall} {link} Linked($)in
    '''
    post_key = f'Post {link} for Linked($)in'
    post_item = {
        'Text': post.strip(),
        'Date': my_date,
        'Post Link': link,
        'Post key': post_key,
        'Number of Bylines': author_number,
        'Image url': image_url
    }
    post_item_list.append(post_item)

    item = {
        'Date': my_date,
        'Link': link,
        'Title': header,
        'Sentence': sentence,
        'publication_name' : pub_name,
        'author_name' : author_name,
        'author_twitter' : author_twitter,
        'author_ig' : author_ig,
        'author_fb' : author_fb,
        'author_linkedin' : author_linkedin,
        'publication_twitter' : pub_twitter,
        'publication_ig' : pub_ig,
        'publication_fb' : pub_fb,
        'publication_linkedin' : pub_linkedin,
        'paywall' : paywall,
        'Number of Bylines': author_number,
        'Image url': image_url
        
    }
    item_list.append(item)


def nytimes_scraper():  #Done
    today = datetime.now(eastern_tz).date()
    engine = create_engine(f"mysql+pymysql://{uname}:{pwd}@{hostname}/{dbname}")
    conn = engine.connect()
    query = text('SELECT * FROM articles')
    data = pd.read_sql_query(query, conn)
    urls = data['Article URL'][(data['Publication Name'] == 'The New York Times') & (data['Do not scrape'] == 'N')]
    all_authors = data['Author Name'][(data['Publication Name'] == 'The New York Times') & (data['Do not scrape'] == 'N')]
    urls = urls.dropna().to_list()
    all_authors = all_authors.dropna().to_list()
    if len(urls) > 0:
        for x in range(len(urls)):
            try:
                ua = get_random_user_agent()
                headers = {
                    'User-Agent': ua
                }
                scraper = cloudscraper.create_scraper()
                response = scraper.get(urls[x], headers=headers)
                soup = BeautifulSoup(response.text, 'lxml')
                posts = soup.select('.css-112uytv')
                for post in posts:
                    try:
                        post_link = post.select_one('.css-1l4spti a')['href']
                        post_link = 'https://www.nytimes.com' + post_link
                        if all_authors[x] in post.text:
                            res = scraper.get(post_link)
                            soup = BeautifulSoup(res.text, 'lxml')
                            meta = soup.select_one('script').text
                            json_data = json.loads(meta)
                            date = json_data['datePublished']
                            try:
                                date = datetime.fromisoformat(date.replace('Z', '+00:00')).date()
                                my_date = date.strftime("%Y, %m, %d")
                            except:
                                date = datetime.strptime('20230215', "%Y%m%d").date()
                                my_date = date.strftime("%Y, %m, %d")
                                
                            try:
                                delta = today - date
                            except:
                                delta = timedelta(days=5)
                            if delta < timedelta(days=3):
                                link = json_data['url']
                                header = json_data['headline']
                                try:
                                    image_url = json_data['image'][0]['url']
                                except:
                                    image_url = None
                                try:
                                    sentence = remove_period(json_data['description']).split('.')
                                    sentence = sentence[0]
                                except:
                                    sentence = remove_period(post.select_one('p'))
                                authors = json_data['author']
                                authors_num = len(authors)
                                add_up(data, urls[x], link, header, sentence, my_date, author_number=authors_num, image_url=image_url)
                            else:
                                break
                        else:
                            pass
                    except:
                        pass
            except:
                pass
    else:
        pass
        
def forbes_scraper():  #Done
    today = datetime.now(eastern_tz).date()
    engine = create_engine(f"mysql+pymysql://{uname}:{pwd}@{hostname}/{dbname}")
    conn = engine.connect()
    query = text('SELECT * FROM articles')
    data = pd.read_sql_query(query, conn)
    urls = data['Article URL'][(data['Publication Name'] == 'Forbes') & (data['Do not scrape'] == 'N')]
    urls.dropna(inplace=True)
    if len(urls) > 0:
        for url in urls:
            try:
                ua = get_random_user_agent()
                headers = {
                    'User-Agent': ua
                }
                s = session()
                response = s.get(url, headers=headers)
                soup = BeautifulSoup(response.text, 'lxml')
                posts = soup.select('article')
                for post in posts:
                    try:
                        link = post.select_one('.stream-item__title')['href']
                        res = s.get(link, headers=headers)
                        soup = BeautifulSoup(res.text, 'lxml')
                        json_data = soup.select_one('script[type="application/ld+json"]').text
                        json_data = json.loads(json_data)
                        date = json_data['datePublished']
                        try:
                            date = parser.parse(date).date()
                            my_date = date.strftime("%Y, %m, %d")
                        except:
                            date = datetime.strptime('20230215', "%Y%m%d").date()
                            my_date = date.strftime("%Y, %m, %d")
                            
                        try:
                            delta = today - date
                        except:
                            delta = timedelta(days=5)
                        if delta < timedelta(days=3):
                            link = json_data['mainEntityOfPage']
                            header = json_data['headline']
                            try:
                                sentence = remove_period(json_data['description']).split('.')
                                sentence = sentence[0]
                            except:
                                sentence = remove_period(json_data['description'])
                            try:
                                image_url = json_data['image']['url']
                            except:
                                image_url = None
                            add_up(data, url, link, header, sentence, my_date, image_url=image_url)
                        else:
                            pass
                    except:
                        pass
            except:
                pass
    else:
        pass

def nj_scraper():   #edited
    today = datetime.now(eastern_tz).date()
    engine = create_engine(f"mysql+pymysql://{uname}:{pwd}@{hostname}/{dbname}")
    conn = engine.connect()
    query = text('SELECT * FROM articles')
    data = pd.read_sql_query(query, conn)
    urls = data['Article URL'][(data['Publication Name'] == 'NJ.com') & (data['Do not scrape'] == 'N')]
    urls.dropna(inplace=True)
    if len(urls) > 0:
        for url in urls:
            try:
                ua = get_random_user_agent()
                headers = {
                    'User-Agent': ua
                }
                s = session()
                response = s.get(url, headers=headers)
                soup = BeautifulSoup(response.text, 'lxml')
                posts = soup.select('.river-item')
                for post in posts:
                    try:
                        link = post.select_one('a.river-item__headline-link')['href']
                        res = s.get(link, headers=headers)
                        soup = BeautifulSoup(res.text, 'lxml')
                        json_data = soup.select_one('script[type="application/ld+json"]').text
                        json_data = json.loads(json_data)[0]
                        date = json_data['datePublished']
                        try:
                            date = parser.parse(date).date()
                            my_date = date.strftime("%Y, %m, %d")
                        except:
                            date = datetime.strptime('20230215', "%Y%m%d").date()
                            my_date = date.strftime("%Y, %m, %d")          
                        try:
                            delta = today - date
                        except:
                            delta = timedelta(days=5)
                        if delta < timedelta(days=3):
                            link = json_data['url']
                            header = json_data['headline']
                            try:
                                sentence = remove_period(post.select_one('.river-item__summary').text.replace('\n', ' ')).split('.')
                                sentence = sentence[0]
                            except:
                                sentence = remove_period(post.select_one('p').text)
                            try:
                                image_url = json_data['image']
                            except:
                                image_url = None
                            authors = json_data['author']
                            authors_num = len(authors)
                            add_up(data, url, link, header, sentence, my_date, author_number=authors_num, image_url=image_url)
                        else:
                            break
                    except:
                        pass
            except:
                pass

def fangraph_scraper():  #edited
    today = datetime.now(eastern_tz).date()
    engine = create_engine(f"mysql+pymysql://{uname}:{pwd}@{hostname}/{dbname}")
    conn = engine.connect()
    query = text('SELECT * FROM articles')
    data = pd.read_sql_query(query, conn)
    urls = data['Article URL'][(data['Publication Name'] == 'FanGraphs') & (data['Do not scrape'] == 'N')]
    urls.dropna(inplace=True)
    if len(urls) > 0:
        for url in urls:
            try:
                ua = get_random_user_agent()
                headers = {
                    'User-Agent': ua
                }
                s = session()
                response = s.get(url, headers=headers)
                soup = BeautifulSoup(response.text, 'lxml')
                posts = soup.select('.post')

                for post in posts:
                    try:
                        link = post.select_one('h2 a')['href']
                        res = s.get(link, headers=headers)
                        soup = BeautifulSoup(res.text, 'lxml')
                        json_data = soup.select('script[type="application/ld+json"]')[-1].text
                        json_data = json.loads(json_data)
                        date = json_data['datePublished']
                        try:
                            date = parser.parse(date).date()
                            my_date = date.strftime("%Y, %m, %d")
                            print(date)
                        except:
                            date = datetime.strptime('20230215', "%Y%m%d").date()
                            my_date = date.strftime("%Y, %m, %d")             

                        try:
                            delta = today - date
                        except:
                            delta = timedelta(days=5)
                        if delta < timedelta(days=3):
                            link = json_data['mainEntityOfPage']['@id']
                            header = json_data['headline']
                            try:
                                sentence = json_data['description'].split('.')
                                sentence = sentence[0]
                            except:
                                sentence = json_data['description']
                            try:
                                image_url = json_data['image']['url']
                            except:
                                image_url = None
                            authors = json_data['author']['name'].split('and')
                            authors_num = len(authors)
                            add_up(data, url, link, header, sentence, my_date, author_number=authors_num, image_url=image_url)
                        else:
                            break
                    except:
                        pass
            except:
                pass

def cbs_sports_scraper():  #edited
    today = datetime.now(eastern_tz).date()
    engine = create_engine(f"mysql+pymysql://{uname}:{pwd}@{hostname}/{dbname}")
    conn = engine.connect()
    query = text('SELECT * FROM articles')
    data = pd.read_sql_query(query, conn)
    urls = data['Article URL'][(data['Publication Name'] == 'CBS Sports') & (data['Do not scrape'] == 'N')]
    urls.dropna(inplace=True)
    if len(urls) > 0:
        for url in urls:
            try:
                ua = get_random_user_agent()
                headers = {
                    'User-Agent': ua
                }
                s = session()
                response = s.get(url, headers=headers)
                soup = BeautifulSoup(response.text, 'lxml')
                posts = soup.select('.asset')
                for post in posts:
                    try:
                        post_link = post.select_one('a')['href']
                        post_link = 'https://www.cbssports.com' + post_link
                        res = s.get(post_link)
                        soup = BeautifulSoup(res.text, 'lxml')
                        date = soup.select_one('time')['datetime']
                        try:
                            date = parser.parse(date).date()
                            my_date = date.strftime("%Y, %m, %d")
                        except:
                            date = datetime.strptime('20230215', "%Y%m%d").date()
                            my_date = date.strftime("%Y, %m, %d")     
                        try:
                            delta = today - date
                        except:
                            delta = timedelta(days=5)
                        if delta < timedelta(days=3):
                            header = post.select_one('h3').text.strip()
                            try:
                                sentence = remove_period(post.select_one('p').text).split('.')
                                sentence = sentence[0]
                            except:
                                sentence = remove_period(post.select_one('p').text)
                            try:
                                image_url = soup.select_one('.Article-featuredImageImg.is-lazy-image')['data-lazy']
                            except:
                                image_url = None
                            authors = soup.select('.ArticleAuthor-name--link')
                            authors_num = len(authors)
                            add_up(data, url, post_link, header, sentence, my_date, author_number=authors_num, image_url=image_url)
                        else:
                            break
                    except:
                        pass
            except:
                pass

def ringer_scraper():   #edited
    today = datetime.now(eastern_tz).date()
    engine = create_engine(f"mysql+pymysql://{uname}:{pwd}@{hostname}/{dbname}")
    conn = engine.connect()
    query = text('SELECT * FROM articles')
    data = pd.read_sql_query(query, conn)
    urls = data['Article URL'][(data['Publication Name'] == 'The Ringer') & (data['Do not scrape'] == 'N')]
    urls.dropna(inplace=True)
    if len(urls) > 0:
        for url in urls:
            try:
                ua = get_random_user_agent()
                headers = {
                    'User-Agent': ua
                }
                s = session()
                response = s.get(url, headers=headers)
                soup = BeautifulSoup(response.text, 'lxml')
                posts = soup.select('.c-compact-river__entry ')
                for post in posts:
                    try:
                        link = post.select_one('h2 a')['href']
                        res = requests.get(link, headers=headers)
                        soup = BeautifulSoup(res.text, 'lxml')
                        json_data = soup.select_one('script[type="application/ld+json"]').text
                        json_data = json.loads(json_data)[0]
                        date = json_data['datePublished']
                        try:
                            date = parser.parse(date).date()
                            my_date = date.strftime("%Y, %m, %d")
                        except:
                            date = datetime.strptime('20230215', "%Y%m%d").date()
                            my_date = date.strftime("%Y, %m, %d")           
                        try:
                            delta = today - date
                        except:
                            delta = timedelta(days=5)
                        if delta < timedelta(days=3):
                            link = json_data['url']
                            header = json_data['headline'].replace('‘', '').replace('’', '')
                            desc = json_data['description'].replace('‘', '').replace('’', '').replace('“', '').replace('”', '')
                            try:
                                sentence = remove_period(desc).split('.')
                                sentence = sentence[0]
                            except:
                                sentence = remove_period(desc)
                            try:
                                image_url= json_data['image'][0]['url']
                            except:
                                image_url= None
                            authors = json_data['author']
                            authors_num = len(authors)
                            add_up(data, url, link, header, sentence, my_date, author_number=authors_num, image_url=image_url)
                        else:
                            break
                    except:
                        pass
            except:
                pass

def sportsbusinessjournal_scraper():  #edited
    today = datetime.now(eastern_tz).date()
    engine = create_engine(f"mysql+pymysql://{uname}:{pwd}@{hostname}/{dbname}")
    conn = engine.connect()
    query = text('SELECT * FROM articles')
    data = pd.read_sql_query(query, conn)
    urls = data['Article URL'][(data['Publication Name'] == 'Sports Business Journal') & (data['Do not scrape'] == 'N')]
    urls.dropna(inplace=True)
    if len(urls) > 0:
        for url in urls:
            try:
                ua = get_random_user_agent()
                headers = {
                    'User-Agent': ua
                }
                s = session()
                response = s.get(url, headers=headers)
                soup = BeautifulSoup(response.text, 'lxml')
                posts = soup.select('.article')[1:]
                for post in posts:
                    try:
                        link = post.select_one('h2 a')['href']
                        res = s.get(link, headers=headers)
                        soup = BeautifulSoup(res.text, 'lxml')
                        json_data = soup.select_one('script[type="application/ld+json"]').text
                        json_data = json.loads(json_data)
                        date = json_data['datePublished']
                        try:
                            date = parser.parse(date).date()
                            my_date = date.strftime("%Y, %m, %d")
                        except:
                            date = datetime.strptime('20230215', "%Y%m%d").date()
                            my_date = date.strftime("%Y, %m, %d")           
                        try:
                            delta = today - date
                        except:
                            delta = timedelta(days=5)
                        if delta < timedelta(days=3):
                            header = json_data['headline']
                            try:
                                sentence = remove_period(post.select_one('.text-container .text-frame').text.strip().replace('\n', ' ')).split('.')
                                sentence = sentence[0]
                            except:
                                sentence = remove_period(post.select_one('.text-container .text-frame').text.strip().replace('\n', ' '))
                            try:
                                image_url = json_data['image']
                                if image_url == '':
                                    image_url = None
                            except:
                                image_url = None
                            authors = json_data['author'].split('and')
                            authors_num = len(authors)
                            add_up(data, url, link, header, sentence, my_date, author_number=authors_num, image_url=image_url)
                        else:
                            break
                    except:
                        pass
            except:
                pass

def yahoo_scraper():  #edited
    today = datetime.now(eastern_tz).date()
    engine = create_engine(f"mysql+pymysql://{uname}:{pwd}@{hostname}/{dbname}")
    conn = engine.connect()
    query = text('SELECT * FROM articles')
    data = pd.read_sql_query(query, conn)
    urls = data['Article URL'][(data['Publication Name'] == 'Yahoo') & (data['Do not scrape'] == 'N')]
    s = session()
    urls.dropna(inplace=True)
    if len(urls) > 0:
        for url in urls:
            try:
                ua = get_random_user_agent()
                headers = {
                    'User-Agent': ua
                }
                response = s.get(url, headers=headers)
                soup = BeautifulSoup(response.text, 'lxml')
                posts = soup.select('.item-hover-trigger')
                for post in posts:
                    try:
                        link = post.select_one('h4 a')['href']
                        res = s.get(link, headers=headers)
                        soup = BeautifulSoup(res.text, 'lxml')
                        json_data = soup.select_one('script[type="application/ld+json"]').text
                        json_data = json.loads(json_data)
                        date = json_data['datePublished']
                        try:
                            date = parser.parse(date).date()
                            my_date = date.strftime("%Y, %m, %d")
                        except:
                            date = datetime.strptime('20230215', "%Y%m%d").date()
                            my_date = date.strftime("%Y, %m, %d")  
                        try:
                            delta = today - date
                        except:
                            delta = timedelta(days=5)
                        if delta < timedelta(days=3):
                            link = json_data['mainEntityOfPage']
                            header = json_data['headline']
                            try:
                                sentence = remove_period(json_data['description']).split('.')
                                sentence = sentence[0]
                            except:
                                sentence = remove_period(json_data['description'])
                            try:
                                image_url = json_data['image']['url']
                            except:
                                image_url = None
                            authors = soup.select('.caas-author-byline-collapse a')
                            authors_num = len(authors)
                            add_up(data, url, link, header, sentence, my_date, author_number=authors_num, image_url=image_url)
                        else:
                            break
                    except:
                        pass
            except:
                pass

def nypost_scraper():   #edited test seperately
    today = datetime.now(eastern_tz).date()
    engine = create_engine(f"mysql+pymysql://{uname}:{pwd}@{hostname}/{dbname}")
    conn = engine.connect()
    query = text('SELECT * FROM articles')
    data = pd.read_sql_query(query, conn)
    urls = data['Article URL'][(data['Publication Name'] == 'New York Post') & (data['Do not scrape'] == 'N')]
    urls.dropna(inplace=True)
    if len(urls) > 0:
        for url in urls:
            try:
                ua = get_random_user_agent()
                headers = {
                    'User-Agent': ua
                }
                s = session()
                response = s.get(url, headers=headers)
                soup = BeautifulSoup(response.text, 'lxml')
                posts = soup.select('.story.story--archive.story--i-flex')        
                for post in posts:
                    try:
                        link = post.select_one('a')['href']
                        res = s.get(link, headers=headers)
                        soup = BeautifulSoup(res.text, 'lxml')
                        json_data = soup.select_one('script[type="application/ld+json"]').text.strip()
                        json_data = json.loads(json_data, strict = False)
                        date = json_data['datePublished']
                        try:
                            date = parser.parse(date).date()
                            my_date = date.strftime("%Y, %m, %d")
                        except:
                            date = datetime.strptime('20230215', "%Y%m%d").date()
                            my_date = date.strftime("%Y, %m, %d")             
                        try:
                            delta = today - date
                        except:
                            delta = timedelta(days=5)
                        if delta < timedelta(days=3):
                            link = json_data['url']
                            header = json_data['headline']
                            try:
                                sentence = remove_period(post.select_one('p').text.strip()).split('.')
                                sentence = sentence[0]
                            except:
                                sentence = remove_period(post.select_one('p').text.strip())
                            try:
                                image_url = json_data['image']['url']
                            except:
                                image_url = None
                            authors = json_data['author']
                            authors_num = len(authors)
                            add_up(data, url, link, header, sentence, my_date, author_number=authors_num, image_url=image_url)
                        else:
                            break
                    except:
                        pass
            except:
                pass

def foxsports_scraper(): #edited
    today = datetime.now(eastern_tz).date()
    engine = create_engine(f"mysql+pymysql://{uname}:{pwd}@{hostname}/{dbname}")
    conn = engine.connect()
    query = text('SELECT * FROM articles')
    data = pd.read_sql_query(query, conn)
    urls = data['Article URL'][(data['Publication Name'] == 'FOX Sports') & (data['Do not scrape'] == 'N')]
    urls.dropna(inplace=True)
    if len(urls) > 0:
        for url in urls:
            try:
                ua = get_random_user_agent()
                headers = {
                    'User-Agent': ua
                }
                s = session()
                response = s.get(url, headers=headers)
                soup = BeautifulSoup(response.text, 'lxml')
                posts = soup.select('a.news')
                for post in posts:
                    try:
                        link = post['href']
                        link = 'https://www.foxsports.com' + link
                        res = s.get(link, headers=headers)
                        soup = BeautifulSoup(res.text, 'lxml')
                        json_data = soup.select_one('script[type="application/ld+json"]').text.strip()
                        json_data = json.loads(json_data, strict = False)
                        date = json_data['datePublished']
                        try:
                            date = parser.parse(date).date()
                            my_date = date.strftime("%Y, %m, %d")
                        except:
                            date = datetime.strptime('20230215', "%Y%m%d").date()
                            my_date = date.strftime("%Y, %m, %d")
                        try:
                            delta = today - date
                        except:
                            delta = timedelta(days=5)
                        if delta < timedelta(days=3):
                            link = post['href']
                            link = 'https://www.foxsports.com' + link
                            header = json_data['headline']
                            try:
                                sentence = remove_period(post.select_one('span').text.strip()).split('.')
                                sentence = sentence[0]
                            except:
                                sentence = remove_period(post.select_one('span').text.strip())
                            try:
                                image_url = json_data['image'][0]['url']
                            except:
                                image_url = None
                            try:
                                authors = json_data['author']
                            except:
                                authors = None
                            authors_num = len(authors)
                            add_up(data, url, link, header, sentence, my_date, author_number=authors_num, image_url=image_url)
                        else:
                            break
                    except:
                        pass
            except:
                pass

def insider_scraper():  #edited
    today = datetime.now(eastern_tz).date()
    engine = create_engine(f"mysql+pymysql://{uname}:{pwd}@{hostname}/{dbname}")
    conn = engine.connect()
    query = text('SELECT * FROM articles')
    data = pd.read_sql_query(query, conn)
    urls = data['Article URL'][(data['Publication Name'] == 'Insider') & (data['Do not scrape'] == 'N')]
    urls.dropna(inplace=True)
    if len(urls) > 0:
        for url in urls:
            try:
                ua = get_random_user_agent()
                headers = {
                    'User-Agent': ua
                }
                s = session()
                response = s.get(url, headers=headers)
                soup = BeautifulSoup(response.text, 'lxml')
                posts = soup.select('.river-item.featured-post')
                for post in posts:
                    try:
                        link = post.select_one('h2 a')['href']
                        link = 'https://www.insider.com' + link
                        res = s.get(link, headers=headers)
                        soup = BeautifulSoup(res.text, 'lxml')
                        json_data = soup.select_one('script[type="application/ld+json"]').text.strip()
                        json_data = json.loads(json_data, strict = False)
                        date = json_data['datePublished']
                        try:
                            date = parser.parse(date).date()
                            my_date = date.strftime("%Y, %m, %d")
                            print(date)
                        except:
                            date = datetime.strptime('20230215', "%Y%m%d").date()
                            my_date = date.strftime("%Y, %m, %d")             
                        try:
                            delta = today - date
                        except:
                            delta = timedelta(days=5)
                        if delta < timedelta(days=3):
                            link = json_data['mainEntityOfPage']['@id']
                            header = json_data['headline']
                            try:
                                sentence = remove_period(json_data['description']).split('.')
                                sentence = sentence[0]
                            except:
                                sentence = remove_period(json_data['description'].strip())
                            try:
                                image_url = json_data['image']['url']
                            except:
                                image_url = None
                            authors = soup.select('.byline-link.byline-author-name')
                            authors_num = len(authors)
                            add_up(data, url, link, header, sentence, my_date, author_number=authors_num, image_url=image_url)
                        else:
                            break
                    except:
                        pass
            except:
                pass

def tampabay_scraper():  #edited
    engine = create_engine(f"mysql+pymysql://{uname}:{pwd}@{hostname}/{dbname}")
    engine = engine
    conn = engine.connect()
    query = text('SELECT * FROM articles')
    data = pd.read_sql_query(query, conn)
    urls = data['Article URL'][(data['Publication Name'] == 'Tampa Bay Times') & (data['Do not scrape'] == 'N')]
    urls.dropna(inplace=True)
    if len(urls) > 0:
        for url in urls:
            try:
                s = session()
                ua = get_random_user_agent()
                headers = {
                    'User-Agent': ua
                }
                response = s.get(url,  headers=headers)
                soup = BeautifulSoup(response.text, 'lxml')
                posts = soup.select('.feed-item')
                for post in posts:
                    try:
                        post_link = 'https://www.tampabay.com' + post.select_one('.headline a')['href']
                        res = s.get(post_link, headers=headers)
                        soup = BeautifulSoup(res.text, 'lxml')
                        json_data = soup.select_one('script[type="application/ld+json"]').text
                        json_data = json.loads(json_data)
                        try:
                            date = json_data['datePublished']
                            date = datetime.fromisoformat(date.replace('Z', '+00:00')).date()
                            print(date)
                        except:
                            date = datetime.strptime('20230215', "%Y%m%d").date()
                            
                        try:
                            delta = datetime.now(eastern_tz).date() - date
                        except:
                            delta = timedelta(days=5)
                        if delta < timedelta(days=3):
                            my_date = date.strftime("%Y, %m, %d")
                            link = res.url
                            header = json_data['headline']
                            desc = json_data['mainEntityOfPage']['primaryImageOfPage']['description']
                            try:
                                sentence = remove_period(desc).split('.')
                                sentence = sentence[0]
                            except:
                                sentence = remove_period(desc)
                            try:
                                image_url = json_data['image'][0]
                            except:
                                image_url = None
                            authors = json_data['author']
                            authors_num = len(authors)
                            add_up(data, url, link, header, sentence, my_date, image_url= image_url, author_number=authors_num)
                        else:
                            break
                    except:
                        pass
            except:
                pass

def sporting_news():   #edited
    engine = create_engine(f"mysql+pymysql://{uname}:{pwd}@{hostname}/{dbname}")
    engine = engine
    conn = engine.connect()
    query = text('SELECT * FROM articles')
    data = pd.read_sql_query(query, conn)
    urls = data['Article URL'][(data['Publication Name'] == 'Sporting News') & (data['Do not scrape'] == 'N')]
    urls.dropna(inplace=True)
    if len(urls) > 0:
        for url in urls:
            try:
                s = session()
                ua = get_random_user_agent()
                headers = {
                    'User-Agent': ua
                }
                response = s.get(url,  headers=headers)
                soup = BeautifulSoup(response.text, 'lxml')
                posts = soup.select('.list-item')
                for post in posts:
                    try:
                        post_link = 'https://www.sportingnews.com' + post.select_one('.list-item__title a')['href']
                        res = s.get(post_link)
                        soup = BeautifulSoup(res.text, 'lxml')
                        json_data = soup.select_one('script[type="application/ld+json"]').text
                        json_data = json.loads(json_data)
                        header = json_data['headline']
                        try:
                            sentence = remove_period(soup.select_one('p').text.strip()).split('.')
                            sentence = sentence[0]
                        except:
                            sentence = remove_period(soup.select_one('p').text.strip())
                        try:
                            date = json_data['datePublished']
                            date =  datetime.fromisoformat(date).replace(tzinfo=None).date()
                        except:
                            date = datetime.strptime('20230215', "%Y%m%d").date()                    
                        try:
                            delta = datetime.now(eastern_tz).date() - date
                        except:
                            delta = timedelta(days=5)
                        if delta < timedelta(days=3):
                            my_date = date.strftime("%Y, %m, %d")
                            link = res.url
                            try:
                                image_url = json_data['image'][0]
                            except:
                                image_url = None
                            authors = json_data['author']
                            authors_num = len(authors)
                            add_up(data, url, link, header, sentence, my_date, image_url= image_url, author_number=authors_num)
                        else:
                            break
                    except:
                        pass
            except:
                pass

def northjersey_scraper():    #edited
    engine = create_engine(f"mysql+pymysql://{uname}:{pwd}@{hostname}/{dbname}")
    engine = engine
    conn = engine.connect()
    query = text('SELECT * FROM articles')
    data = pd.read_sql_query(query, conn)
    urls = data['Article URL'][(data['Publication Name'] == 'The Record') & (data['Do not scrape'] == 'N')]
    urls.dropna(inplace=True)
    if len(urls) > 0:
        for url in urls:
            try:
                s = session()
                ua = get_random_user_agent()
                headers = {
                    'User-Agent': ua
                }
                response = s.get(url,  headers=headers)
                soup = BeautifulSoup(response.text, 'lxml')
                posts = soup.select_one('.articles').find_all_next()[:20]
                for post in posts[:20]:
                    try:
                        link = post['url']
                        res = requests.get(link, headers=headers)
                        soup = BeautifulSoup(res.text, 'lxml')
                        json_data = soup.select_one('script[type="application/ld+json"]').text
                        json_data = json.loads(json_data)[0]
                        try:
                            date = json_data['datePublished']
                            date = datetime.fromisoformat(date.replace('Z', '+00:00')).date()
                        except:
                            date = datetime.strptime('20230215', "%Y%m%d").date()  
                            
                        try:
                            delta = datetime.now(eastern_tz).date() - date
                        except:
                            delta = timedelta(days=5)
                        if delta < timedelta(days=3):
                            link = json_data['url']
                            header = json_data['headline']
                            my_date = date.strftime("%Y, %m, %d")
                            try:
                                sentence = remove_period(json_data['description'])
                                sentence = sentence.split('.')
                                sentence = sentence[0]                          
                            except:
                                sentence = remove_period(json_data['description'])
                            try:
                                image_url = json_data['image']['url']
                            except:
                                image_url = None
                            
                            authors = [json_data['author']]
                            authors_num = len(authors)
                            add_up(data, url, link, header, sentence, my_date, image_url= image_url, author_number=authors_num)
                        else:
                            break
                    except:
                        pass
            except:
                pass

def theathletic_scraper():  #edited
    engine = create_engine(f"mysql+pymysql://{uname}:{pwd}@{hostname}/{dbname}")
    engine = engine
    conn = engine.connect()
    query = text('SELECT * FROM articles')
    data = pd.read_sql_query(query, conn)
    urls = data['Article URL'][(data['Publication Name'] == 'The Athletic') & (data['Do not scrape'] == 'N')]
    urls.dropna(inplace=True)
    if len(urls) > 0:
        for url in urls:
            try:
                s = session()
                ua = get_random_user_agent()
                headers = {
                    'User-Agent': ua
                }
                response = s.get(url,  headers=headers)
                soup = BeautifulSoup(response.text, 'lxml')
                posts = soup.select('.MuiTypography-root.MuiLink-root.MuiLink-underlineNone.MuiTypography-colorInherit')
                for post in posts:
                    try:
                        post_link = post['href']
                        res = s.get(post_link, headers=headers)
                        soup = BeautifulSoup(res.text, 'lxml')
                        json_data = soup.select_one('script[type="application/ld+json"]').text
                        json_data = json.loads(json_data)
                        try:
                            date = json_data['datePublished']
                            date = datetime.fromisoformat(date.replace('Z', '+00:00')).date()
                        except:
                            date = datetime.strptime('20230215', "%Y%m%d").date()
                            
                        try:
                            delta = datetime.now(eastern_tz).date() - date
                        except:
                            delta = timedelta(days=5)
                        if delta < timedelta(days=3):
                            my_date = date.strftime("%Y, %m, %d")
                            link = json_data['url']
                            header = json_data['headline']
                            try:
                                sentence = remove_period(json_data['description']).split('.')
                                sentence = sentence[0]
                            except:
                                sentence = remove_period(json_data['description'].strip())
                            try:
                                image_url = json_data['image']['url']
                            except:
                                image_url = None
                            authors = json_data['author']
                            authors_num = len(authors)
                            add_up(data, url, link, header, sentence, my_date, image_url= image_url, author_number=authors_num)
                        else:
                            break
                    except:
                        pass
            except:
                pass

def apnews_scraper():   #edited
    engine = create_engine(f"mysql+pymysql://{uname}:{pwd}@{hostname}/{dbname}")
    engine = engine
    conn = engine.connect()
    query = text('SELECT * FROM articles')
    data = pd.read_sql_query(query, conn)
    s = session()
    ua = get_random_user_agent()
    headers = {
        'User-Agent': ua
    }
    response = s.get('https://apnews.com/MLB',  headers=headers)
    soup = BeautifulSoup(response.text, 'lxml')
    author_names = ['Ronald Blum', 'Ben Walker', 'Mike Fitzpatrick', 'Jerry Beach', 'Larry Fleisher', 'Scott Orgera']
    all_author = []
    for author_n in author_names:
        if author_n.upper() in soup.text:
            all_author.append(author_n)
    for author in all_author:
        try:
            url = data['Article URL'][(data['Publication Name'] == 'Associated Press') & (data['Do not scrape'] == 'N') & (data['Author Name'] == author)].item()
            s = session()
            ua = get_random_user_agent()
            headers = {
                'User-Agent': ua
            }
            response = s.get(url,  headers=headers)
            soup = BeautifulSoup(response.text, 'lxml')
            posts = soup.select('.FeedCard')
            for post in posts:
                try:
                    if author.upper() in post.text:
                        link = 'https://apnews.com' + post.select_one('.CardHeadline a')['href']
                        res = s.get(link, headers=headers)
                        soup = BeautifulSoup(res.text, 'lxml')
                        json_data = soup.select_one('script[type="application/ld+json"]').text
                        json_data = json.loads(json_data)
                        try:
                            date = post.select_one('.Timestamp')['data-source']
                            date = datetime.strptime(date, "%Y-%m-%dT%H:%M:%SZ").date()
                        except:
                            date = datetime.strptime('20230215', "%Y%m%d").date()
                    
                        try:
                            delta = datetime.now(eastern_tz).date() - date
                        except:
                            delta = timedelta(days=5)
                        if delta < timedelta(days=3):
                            my_date = date.strftime("%Y, %m, %d")
                            header = json_data['headline']
                            try:
                                sentence = remove_period(json_data['description']).split('.')
                                sentence = sentence[0]
                            except:
                                sentence = remove_period(json_data['description'])
                            try:
                                image_url = json_data['image']
                            except:
                                image_url = None
                            authors = json_data['author']
                            authors_num = len(authors)
                            add_up(data, url, link, header, sentence, my_date, author_name=author, author_number=authors_num, image_url=image_url)                                               
                        else:
                            break
                    else:
                        pass
                except:
                    pass
        except:
            pass

def mlb_scraper():   #edited
    engine = create_engine(f"mysql+pymysql://{uname}:{pwd}@{hostname}/{dbname}")
    engine = engine
    conn = engine.connect()
    query = text('SELECT * FROM articles')
    data = pd.read_sql_query(query, conn)
    s = session()
    ua = get_random_user_agent()
    headers = {
        'User-Agent': ua
    }
    response = s.get('https://www.mlb.com/news',  headers=headers)
    soup = BeautifulSoup(response.text, 'lxml')
    author_names = ['David Adler', 'Bill Ladson', 'Sarah Langs', 'Andrew Simon', 'Betelhem Ashame', 'Elizabeth Muratore', 'Mark Feinsand',
                    'Mike Lupica', 'Mike Petriello', 'Nathalie Alonso']
    all_author = []
    for author_n in author_names:
        if author_n in soup.text:
            all_author.append(author_n)
    for author in all_author:
        try:
            url = data['Article URL'][(data['Publication Name'] == 'MLB.com') & (data['Do not scrape'] == 'N') & (data['Author Name'] == author)].item()
            ua = get_random_user_agent()
            headers = {
                'User-Agent': ua
            }
            response = s.get(url,  headers=headers)
            soup = BeautifulSoup(response.text, 'lxml')
            posts = soup.select('article')
            for post in posts:
                try:
                    if author in post.text:
                        link = 'https://www.mlb.com' + post.select_one('.p-button__link')['href']
                        res = s.get(link, headers=headers)
                        soup = BeautifulSoup(res.text, 'lxml')
                        json_data = soup.select_one('script[type="application/ld+json"]').text
                        json_data = json.loads(json_data)
                        try:
                            date = json_data['datePublished']
                            date = parser.parse(date).date()
                        except:
                            date = datetime.strptime('20230215', "%Y%m%d").date()
                        try:
                            delta = datetime.now(eastern_tz).date() - date
                        except:
                            delta = timedelta(days=5)
                        if delta < timedelta(days=3):
                            my_date = date.strftime("%Y, %m, %d")
                            header = json_data['headline']
                            try:
                                sentence = remove_period(post.select_one('p').text.replace('  ', '').replace('\n', ' ')).split('.')
                                sentence = sentence[0]
                            except:
                                sentence = remove_period(post.select_one('p').text.replace('  ', '').replace('\n', ''))
                            link = json_data['url']
                            try:
                                image_url = json_data['image'][0]
                            except:
                                image_url = None
                            authors = json_data['author']['name'].split(',')
                            authors_num = len(authors)
                            add_up(data, url, link, header, sentence, my_date, author_name=author, author_number=authors_num, image_url=image_url)
                        else:
                            pass
                    else:
                        pass
                except:
                    pass
        except:
            pass

def mlb_extra_scraper():   #edited
    s = session()
    engine = create_engine(f"mysql+pymysql://{uname}:{pwd}@{hostname}/{dbname}")
    engine = engine
    conn = engine.connect()
    query = text('SELECT * FROM articles')
    data = pd.read_sql_query(query, conn)
    urls = ['https://www.mlb.com/yankees/news', 'https://www.mlb.com/mets/news']
    all_authors = ['Bryan Hoch', 'Anthony DiComo']
    for url in urls:
        try:
            ua = get_random_user_agent()
            headers = {
                'User-Agent': ua
            }
            response = s.get(url,  headers=headers)
            soup = BeautifulSoup(response.text, 'lxml')
            posts = soup.select('article')
            for post in posts:
                try:
                    for author in all_authors:
                        if author in post.text:
                            link = 'https://www.mlb.com' + post.select_one('.p-button__link')['href']
                            res = s.get(link, headers=headers)
                            soup = BeautifulSoup(res.text, 'lxml')
                            json_data = soup.select_one('script[type="application/ld+json"]').text
                            json_data = json.loads(json_data)
                            try:
                                date = json_data['datePublished']
                                date = parser.parse(date).date()
                            except:
                                date = datetime.strptime('20230215', "%Y%m%d").date()
                            try:
                                delta = datetime.now(eastern_tz).date() - date
                            except:
                                delta = timedelta(days=5)
                            if delta < timedelta(days=3):
                                my_date = date.strftime("%Y, %m, %d")
                                header = json_data['headline']
                                try:
                                    sentence = remove_period(post.select_one('p').text.replace('  ', '').replace('\n', ' ')).split('.')
                                    sentence = sentence[0]
                                except:
                                    sentence = remove_period(post.select_one('p').text.replace('  ', '').replace('\n', ''))
                                link = json_data['url']
                                try:
                                    image_url = json_data['image'][0]
                                except:
                                    image_url = None
                                authors = json_data['author']['name'].split(',')
                                authors_num = len(authors)
                                add_up(data, url, link, header, sentence, my_date, author_name=author, author_number=authors_num, image_url=image_url)
                            else:
                                pass
                        else:
                            pass
                except:
                    pass
        except:
            pass

def courant_scraper():   #edited
    today = datetime.now(eastern_tz).date()
    engine = create_engine(f"mysql+pymysql://{uname}:{pwd}@{hostname}/{dbname}")
    conn = engine.connect()
    query = text('SELECT * FROM articles')
    data = pd.read_sql_query(query, conn)
    urls = data['Article URL'][(data['Publication Name'] == 'Hartford Courant') & (data['Do not scrape'] == 'N')]
    urls.dropna(inplace=True)
    if len(urls) > 0:
        for url in urls:
            try:
                ua = get_random_user_agent()
                headers = {
                    'User-Agent': ua
                }
                s = session()
                response = s.get(url, headers=headers)
                soup = BeautifulSoup(response.text, 'lxml')
                posts_table = soup.select_one('.author-stories-feed')
                posts = posts_table.select('article')
                for post in posts:
                    try:
                        link = post.select_one('.article-title')['href']
                        res = s.get(link, headers=headers)
                        soup = BeautifulSoup(res.text, 'lxml')
                        json_data = soup.select_one('script[type="application/ld+json"]').text
                        json_data = json.loads(json_data)
                        date = json_data['datePublished']
                        try:
                            date = parser.parse(date).date()
                            my_date = date.strftime("%Y, %m, %d")
                        except:
                            date = datetime.strptime('20230215', "%Y%m%d").date()
                            my_date = date.strftime("%Y, %m, %d")             

                        try:
                            delta = today - date
                        except:
                            delta = timedelta(days=5)
                        if delta < timedelta(days=3):
                            header = json_data['headline'].replace('&#8217;', "'")
                            link = json_data['url']
                            try:
                                sentence = remove_period(post.select_one('.excerpt').text.strip()).split('.')
                                sentence = sentence[0]
                            except:
                                sentence = remove_period(post.select_one('.excerpt').text.strip())
                            try:
                                image_url = json_data['image']['url']
                            except:
                                image_url = None
                            authors = json_data['author']
                            authors_num = len(authors)
                            add_up(data, url, link, header, sentence, my_date, author_number=authors_num, image_url=image_url)
                        else:
                            break
                    except:
                        pass
            except:
                pass

def wsj_scraper():  #Done
    today = datetime.now(eastern_tz).date()
    engine = create_engine(f"mysql+pymysql://{uname}:{pwd}@{hostname}/{dbname}")
    conn = engine.connect()
    query = text('SELECT * FROM articles')
    data = pd.read_sql_query(query, conn)
    urls = data['Article URL'][(data['Publication Name'] == 'Wall Street Journal') & (data['Do not scrape'] == 'N')]
    urls.dropna(inplace=True)
    if len(urls) > 0:
        for url in urls:
            try:
                scraper = cloudscraper.create_scraper()
                ua = get_random_user_agent()
                headers = {
                    'User-Agent': ua
                }
                response = scraper.get('https://www.wsj.com/news/author/lindsey-adler?id=%7B%22count%22%3A10%2C%22query%22%3A%7B%22and%22%3A%5B%7B%22term%22%3A%7B%22key%22%3A%22AuthorId%22%2C%22value%22%3A%229460%22%7D%7D%2C%7B%22terms%22%3A%7B%22key%22%3A%22Product%22%2C%22value%22%3A%5B%22WSJ.com%22%2C%22WSJPRO%22%2C%22WSJ%20Video%22%5D%7D%7D%5D%7D%2C%22sort%22%3A%5B%7B%22key%22%3A%22LiveDate%22%2C%22order%22%3A%22desc%22%7D%5D%7D%2Fpage%3D0&type=allesseh_content_full')
                posts = response.json()['collection']
                for post in posts:
                    try:
                        post_id = post['id']
                        res = requests.get(f'https://www.wsj.com/news/author/lindsey-adler?id={post_id}&type=article%7Ccapi', headers=headers)
                        json_data = res.json()
                        try:
                            date_timestamp = json_data['data']['timestamp']
                            timestamp = date_timestamp / 1000.0 
                            date = datetime.fromtimestamp(timestamp).date()
                        except:
                            date = datetime.strptime('20230215', "%Y%m%d").date()
                        try:
                            delta = today - date
                        except:
                            delta = timedelta(days=5)

                        if delta < timedelta(days=3):
                            my_date = date.strftime("%Y, %m, %d") 
                            header = json_data['data']['headline']
                            try:
                                sentence = remove_period(json_data['data']['summary']).split('.')
                                sentence = sentence[0]
                            except:
                                sentence = remove_period(json_data['data']['summary'])
                            link = json_data['data']['canonical_url']
                            try:
                                image_url = json_data['data']['image']['M']['url']
                            except:
                                image_url = None
                            authors = json_data['data']['byline']
                            authors = re.split(r'\s+and\s+', authors)
                            authors_num = len(authors)
                            add_up(data, url, link, header, sentence, my_date, author_number=authors_num, image_url=image_url)
                        else:
                            break
                    except:
                        pass
            except:
               pass
        
def nydailynews_scraper():  #edited
    engine = create_engine(f"mysql+pymysql://{uname}:{pwd}@{hostname}/{dbname}")
    engine = engine
    conn = engine.connect()
    query = text('SELECT * FROM articles')
    data = pd.read_sql_query(query, conn)
    urls = data['Article URL'][(data['Publication Name'] == 'New York Daily News') & (data['Do not scrape'] == 'N')]
    urls.dropna(inplace=True)
    if len(urls) > 0:
        for url in urls:
            try:
                s = session()
                ua = get_random_user_agent()
                headers = {
                    'User-Agent': ua
                }
                response = s.get(url,  headers=headers)
                soup = BeautifulSoup(response.text, 'lxml')
                posts = soup.select('article')
                for post in posts:
                    try:
                        post_link = 'https://www.nydailynews.com' + post.select_one('a')['href']
                        res = s.get(post_link, headers=headers)
                        soup = BeautifulSoup(res.text, 'lxml')
                        json_data = soup.select_one('script[type="application/ld+json"]').text
                        json_data = json.loads(json_data)
                        try:
                            date = json_data['datePublished']
                            date = datetime.fromisoformat(date.replace('Z', '+00:00')).date()
                        except:
                            date = datetime.strptime('20230215', "%Y%m%d").date()
                        
                        try:
                            delta = datetime.now(eastern_tz).date() - date
                        except:
                            delta = timedelta(days=5)
                        if delta < timedelta(days=3):
                            my_date = date.strftime("%Y, %m, %d")
                            link = json_data['url']
                            header = json_data['headline']
                            sentence = remove_period(json_data['description'])
                            try:
                                sentence = sentence.split('.')
                                sentence = sentence[0]
                            except:
                                sentence = sentence
                            try:
                                image_url = json_data['image']['url']
                            except:
                                image_url = None
                            authors = json_data['author']
                            authors_num = len(authors)
                            add_up(data, url, link, header, sentence, my_date, author_number=authors_num, image_url=image_url)      
                        else:
                            break
                    except:
                        pass
            except:
                pass
            
def si_scraper():  #Done
    engine = create_engine(f"mysql+pymysql://{uname}:{pwd}@{hostname}/{dbname}")
    engine = engine
    conn = engine.connect()
    query = text('SELECT * FROM articles')
    data = pd.read_sql_query(query, conn)
    urls = data['Article URL'][(data['Publication Name'] == 'Sports Illustrated') & (data['Do not scrape'] == 'N')]
    urls.dropna(inplace=True)
    if len(urls) > 0:
        for url in urls:
            try:
                ua = get_random_user_agent()
                headers = {
                    'User-Agent': ua
                }
                proxies = {
                'http': 'http://172.102.218.198:6098',
                'http': 'http://104.239.76.236:6895',
                }
                scraper = cloudscraper.create_scraper()
                response = scraper.get(url, headers=headers, proxies=proxies)
                soup = BeautifulSoup(response.text, 'lxml')
                posts = soup.select('.l-grid--item')
                for post in posts:
                    try:
                        post_link = 'https://www.si.com' + post.select_one('phoenix-super-link')['href']
                        res = scraper.get(post_link, headers=headers)
                        soup = BeautifulSoup(res.text, 'lxml')
                        try:
                            date = soup.select_one('time')['datetime']
                            date = datetime.fromisoformat(date).date()
                        except:
                            date = datetime.strptime('20230215', "%Y%m%d").date()
                        try:
                            delta = datetime.now(eastern_tz).date() - date
                        except:
                            delta = timedelta(days=5)

                        if delta < timedelta(days=3):
                            my_date = date.strftime("%Y, %m, %d")
                            link = res.url
                            header = soup.select_one('.m-detail-header--title').text
                            try:
                                sentence = remove_period(soup.select_one('.m-detail--body p').text.replace('\xa0', ' ')).split('.')
                                sentence = sentence[0]
                            except:
                                sentence = remove_period(soup.select_one('.m-detail--body p').text.replace('\xa0', ' '))
                            add_up(data, url, link, header, sentence, my_date)
                        else:
                            break
                    except:
                        pass
            except:
                pass
            
def sny_scraper():   #Done
    def get_page_soup(url):
        with sync_playwright() as p:
            browser = p.chromium.launch()
            page = browser.new_page()
            page.goto(url)
            page.wait_for_selector('article.w-full.max-w-full', timeout=100000)
            soup = BeautifulSoup(page.content(), 'lxml')
            browser.close()
            return soup
        
    def get_soup(url):
        with sync_playwright() as p:
            browser = p.chromium.launch()
            page = browser.new_page()
            page.goto(url)
            page.wait_for_selector('.max-w-full', timeout=100000)
            soup = BeautifulSoup(page.content(), 'lxml')
            browser.close()
            return soup

    engine = create_engine(f"mysql+pymysql://{uname}:{pwd}@{hostname}/{dbname}")
    engine = engine
    conn = engine.connect()
    query = text('SELECT * FROM articles')
    data = pd.read_sql_query(query, conn)
    urls = data['Article URL'][(data['Publication Name'] == 'SNY') & (data['Do not scrape'] == 'N')]
    urls.dropna(inplace=True)
    if len(urls) > 0:
        for url in urls:
            try:
                soup = get_soup(url)
                posts = soup.select('.max-w-full')
                for post in posts:
                    try:
                        post_link = 'https://sny.tv' + post.select_one('a')['href']
                        soup = get_page_soup(post_link)
                        try:
                            date = soup.select_one('.w-full.flex.justify-between.items-end').text
                            date = datetime.strptime(date, "%m/%d/%Y %I:%M%p").date()
                        except:
                            date = datetime.strptime('20230215', "%Y%m%d").date()               
                        try:
                            delta = datetime.now(eastern_tz).date() - date
                        except:
                            delta = timedelta(days=5)

                        if delta < timedelta(days=3):
                            header = soup.select_one('h1').text
                            try:
                                sentence = remove_period(soup.select_one('.article-body').text).split('.')
                                sentence = sentence[0]
                            except:
                                sentence = remove_period(soup.select_one('.article-body').text)
                            link = post_link
                            my_date = date.strftime("%Y, %m, %d")
                            try:
                                image_url = post.select_one('.article-brief-image.image-container-wide.w-full.relative.overflow-hidden div img')['src']
                            except:
                                image_url = None
                            authors = soup.select('.flex.flex-col.whitespace-no-wrap span.font-bold')
                            authors_num = len(authors)
                            add_up(data, url, link, header, sentence, my_date, author_number=authors_num, image_url=image_url)                    
                        else:
                            break
                    except:
                        pass
            except:
                pass

def newsday_scraper():  #Done
    def get_json(url):
        with sync_playwright() as p:
            browser = p.chromium.launch()
            page = browser.new_page()
            json_data = []
            page.on("response", lambda response: json_data.append(response.json() if '?x-algolia-agent' in response.url else None))
            page.goto(url, wait_until='load')
            page.wait_for_selector('.headline')
            json_data = [value for value in json_data if value is not None]
            browser.close()
            return json_data

    engine = create_engine(f"mysql+pymysql://{uname}:{pwd}@{hostname}/{dbname}")
    engine = engine
    conn = engine.connect()
    query = text('SELECT * FROM articles')
    data = pd.read_sql_query(query, conn)
    urls = data['Article URL'][(data['Publication Name'] == 'Newsday') & (data['Do not scrape'] == 'N')]
    urls.dropna(inplace=True)
    if len(urls) > 0:
        for url in urls:
            try:
                json_data = get_json(url)
                posts = json_data[0]['results'][0]['hits']
                for post in posts:
                    try:
                        try:
                            date = post['publishedDate']
                            date = datetime.fromisoformat(date.replace('Z', '+00:00')).date()
                        except:
                            date = datetime.strptime('20230215', "%Y%m%d").date()                
                        try:
                            delta = datetime.now(eastern_tz).date() - date
                        except:
                            delta = timedelta(days=5)

                        if delta < timedelta(days=3):
                            header = post['headline'].replace('\xa0', ' ')
                            try:
                                sentence = remove_period(post['lead'])
                                sentence = sentence.split('.')
                                sentence = sentence[0]
                            except:
                                sentence = remove_period(post['lead'])
                            my_date = date.strftime("%Y, %m, %d")
                            link = post['url']
                            try:
                                image_url = post['topElement']['baseUrl']
                            except:
                                image_url = None
                            authors = post['authors']
                            authors_num = len(authors)
                            add_up(data, url, link, header, sentence, my_date, author_number=authors_num, image_url=image_url)  
                        else:
                            break
                    except:
                        pass
            except:
                pass

class NewsScraper:
    @staticmethod
    def scrapers():
        post_item_list.clear()
        item_list.clear()
        s = session()
        nytimes_scraper()
        forbes_scraper()
        nj_scraper()
        fangraph_scraper()
        cbs_sports_scraper()
        ringer_scraper()
        sportsbusinessjournal_scraper()
        yahoo_scraper()
        nypost_scraper()
        foxsports_scraper()
        insider_scraper()
        tampabay_scraper()
        sporting_news()
        northjersey_scraper()
        theathletic_scraper()
        apnews_scraper()
        mlb_scraper()
        mlb_extra_scraper()
        courant_scraper()
        wsj_scraper()
        nydailynews_scraper()
        # # #si_scraper()
        sny_scraper()
        newsday_scraper()
        
        return item_list, post_item_list