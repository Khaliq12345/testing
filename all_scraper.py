import streamlit as st
import os
from playwright.sync_api import sync_playwright
import requests
from requests import session
from bs4 import BeautifulSoup
import pandas as pd
from datetime import datetime, timedelta
from latest_user_agents import get_random_user_agent
from sqlalchemy import create_engine, text
import pytz
import cloudscraper
eastern_tz = pytz.timezone('US/Eastern')
os.system("playwright install chromium")

hostname=st.secrets['hostname']
dbname=st.secrets['dbname']
uname=st.secrets['uname']
pwd=st.secrets['pwd']

post_item_list =[]
item_list = []

def add_up(data, url, link, header, sentence, my_date, author_name=None):
    if author_name is not None:
        author_twitter = str(data.loc[(data['Author Name'] == author_name), 'Author Twitter'].item()).replace('"', '')
        pub_twitter = str(data.loc[(data['Author Name'] == author_name), 'Publication Twitter'].item()).replace('"', '')
        author_fb = str(data.loc[(data['Author Name'] == author_name), 'Author FB'].item()).replace('"', '')
        pub_fb = str(data.loc[(data['Author Name'] == author_name), 'Publication FB'].item()).replace('"', '')
        author_ig = str(data.loc[(data['Author Name'] == author_name), 'Author IG'].item()).replace('"', '')
        pub_ig = str(data.loc[(data['Author Name'] == author_name), 'Publication IG'].item()).replace('"', '')
        author_linkedin = str(data.loc[(data['Author Name'] == author_name), 'Author LinkedIn'].item()).replace('"', '')
        pub_linkedin = str(data.loc[(data['Author Name'] == author_name), 'Publication LinkedIn'].item()).replace('"', '')
        paywall = str(data.loc[(data['Author Name'] == author_name), 'Default Paywall  (Y/N)'].item()).replace('"', '')
        pub_name = str(data.loc[(data['Author Name'] == author_name), 'Publication Name'].item()).replace('"', '')

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
        author_twitter = str(data.loc[data['Article URL'] == url, 'Author Twitter'].item()).replace('"', '')
        pub_twitter = str(data.loc[data['Article URL'] == url, 'Publication Twitter'].item()).replace('"', '')
        author_fb = str(data.loc[data['Article URL'] == url, 'Author FB'].item()).replace('"', '')
        pub_fb = str(data.loc[data['Article URL'] == url, 'Publication FB'].item()).replace('"', '')
        author_ig = str(data.loc[data['Article URL'] == url, 'Author IG'].item()).replace('"', '')
        pub_ig = str(data.loc[data['Article URL'] == url, 'Publication IG'].item()).replace('"', '')
        author_linkedin = str(data.loc[data['Article URL'] == url, 'Author LinkedIn'].item()).replace('"', '')
        pub_linkedin = str(data.loc[data['Article URL'] == url, 'Publication LinkedIn'].item()).replace('"', '')
        paywall = str(data.loc[data['Article URL'] == url, 'Default Paywall  (Y/N)'].item()).replace('"', '')  
        pub_name = str(data.loc[(data['Article URL'] == url), 'Publication Name'].item()).replace('"', '')     

        if 'None' in author_twitter:
            author_twitter = str(data.loc[data['Article URL'] == url, 'Author Name'].item()).replace('"', '')
        if 'None' in pub_twitter:
            pub_twitter = str(data.loc[data['Article URL'] == url, 'Publication Name'].item()).replace('"', '')

        if 'None' in author_fb:
            author_fb = str(data.loc[data['Article URL'] == url, 'Author Name'].item()).replace('"', '')
        if 'None' in pub_fb:
            pub_fb = str(data.loc[data['Article URL'] == url, 'Publication Name'].item()).replace('"', '')

        if 'None' in author_ig:
            author_ig = str(data.loc[data['Article URL'] == url, 'Author Name'].item()).replace('"', '')
        if 'None' in pub_ig:
            pub_ig = str(data.loc[data['Article URL'] == url, 'Publication Name'].item()).replace('"', '')

        if 'None' in author_linkedin:
            author_linkedin = str(data.loc[data['Article URL'] == url, 'Author Name'].item()).replace('"', '')
        if 'None' in pub_linkedin:
            pub_linkedin = str(data.loc[data['Article URL'] == url, 'Publication Name'].item()).replace('"', '')

    if 'N' in paywall:
        paywall = ' '
    elif 'Y' in paywall:
        paywall = '<$>'
        
    sentence = sentence.encode('utf-8').decode('utf-8').replace('“', '').replace('”', '').replace('$', '')

    post = f'''
    '{header}' by {author_twitter} for {pub_twitter}: {sentence}... {paywall} {link} Twit($)ter
    '''
    post_key = post + '!'
    post_item = {
        'Text': post.strip(),
        'Date': my_date,
        'Post Link': link,
        'Post key': post_key
    }
    post_item_list.append(post_item)

    post = f'''
    '{header}' by {author_fb} for {pub_fb}: {sentence}... {paywall} {link} Face($)book
    '''
    post_key = post + '!'
    post_item = {
        'Text': post.strip(),
        'Date': my_date,
        'Post Link': link,
        'Post key': post_key
    }
    post_item_list.append(post_item)

    post = f'''
    '{header}' by {author_ig} for {pub_ig}: {sentence}... {paywall} {link} I($)G

    VISIT THE LINK IN OUR BIO TO READ THIS ARTICLE
    '''
    post_key = post + '!'
    post_item = {
        'Text': post.strip(),
        'Date': my_date,
        'Post Link': link,
        'Post key': post_key
    }
    post_item_list.append(post_item)

    post = f'''
    '{header}' by {author_linkedin} for {pub_linkedin}: {sentence}... {paywall} {link} Linked($)in
    '''
    post_key = post + '!'
    post_item = {
        'Text': post.strip(),
        'Date': my_date,
        'Post Link': link,
        'Post key': post_key
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
        'paywall' : paywall
        
    }
    item_list.append(item)

