import streamlit as st
import requests
from bs4 import BeautifulSoup
import pandas as pd
from datetime import datetime, timedelta
from latest_user_agents import get_random_user_agent
from sqlalchemy import create_engine, text

hostname=st.secrets['hostname']
dbname=st.secrets['dbname']
uname=st.secrets['uname']
pwd=st.secrets['pwd']
engine = create_engine(f"mysql+pymysql://{uname}:{pwd}@{hostname}/{dbname}")
engine = engine
conn = engine.connect()
query = text('SELECT * FROM articles')
data = pd.read_sql_query(query, conn)

post_item_list =[]
item_list = []

def add_up(data, url, link, header, sentence, my_date):
    author_twitter = str(data.loc[data['Article URL'] == url, 'Author Twitter'].item()).replace('"', '')
    pub_twitter = str(data.loc[data['Article URL'] == url, 'Publication Twitter'].item()).replace('"', '')
    author_fb = str(data.loc[data['Article URL'] == url, 'Author FB'].item()).replace('"', '')
    pub_fb = str(data.loc[data['Article URL'] == url, 'Publication FB'].item()).replace('"', '')
    author_ig = str(data.loc[data['Article URL'] == url, 'Author IG'].item()).replace('"', '')
    pub_ig = str(data.loc[data['Article URL'] == url, 'Publication IG'].item()).replace('"', '')
    author_linkedin = str(data.loc[data['Article URL'] == url, 'Author LinkedIn'].item()).replace('"', '')
    pub_linkedin = str(data.loc[data['Article URL'] == url, 'Publication LinkedIn'].item()).replace('"', '')
    paywall = str(data.loc[data['Article URL'] == url, 'Default Paywall  (Y/N)'].item()).replace('"', '')

    if 'nan' in author_twitter:
        author_twitter = str(data.loc[data['Article URL'] == url, 'Author Name'].item()).replace('"', '')
    if 'nan' in pub_twitter:
        pub_twitter = str(data.loc[data['Article URL'] == url, 'Publication Name'].item()).replace('"', '')

    if 'nan' in author_fb:
        author_fb = str(data.loc[data['Article URL'] == url, 'Author Name'].item()).replace('"', '')
    if 'nan' in pub_fb:
        pub_fb = str(data.loc[data['Article URL'] == url, 'Publication Name'].item()).replace('"', '')

    if 'nan' in author_ig:
        author_ig = str(data.loc[data['Article URL'] == url, 'Author Name'].item()).replace('"', '')
    if 'nan' in pub_ig:
        pub_ig = str(data.loc[data['Article URL'] == url, 'Publication Name'].item()).replace('"', '')

    if 'nan' in author_linkedin:
        author_linkedin = str(data.loc[data['Article URL'] == url, 'Author Name'].item()).replace('"', '')
    if 'nan' in pub_linkedin:
        pub_linkedin = str(data.loc[data['Article URL'] == url, 'Publication Name'].item()).replace('"', '')

    if 'N' in paywall:
        paywall = ''
    elif 'Y' in paywall:
        paywall = '<$>' 
        
    sentence = sentence.replace('..', '').encode('utf-8').decode('utf-8').replace('“', '').replace('”', '').replace('$', '')
    post = f'''
    '{header}' by {author_twitter} for {pub_twitter}: {sentence}.. {paywall}{link} Twit($)ter
    '''
    post_item = {
        'Text': post.strip(),
        'Date': my_date,
        'Post Link': link
    }
    post_item_list.append(post_item)
    post = f'''
    '{header}' by {author_fb} for {pub_fb}: {sentence}.. {paywall}{link} Face($)book
    '''
    post_item = {
        'Text': post.strip(),
        'Date': my_date,
        'Post Link': link
    }
    post_item_list.append(post_item)
    post = f'''
    '{header}' by {author_ig} for {pub_ig}: {sentence}.. {paywall}{link} I($)G

    VISIT THE LINK IN OUR BIO TO READ THIS ARTICLE
    '''
    post_item = {
        'Text': post.strip(),
        'Date': my_date,
        'Post Link': link
    }
    post_item_list.append(post_item)
    post = f'''
    '{header}' by {author_linkedin} for {pub_linkedin}: {sentence}.. {paywall}{link} Linked($)in
    '''
    post_item = {
        'Text': post.strip(),
        'Date': my_date,
        'Post Link': link
    }
    post_item_list.append(post_item)

    item = {
        'Date': my_date,
        'Link': link,
        'Title': header,
        'Sentence': sentence,
        'publication_name' : data.loc[data['Article URL'] == url, 'Publication Name'].item(),
        'author_name' : data.loc[data['Article URL'] == url, 'Author Name'].item(),
        'author_twitter' : data.loc[data['Article URL'] == url, 'Author Twitter'].item(),
        'author_ig' : data.loc[data['Article URL'] == url, 'Author IG'].item(),
        'author_fb' : data.loc[data['Article URL'] == url, 'Author FB'].item(),
        'author_linkedin' : data.loc[data['Article URL'] == url, 'Author LinkedIn'].item(),
        'publication_twitter' : data.loc[data['Article URL'] == url, 'Publication Twitter'].item(),
        'publication_ig' : data.loc[data['Article URL'] == url, 'Publication IG'].item(),
        'publication_fb' : data.loc[data['Article URL'] == url, 'Publication FB'].item(),
        'publication_linkedin' : data.loc[data['Article URL'] == url, 'Publication LinkedIn'].item(),
        'paywall' : data.loc[data['Article URL'] == url, 'Default Paywall  (Y/N)'].item()
        
    }
    item_list.append(item)