def nytimes_scraper():
    today = datetime.now(eastern_tz).date()
    engine = create_engine(f"mysql+pymysql://{uname}:{pwd}@{hostname}/{dbname}")
    conn = engine.connect()
    query = text('SELECT * FROM articles')
    data = pd.read_sql_query(query, conn)
    urls = data['Article URL'][(data['Publication Name'] == 'The New York Times') & (data['Do not scrape'] == 'N')]
    urls.dropna(inplace=True)     
    if len(urls) > 0:
        for url in urls:
            try:
                ua = get_random_user_agent()
                headers = {
                    'User-Agent': ua
                }
                response = requests.get(url, headers=headers)
                response = requests.get(url)
                soup = BeautifulSoup(response.text, 'lxml')
                posts = soup.select('.css-112uytv')
                for post in posts:
                    try:
                        link_date = post.select_one('.css-1l4spti a')['href']
                        date = link_date.split('/sports/baseball')
                        date = date[0].replace('/', '')
                        try:
                            date = datetime.strptime(date, "%Y%m%d")
                            my_date = date.strftime("%Y, %m, %d")
                        except:
                            date = datetime.strptime('20230215', "%Y%m%d")
                            my_date = date.strftime("%Y, %m, %d")
                            
                        try:
                            delta = today - date
                        except:
                            delta = timedelta(days=22)
                        if delta < timedelta(days=20):
                            link = 'https://www.nytimes.com' + link_date
                            header = post.select_one('h2').text
                            try:
                                sentence = post.select_one('p').text.split('.')
                                sentence = sentence[0]
                            except:
                                sentence = post.select_one('p').text

                            add_up(data, url, link, header, sentence, my_date)
                        else:
                            pass
                    except:
                        pass
            except:
                pass
    else:
        pass
        
def forbes_scraper():
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
                response = requests.get(url, headers=headers)
                response = requests.get(url)
                soup = BeautifulSoup(response.text, 'lxml')
                posts = soup.select('article')
                for post in posts:
                    try:
                        date = post['data-date']
                        try:
                            date = datetime.fromtimestamp(int(date) / 1000.0).date()
                            my_date = date.strftime("%Y, %m, %d")
                        except:
                            date = datetime.strptime('20230215', "%Y%m%d").date()
                            my_date = date.strftime("%Y, %m, %d")
                            
                        try:
                            delta = today - date
                        except:
                            delta = timedelta(days=11)
                        if delta < timedelta(days=10):
                            link = post.select_one('.stream-item__title')['href']
                            header = post.select_one('.stream-item__title').text
                            try:
                                sentence = post.select_one('.stream-item__description').text.split('.')
                                sentence = sentence[0]
                            except:
                                sentence = post.select_one('.stream-item__description').text

                            add_up(data, url, link, header, sentence, my_date)
                        else:
                            pass
                    except:
                        pass
            except:
                pass
    else:
        pass

def nj_scraper():
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
                response = requests.get(url, headers=headers)
                response = requests.get(url)
                soup = BeautifulSoup(response.text, 'lxml')
                posts = soup.select('.river-item')

                for post in posts:
                    try:
                        date = post.select_one('time')['datetime']
                        try:
                            date = datetime.fromtimestamp(int(date)).date()
                            my_date = date.strftime("%Y, %m, %d")
                        except:
                            date = datetime.strptime('20230215', "%Y%m%d").date()
                            my_date = date.strftime("%Y, %m, %d")           

                        try:
                            delta = today - date
                        except:
                            delta = timedelta(days=11)
                        if delta < timedelta(days=10):
                            link = post.select_one('a.river-item__headline-link')['href']
                            header = post.select_one('h2').text
                            try:
                                sentence = post.select_one('.river-item__summary').text.replace('\n', ' ') .split('.')
                                sentence = sentence[0]
                            except:
                                sentence = post.select_one('p').text

                            add_up(data, url, link, header, sentence, my_date)
                        else:
                            pass
                    except:
                        pass
            except:
                pass

def fangraph_scraper():
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
                response = requests.get(url, headers=headers)
                response = requests.get(url)
                soup = BeautifulSoup(response.text, 'lxml')
                posts = soup.select('.post')

                for post in posts:
                    try:
                        meta = post.select_one('.postmeta_author')
                        date = meta.find_next_sibling().text
                        try:
                            date = datetime.strptime(date, "%B %d, %Y").date()
                            my_date = date.strftime("%Y, %m, %d")
                        except:
                            date = datetime.strptime('20230215', "%Y%m%d").date()
                            my_date = date.strftime("%Y, %m, %d")             

                        try:
                            delta = today - date
                        except:
                            delta = timedelta(days=5)
                        if delta < timedelta(days=3):
                            link = post.select_one('h2 a')['href']
                            header = post.select_one('h2').text
                            try:
                                sentence = post.select_one('p').text.split('.')
                                sentence = sentence[0]
                            except:
                                sentence = post.select_one('p').text

                            add_up(data, url, link, header, sentence, my_date)
                        else:
                            pass
                    except:
                        pass
            except:
                pass

def cbs_sports_scraper():
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
                response = requests.get(url, headers=headers)
                response = requests.get(url)
                soup = BeautifulSoup(response.text, 'lxml')
                posts = soup.select('.asset')

                for post in posts:
                    try:
                        date = post.select_one('time').text
                        if 'H' in date:
                            try:
                                date = today - timedelta(hours=int(date.replace('H ago', '')))
                                my_date = date.strftime("%Y, %m, %d")
                            except:
                                date = datetime.strptime('20230215', "%Y%m%d").date()
                                my_date = date.strftime("%Y, %m, %d")
                        elif 'D' in date:
                            try:
                                date = today - timedelta(days=int(date.replace('D ago', '')))
                                my_date = date.strftime("%Y, %m, %d")
                            except:
                                date = datetime.strptime('20230215', "%Y%m%d").date()
                                my_date = date.strftime("%Y, %m, %d")       
                        try:
                            delta = today - date
                        except:
                            delta = timedelta(days=5)
                        if delta < timedelta(days=3):
                            link = post.select_one('a')['href']
                            link = 'https://www.cbssports.com' + link
                            header = post.select_one('h3').text
                            try:
                                sentence = post.select_one('p').text.split('.')
                                sentence = sentence[0]
                            except:
                                sentence = post.select_one('p').text
                            add_up(data, url, link, header, sentence, my_date)
                        else:
                            pass
                    except:
                        pass
            except:
                pass