def nytimes_scraper(data):
    today = datetime.now()
    query = text('SELECT * FROM articles')
    data = pd.read_sql_query(query, conn)
    urls = data['Article URL'][(data['Publication Name'] == 'The New York Times') & (data['Do not scrape'] == 'N')]
    urls.dropna(inplace=True)     
    if len(urls) > 0:
        for url in urls:
            ua = get_random_user_agent()
            headers = {
                'User-Agent': ua
            }
            response = requests.get(url, headers=headers)
            response = requests.get(url)
            soup = BeautifulSoup(response.text, 'lxml')
            posts = soup.select('.css-112uytv')

            posts = soup.select('.css-112uytv')
            for post in posts:
                link_date = post.select_one('.css-1l4spti a')['href']
                date = link_date.split('/sports/baseball')
                date = date[0].replace('/', '')
                try:
                    date = datetime.strptime(date, "%Y%m%d")
                    my_date = date.strftime("%Y, %m, %d")
                except:
                    date = datetime.strptime('20230215', "%Y%m%d")
                    my_date = date.strftime("%Y, %m, %d")
                    
                delta = today - date

                if delta < timedelta(days=3):
                    link = 'https://www.nytimes.com' + link_date
                    header = post.select_one('h2').text
                    sentence = post.select_one('p').text

                    add_up(data, url, link, header, sentence, my_date)
                else:
                    pass
    else:
        pass
        
def forbes_scraper(data):
    today = datetime.now()
    query = text('SELECT * FROM articles')
    data = pd.read_sql_query(query, conn)
    urls = data['Article URL'][(data['Publication Name'] == 'Forbes') & (data['Do not scrape'] == 'N')]
    urls.dropna(inplace=True)
    if len(urls) > 0:
        for url in urls:
            ua = get_random_user_agent()
            headers = {
                'User-Agent': ua
            }
            response = requests.get(url, headers=headers)
            response = requests.get(url)
            soup = BeautifulSoup(response.text, 'lxml')
            posts = soup.select('article')
            for post in posts:
                date = post['data-date']
                try:
                    date = datetime.fromtimestamp(int(date) / 1000.0)
                    my_date = date.strftime("%Y, %m, %d")
                except:
                    date = datetime.strptime('20230215', "%Y%m%d")
                    my_date = date.strftime("%Y, %m, %d")
                    
                delta = today - date

                if delta < timedelta(days=3):
                    link = post.select_one('.stream-item__title')['href']
                    header = post.select_one('.stream-item__title').text
                    sentence = post.select_one('.stream-item__description').text

                    add_up(data, url, link, header, sentence, my_date)
                else:
                    pass
    else:
        pass

def nj_scraper(data):
    today = datetime.now()
    query = text('SELECT * FROM articles')
    data = pd.read_sql_query(query, conn)
    urls = data['Article URL'][(data['Publication Name'] == 'NJ.com') & (data['Do not scrape'] == 'N')]
    urls.dropna(inplace=True)
    if len(urls) > 0:
        for url in urls:
            ua = get_random_user_agent()
            headers = {
                'User-Agent': ua
            }
            response = requests.get(url, headers=headers)
            response = requests.get(url)
            soup = BeautifulSoup(response.text, 'lxml')
            posts = soup.select('.river-item')

            for post in posts:
                date = post.select_one('time')['datetime']
                try:
                    date = datetime.fromtimestamp(int(date))
                    my_date = date.strftime("%Y, %m, %d")
                except:
                    date = datetime.strptime('20230215', "%Y%m%d")
                    my_date = date.strftime("%Y, %m, %d")           

                delta = today - date
                if delta < timedelta(days=3):
                    link = post.select_one('a.river-item__headline-link')['href']
                    header = post.select_one('h2').text
                    sentence = post.select_one('p').text

                    add_up(data, url, link, header, sentence, my_date)
                else:
                    pass

class NewsScraper:
    
    @staticmethod
    def scrapers():
        #nj_scraper(data)
        nytimes_scraper(data)
        #forbes_scraper(data)
        return item_list, post_item_list