def ringer_scraper():
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
                response = requests.get(url, headers=headers)
                response = requests.get(url)
                soup = BeautifulSoup(response.text, 'lxml')
                posts = soup.select('.c-compact-river__entry ')

                for post in posts:
                    try:
                        date = post.select_one('time')['datetime']
                        try:
                            date = datetime.fromisoformat(date).date()
                            my_date = date.strftime("%Y, %m, %d")
                        except:
                            date = datetime.strptime('20230215', "%Y%m%d").date()
                            my_date = date.strftime("%Y, %m, %d")           

                        try:
                            delta = today - date
                        except:
                            delta = timedelta(days=5)
                        if delta < timedelta(days=3):
                            link = post.select_one('h2 a')['href']
                            header = post.select_one('h2').text
                            try:
                                sentence = post.select_one('.p-dek.c-entry-box--compact__dek').text.split('.')
                                sentence = sentence[0]
                            except:
                                sentence = post.select_one('.p-dek.c-entry-box--compact__dek').text

                            add_up(data, url, link, header, sentence, my_date)
                        else:
                            pass
                    except:
                        pass
            except:
                pass

def sportsbusinessjournal_scraper():
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
                response = requests.get(url, headers=headers)
                response = requests.get(url)
                soup = BeautifulSoup(response.text, 'lxml')
                posts = soup.select('.article')[1:]

                for post in posts:
                    try:
                        date = post.select('span')[-1].text
                        try:
                            date = datetime.strptime(date, "%A, %B %d, %Y").date()
                            my_date = date.strftime("%Y, %m, %d")
                        except:
                            date = datetime.strptime('20230215', "%Y%m%d").date()
                            my_date = date.strftime("%Y, %m, %d")           

                        try:
                            delta = today - date
                        except:
                            delta = timedelta(days=5)
                        if delta < timedelta(days=3):
                            link = post.select_one('h2 a')['href']
                            header = post.select_one('h2').text
                            try:
                                sentence = post.select_one('.text-container .text-frame').text.strip().replace('\n', ' ').split('.')
                                sentence = sentence[0]
                            except:
                                sentence = post.select_one('.text-container .text-frame').text.strip().replace('\n', ' ')

                            add_up(data, url, link, header, sentence, my_date)
                        else:
                            pass
                    except:
                        pass
            except:
                pass

def yahoo_scraper():
    today = datetime.now(eastern_tz).date()
    engine = create_engine(f"mysql+pymysql://{uname}:{pwd}@{hostname}/{dbname}")
    conn = engine.connect()
    query = text('SELECT * FROM articles')
    data = pd.read_sql_query(query, conn)
    urls = data['Article URL'][(data['Publication Name'] == 'Yahoo') & (data['Do not scrape'] == 'N')]
    urls.dropna(inplace=True)
    if len(urls) > 0:
        for url in urls:
            try:
                ua = get_random_user_agent()
                headers = {
                    'User-Agent': ua
                }
                response = requests.get(url, headers=headers)
                response = requests.get(url)
                soup = BeautifulSoup(response.text, 'lxml')
                posts = soup.select('.item-hover-trigger')

                for post in posts:
                    try:
                        date = post.select_one('p').find_next().text
                        if 'h' in date:
                            try:
                                date = today - timedelta(hours=int(date.replace('h ago', '')))
                                my_date = date.strftime("%Y, %m, %d")
                            except:
                                date = datetime.strptime('20230215', "%Y%m%d").date()
                                my_date = date.strftime("%Y, %m, %d")
                        elif 'd' in date:
                            try:
                                date = today - timedelta(days=int(date.replace('d ago', '')))
                                my_date = date.strftime("%Y, %m, %d")
                            except:
                                date = datetime.strptime('20230215', "%Y%m%d").date()
                                my_date = date.strftime("%Y, %m, %d")       
                        try:
                            delta = today - date
                        except:
                            delta = timedelta(days=5)
                        if delta < timedelta(days=3):
                            link = post.select_one('h4 a')['href']
                            header = post.select_one('h4').text
                            try:
                                sentence = post.select_one('p').text.split('.')
                                sentence = sentence[0]
                            except:
                                sentence = post.select_one('p').text

                            add_up(data, url, link, header, sentence, my_date)
                        else:
                            break
                    except:
                        pass
            except:
                pass

def nypost_scraper():
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
                response = requests.get(url, headers=headers)
                soup = BeautifulSoup(response.text, 'lxml')
                posts = soup.select('.story.story--archive.story--i-flex')        
                for post in posts:
                    try:
                        date = post.select_one('span').text.split('|')[0].strip()
                        try:
                            date = datetime.strptime(date, "%B %d, %Y").date()
                            my_date = date.strftime("%Y, %m, %d")
                        except:
                            date = datetime.strptime('20230215', "%Y%m%d").date()
                            my_date = date.strftime("%Y, %m, %d")             

                        try:
                            delta = today - date
                        except:
                            delta = timedelta(days=5)
                        if delta < timedelta(days=3):
                            link = post.select_one('a')['href']
                            header = post.select_one('h3').text.strip()
                            try:
                                sentence = post.select_one('p').text.strip().split('.')
                                sentence = sentence[0]
                            except:
                                sentence = post.select_one('p').text.strip()


                            add_up(data, url, link, header, sentence, my_date)
                        else:
                            break
                    except:
                        pass
            except:
                pass

def foxsports_scraper():
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
                response = requests.get(url, headers=headers)
                soup = BeautifulSoup(response.text, 'lxml')
                posts = soup.select('a.news')

                for post in posts:
                    try:
                        date = post.select_one('.article-time-source').text.strip()
                        if 'H' in date:
                            try:
                                date = today - timedelta(hours=int(date[0]))
                                my_date = date.strftime("%Y, %m, %d")
                            except:
                                date = datetime.strptime('20230215', "%Y%m%d").date()
                                my_date = date.strftime("%Y, %m, %d")
                        elif 'D' in date:
                            try:
                                date = today - timedelta(days=int(date[0]))
                                my_date = date.strftime("%Y, %m, %d")
                            except:
                                date = datetime.strptime('20230215', "%Y%m%d").date()
                                my_date = date.strftime("%Y, %m, %d")
                        else:
                            date = datetime.strptime('20230215', "%Y%m%d").date()
                            my_date = date.strftime("%Y, %m, %d")
                        try:
                            delta = today - date
                        except:
                            delta = timedelta(days=5)
                        if delta < timedelta(days=3):
                            link = post['href']
                            link = 'https://www.foxsports.com' + link
                            header = post.select_one('h3').text.strip()
                            try:
                                sentence = post.select_one('span').text.strip().split('.')
                                sentence = sentence[0]
                            except:
                                sentence = post.select_one('span').text.strip()

                            add_up(data, url, link, header, sentence, my_date)
                        else:
                            pass
                    except:
                        pass
            except:
                pass

def insider_scraper():
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
                response = requests.get(url, headers=headers)
                soup = BeautifulSoup(response.text, 'lxml')
                posts = soup.select('.river-item.featured-post')
                    
                for post in posts:
                    try:
                        date = post.select_one('.tout-timestamp').text.strip()
                        try:
                            date = datetime.fromisoformat(date[:-1]).date()
                            my_date = date.strftime("%Y, %m, %d")
                        except:
                            date = datetime.strptime('20230215', "%Y%m%d").date()
                            my_date = date.strftime("%Y, %m, %d")             

                        try:
                            delta = today - date
                        except:
                            delta = timedelta(days=55)
                        if delta < timedelta(days=50):
                            link = post.select_one('h2 a')['href']
                            link = 'https://www.insider.com' + link
                            header = post.select_one('h2').text.strip()
                            try:
                                sentence = post.select_one('.tout-copy.river.body-regular').text.strip().split('.')
                                sentence = sentence[0]
                            except:
                                sentence = post.select_one('.tout-copy.river.body-regular').text.strip()

                            add_up(data, url, link, header, sentence, my_date)
                        else:
                            pass
                    except:
                        pass
            except:
                pass

def tampabay_scraper():
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
                        try:
                            date = post.select_one('.timestamp span')['title']
                            date = datetime.strptime(date, '%Y-%m-%dT%H:%M:%S.%fZ').date()
                        except:
                            date = datetime.strptime('20230215', "%Y%m%d").date()
                            
                        try:
                            delta = datetime.now(eastern_tz).date() - date
                        except:
                            delta = timedelta(days=5)
                        if delta < timedelta(days=3):
                            my_date = date.strftime("%Y, %m, %d")
                            post_link = 'https://www.tampabay.com' + post.select_one('.headline a')['href']
                            res = s.get(post_link)
                            soup = BeautifulSoup(res.text, 'lxml')
                            header = soup.select_one('h1').text
                            try:
                                sentence = soup.select_one('.article__summary').text.split('.')
                                sentence = sentence[0]
                            except:
                                sentence = soup.select_one('.article__summary').text
                            link = res.url
                            add_up(data, url, link, header, sentence, my_date)
                        else:
                            break
                    except:
                        pass
            except:
                pass

def sporting_news():
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
                        header = soup.select_one('h1').text.strip()
                        try:
                            sentence = soup.select_one('p').text.strip().split('.')
                            sentence = sentence[0]
                        except:
                            sentence = soup.select_one('p').text.strip()
                        try:
                            date = soup.select_one('time')['datetime']
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
                            add_up(data, url, link, header, sentence, my_date)
                        else:
                            break
                    except:
                        pass
            except:
                pass

def northjersey_scraper():
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
                        try:
                            date = post['date-published']
                            date = datetime.strptime(date, "%Y-%m-%d %H:%M:%S %z %Z").replace(tzinfo=None).date()
                        except:
                            date = post['publishdate']
                            date = datetime.strptime(date, "%Y-%m-%d %H:%M:%S %z %Z").replace(tzinfo=None).date()
                    
                        try:
                            delta = datetime.now(eastern_tz).date() - date
                        except:
                            delta = timedelta(days=5)
                        if delta < timedelta(days=3):
                            link = post['url']
                            res = requests.get(link)
                            soup = BeautifulSoup(res.text, 'lxml')
                            header = soup.select_one('h1').text
                            my_date = date.strftime("%Y, %m, %d")
                            try:
                                sentence = soup.select_one('.gnt_ar_b_p').text.split('FLA.', '')
                                sentence = sentence.split('.')
                                sentence = sentence[0]                          
                            except:
                                sentence = post['descripton'] 
                            add_up(data, url, link, header, sentence, my_date)
                        else:
                            break
                    except:
                        pass
            except:
                pass

def theathletic_scraper():
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
                        post_link = post_link = post['href']
                        res = s.get(post_link)
                        soup = BeautifulSoup(res.text, 'lxml')
                        try:
                            date = soup.select_one('.sc-294a6039-3.kpapNT').text
                            date = datetime.strptime(date, "%b %d, %Y").date()
                        except:
                            date = datetime.strptime('20230215', "%Y%m%d").date()
                            
                        try:
                            delta = datetime.now(eastern_tz).date() - date
                        except:
                            delta = timedelta(days=20)
                        if delta < timedelta(days=15):
                            my_date = date.strftime("%Y, %m, %d")
                            link = res.url
                            header = soup.select_one('h1').text.strip()
                            try:
                                sentence = soup.select_one('.bodytext1').text.strip().split('.')
                                sentence = sentence[0]
                            except:
                                sentence = soup.select_one('.bodytext1').text.strip()
                            add_up(data, url, link, header, sentence, my_date)
                        else:
                            break
                    except:
                        pass
            except:
                pass

def apnews_scraper():
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
                            header = post.select_one('h2').text
                            try:
                                sentence = post.select_one('p').text.split('.')
                                sentence = sentence[0]
                            except:
                                sentence = post.select_one('p').text
                            link = 'https://apnews.com' + post.select_one('.CardHeadline a')['href']
                            
                            add_up(data, url, link, header, sentence, my_date, author)
                        else:
                            break
                    else:
                        pass
                except:
                    pass
        except:
            pass

def mlb_scraper():
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
                        try:
                            date = post.select_one('.article-item__contributor-date')['data-date']
                            date = datetime.fromisoformat(date.replace("Z", "+00:00")).date()
                        except:
                            date = datetime.strptime('20230215', "%Y%m%d").date()
                    
                        try:
                            delta = datetime.now(eastern_tz).date() - date
                        except:
                            delta = timedelta(days=5)
                        if delta < timedelta(days=3):
                            my_date = date.strftime("%Y, %m, %d")
                            header = post.select_one('h1').text.strip()
                            try:
                                sentence = post.select_one('p').text.replace('  ', '').replace('\n', ' ').split('.')
                                sentence = sentence[0]
                            except:
                                sentence = post.select_one('p').text.replace('  ', '').replace('\n', '')
                            link = 'https://www.mlb.com' + post.select_one('.p-button__link')['href']
                            
                            add_up(data, url, link, header, sentence, my_date, author)
                        else:
                            break
                    else:
                        pass
                except:
                    pass
        except:
            pass

def mlb_extra_scraper():
    s = session()
    engine = create_engine(f"mysql+pymysql://{uname}:{pwd}@{hostname}/{dbname}")
    engine = engine
    conn = engine.connect()
    query = text('SELECT * FROM articles')
    data = pd.read_sql_query(query, conn)
    urls = ['https://www.mlb.com/yankees/news', 'https://www.mlb.com/mets/news']
    authors = ['Bryan Hoch', 'Anthony DiComo']
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
                    for author in authors:
                        if author in post.text:
                            try:
                                date = post.select_one('.article-item__contributor-date')['data-date']
                                date = datetime.fromisoformat(date.replace("Z", "+00:00")).date()
                            except:
                                date = datetime.strptime('20230215', "%Y%m%d").date()
                        
                            try:
                                delta = datetime.now(eastern_tz).date() - date
                            except:
                                delta = timedelta(days=5)
                            if delta < timedelta(days=3):
                                my_date = date.strftime("%Y, %m, %d")
                                header = post.select_one('h1').text.strip()
                                sentence = post.select_one('p').text.split('Fla.')[-1].replace('--', '')
                                try:
                                    sentence = sentence.replace('  ', '').replace('\n', ' ').split('.')
                                    sentence = sentence[0]
                                except:
                                    sentence = post.select_one('p').text.replace('  ', '').replace('\n', '')
                                link = 'https://www.mlb.com' + post.select_one('.p-button__link')['href']
                                add_up(data, url, link, header, sentence, my_date, author)
                        else:
                            pass
                except:
                    pass
        except:
            pass

def courant_scraper():
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
                response = requests.get(url, headers=headers)
                soup = BeautifulSoup(response.text, 'lxml')
                posts_table = soup.select_one('.author-stories-feed')
                posts = posts_table.select('article')
                for post in posts:
                    try:
                        date = post.select_one('time').text.split('at')[0].strip()
                        try:
                            date = datetime.strptime(date,"%B %d, %Y").date()
                            my_date = date.strftime("%Y, %m, %d")
                        except:
                            date = datetime.strptime('20230215', "%Y%m%d").date()
                            my_date = date.strftime("%Y, %m, %d")             

                        try:
                            delta = today - date
                        except:
                            delta = timedelta(days=5)
                        if delta < timedelta(days=3):
                            header = post.select_one('.article-title').text.strip()
                            link = post.select_one('.article-title')['href']
                            try:
                                sentence = post.select_one('.excerpt').text.strip().split('.')
                                sentence = sentence[0]
                            except:
                                sentence = post.select_one('.excerpt').text.strip()

                            add_up(data, url, link, header, sentence, my_date)
                        else:
                            break
                    except:
                        pass
            except:
                pass

def wsj_scraper():
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
                            delta = timedelta(days=11)

                        if delta < timedelta(days=10):
                            my_date = date.strftime("%Y, %m, %d") 
                            header = json_data['data']['headline']
                            try:
                                sentence = json_data['data']['summary'].split('.')
                                sentence = sentence[0]
                            except:
                                sentence = json_data['data']['summary']
                            link = json_data['data']['canonical_url']
                            add_up(data, url, link, header, sentence, my_date)
                        else:
                            break
                    except:
                        pass
            except:
               pass
        
def nydailynews_scraper():
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
                        res = s.get(post_link)
                        soup = BeautifulSoup(res.text, 'lxml')
                        try:
                            date = soup.select_one('time')['datetime']
                            date = datetime.strptime(date, '%Y-%m-%d %H:%M:%S').date()
                        except:
                            date = datetime.strptime('20230215', "%Y%m%d").date()
                        
                        try:
                            delta = datetime.now(eastern_tz).date() - date
                        except:
                            delta = timedelta(days=22)
                        if delta < timedelta(days=20):
                            my_date = date.strftime("%Y, %m, %d")
                            link = res.url
                            header = soup.select_one('h1').text
                            sentence = soup.select_one('article p').text.split('Fla.')[-1].replace('—', '').strip()
                            try:
                                sentence = sentence.split('.')
                                sentence = sentence[0]
                            except:
                                sentence = sentence
                            add_up(data, url, link, header, sentence, my_date)
                        else:
                            break
                    except:
                        pass
            except:
                pass
            
def si_scraper():
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
                scraper = cloudscraper.create_scraper(delay=5)
                response = scraper.get(url, headers=headers)
                st.text(response)
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
                            sentence = soup.select_one('.m-detail--body p').text.replace('\xa0', ' ')
                            add_up(data, url, link, header, sentence, my_date)
                        else:
                            break
                    except:
                        pass
            except:
                pass
def sny_scraper():
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
                                sentence = sentence = soup.select_one('.article-body').text.split('.')
                                sentence = sentence[0]
                            except:
                                sentence = soup.select_one('.article-body').text
                            link = post_link
                            my_date = date.strftime("%Y, %m, %d")
                            add_up(data, url, link, header, sentence, my_date)                    
                        else:
                            break
                    except:
                        pass
            except:
                pass

def newsday_scraper():  
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
                            date = datetime.strptime(date, '%Y-%m-%dT%H:%M:%S.%fZ').date()
                        except:
                            date = datetime.strptime('20230215', "%Y%m%d").date()                
                        try:
                            delta = datetime.now(eastern_tz).date() - date
                        except:
                            delta = timedelta(days=5)

                        if delta < timedelta(days=3):
                            header = post['headline'].replace('\xa0', ' ')
                            try:
                                sentence = post['lead']
                                sentence = sentence.split('.')
                                sentence = sentence[0]
                            except:
                                sentence = post['lead']
                            my_date = date.strftime("%Y, %m, %d")
                            link = post['url']
                            add_up(data, url, link, header, sentence, my_date)
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
        # nytimes_scraper()
        # forbes_scraper()
        # nj_scraper()
        # fangraph_scraper()
        # cbs_sports_scraper()
        # ringer_scraper()
        # sportsbusinessjournal_scraper()
        # yahoo_scraper()
        # nypost_scraper()
        # foxsports_scraper()
        # insider_scraper()
        # tampabay_scraper()
        # sporting_news()
        # northjersey_scraper()
        #theathletic_scraper()
        # apnews_scraper()
        #mlb_scraper()
        #mlb_extra_scraper()
        #courant_scraper()
        #wsj_scraper()
        #si_scraper()
        #nydailynews_scraper()
        si_scraper()
        # sny_scraper()
        #newsday_scraper()
        

        return item_list, post_item_list
