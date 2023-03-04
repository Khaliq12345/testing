import streamlit as st
import requests
from requests import session
from bs4 import BeautifulSoup
import pandas as pd
from datetime import datetime, timedelta
from latest_user_agents import get_random_user_agent
from sqlalchemy import create_engine, text

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
    today = datetime.now()
    engine = create_engine(f"mysql+pymysql://{uname}:{pwd}@{hostname}/{dbname}")
    conn = engine.connect()
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
                    
                try:
                    delta = today - date
                except:
                    delta = 5
                if delta < timedelta(days=3):
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
    else:
        pass
        
def forbes_scraper():
    today = datetime.now()
    engine = create_engine(f"mysql+pymysql://{uname}:{pwd}@{hostname}/{dbname}")
    conn = engine.connect()
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
                    
                try:
                    delta = today - date
                except:
                    delta = 5
                if delta < timedelta(days=3):
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
    else:
        pass

def nj_scraper():
    today = datetime.now()
    engine = create_engine(f"mysql+pymysql://{uname}:{pwd}@{hostname}/{dbname}")
    conn = engine.connect()
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

                try:
                    delta = today - date
                except:
                    delta = 5
                if delta < timedelta(days=3):
                    link = post.select_one('a.river-item__headline-link')['href']
                    header = post.select_one('h2').text
                    try:
                        sentence = post.select_one('.river-item__summary').text.replace('\n', ' ').split('.')
                        sentence = sentence[0]
                    except:
                        sentence = post.select_one('.river-item__summary').text.replace('\n', ' ')

                    add_up(data, url, link, header, sentence, my_date)
                else:
                    pass

def fangraph_scraper():
    today = datetime.now()
    engine = create_engine(f"mysql+pymysql://{uname}:{pwd}@{hostname}/{dbname}")
    conn = engine.connect()
    query = text('SELECT * FROM articles')
    data = pd.read_sql_query(query, conn)
    urls = data['Article URL'][(data['Publication Name'] == 'FanGraphs') & (data['Do not scrape'] == 'N')]
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
            posts = soup.select('.post')

            for post in posts:
                meta = post.select_one('.postmeta_author')
                date = meta.find_next_sibling().text
                try:
                    date = datetime.strptime(date, "%B %d, %Y")
                    my_date = date.strftime("%Y, %m, %d")
                except:
                    date = datetime.strptime('20230215', "%Y%m%d")
                    my_date = date.strftime("%Y, %m, %d")             

                try:
                    delta = today - date
                except:
                    delta = 5
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

def cbs_sports_scraper():
    today = datetime.now()
    engine = create_engine(f"mysql+pymysql://{uname}:{pwd}@{hostname}/{dbname}")
    conn = engine.connect()
    query = text('SELECT * FROM articles')
    data = pd.read_sql_query(query, conn)
    urls = data['Article URL'][(data['Publication Name'] == 'CBS Sports') & (data['Do not scrape'] == 'N')]
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
            posts = soup.select('.asset')

            for post in posts:
                date = post.select_one('time').text
                if 'H' in date:
                    try:
                        date = today - timedelta(hours=int(date.replace('H ago', '')))
                        my_date = date.strftime("%Y, %m, %d")
                    except:
                        date = datetime.strptime('20230215', "%Y%m%d")
                        my_date = date.strftime("%Y, %m, %d")
                elif 'D' in date:
                    try:
                        date = today - timedelta(days=int(date.replace('D ago', '')))
                        my_date = date.strftime("%Y, %m, %d")
                    except:
                        date = datetime.strptime('20230215', "%Y%m%d")
                        my_date = date.strftime("%Y, %m, %d")       
                try:
                    delta = today - date
                except:
                    delta = 5
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

def ringer_scraper():
    today = datetime.now().date()
    engine = create_engine(f"mysql+pymysql://{uname}:{pwd}@{hostname}/{dbname}")
    conn = engine.connect()
    query = text('SELECT * FROM articles')
    data = pd.read_sql_query(query, conn)
    urls = data['Article URL'][(data['Publication Name'] == 'The Ringer') & (data['Do not scrape'] == 'N')]
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
            posts = soup.select('.c-compact-river__entry ')

            for post in posts:
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
                    delta = 5
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

def sportsbusinessjournal_scraper():
    today = datetime.now()
    engine = create_engine(f"mysql+pymysql://{uname}:{pwd}@{hostname}/{dbname}")
    conn = engine.connect()
    query = text('SELECT * FROM articles')
    data = pd.read_sql_query(query, conn)
    urls = data['Article URL'][(data['Publication Name'] == 'Sports Business Journal') & (data['Do not scrape'] == 'N')]
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
            posts = soup.select('.article')[1:]

            for post in posts:
                date = post.select('span')[-1].text
                try:
                    date = datetime.strptime(date, "%A, %B %d, %Y")
                    my_date = date.strftime("%Y, %m, %d")
                except:
                    date = datetime.strptime('20230215', "%Y%m%d")
                    my_date = date.strftime("%Y, %m, %d")           

                try:
                    delta = today - date
                except:
                    delta = 5
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

def yahoo_scraper():
    today = datetime.now()
    engine = create_engine(f"mysql+pymysql://{uname}:{pwd}@{hostname}/{dbname}")
    conn = engine.connect()
    query = text('SELECT * FROM articles')
    data = pd.read_sql_query(query, conn)
    urls = data['Article URL'][(data['Publication Name'] == 'Yahoo') & (data['Do not scrape'] == 'N')]
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
            posts = soup.select('.item-hover-trigger')

            for post in posts:
                date = post.select_one('p').find_next().text
                if 'h' in date:
                    try:
                        date = today - timedelta(hours=int(date.replace('h ago', '')))
                        my_date = date.strftime("%Y, %m, %d")
                    except:
                        date = datetime.strptime('20230215', "%Y%m%d")
                        my_date = date.strftime("%Y, %m, %d")
                elif 'd' in date:
                    try:
                        date = today - timedelta(days=int(date.replace('d ago', '')))
                        my_date = date.strftime("%Y, %m, %d")
                    except:
                        date = datetime.strptime('20230215', "%Y%m%d")
                        my_date = date.strftime("%Y, %m, %d")       

                try:
                    delta = today - date
                except:
                    delta = 5
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
                    pass

def nypost_scraper():
    today = datetime.now()
    engine = create_engine(f"mysql+pymysql://{uname}:{pwd}@{hostname}/{dbname}")
    conn = engine.connect()
    query = text('SELECT * FROM articles')
    data = pd.read_sql_query(query, conn)
    urls = data['Article URL'][(data['Publication Name'] == 'New York Post') & (data['Do not scrape'] == 'N')]
    urls.dropna(inplace=True)
    if len(urls) > 0:
        for url in urls:
            ua = get_random_user_agent()
            headers = {
                'User-Agent': ua
            }
            response = requests.get(url, headers=headers)
            soup = BeautifulSoup(response.text, 'lxml')
            posts = soup.select('.story.story--archive.story--i-flex')        
            for post in posts:
                date = post.select_one('span').text.split('|')[0].strip()
                try:
                    date = datetime.strptime(date, "%B %d, %Y")
                    my_date = date.strftime("%Y, %m, %d")
                except:
                    date = datetime.strptime('20230215', "%Y%m%d")
                    my_date = date.strftime("%Y, %m, %d")             

                try:
                    delta = today - date
                except:
                    delta = 5
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
                    pass

def foxsports_scraper():
    today = datetime.now()
    engine = create_engine(f"mysql+pymysql://{uname}:{pwd}@{hostname}/{dbname}")
    conn = engine.connect()
    query = text('SELECT * FROM articles')
    data = pd.read_sql_query(query, conn)
    urls = data['Article URL'][(data['Publication Name'] == 'FOX Sports') & (data['Do not scrape'] == 'N')]
    urls.dropna(inplace=True)
    if len(urls) > 0:
        for url in urls:
            ua = get_random_user_agent()
            headers = {
                'User-Agent': ua
            }
            response = requests.get(url, headers=headers)
            soup = BeautifulSoup(response.text, 'lxml')
            posts = soup.select('a.news')

            for post in posts:
                date = post.select_one('.article-time-source').text.strip()
                if 'H' in date:
                    try:
                        date = today - timedelta(hours=int(date[0]))
                        my_date = date.strftime("%Y, %m, %d")
                    except:
                        date = datetime.strptime('20230215', "%Y%m%d")
                        my_date = date.strftime("%Y, %m, %d")
                elif 'D' in date:
                    try:
                        date = today - timedelta(days=int(date[0]))
                        my_date = date.strftime("%Y, %m, %d")
                    except:
                        date = datetime.strptime('20230215', "%Y%m%d")
                        my_date = date.strftime("%Y, %m, %d")
                else:
                    date = datetime.strptime('20230215', "%Y%m%d")
                    my_date = date.strftime("%Y, %m, %d")


                try:
                    delta = today - date
                except:
                    delta = 5
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

def insider_scraper():
    today = datetime.now()
    engine = create_engine(f"mysql+pymysql://{uname}:{pwd}@{hostname}/{dbname}")
    conn = engine.connect()
    query = text('SELECT * FROM articles')
    data = pd.read_sql_query(query, conn)
    urls = data['Article URL'][(data['Publication Name'] == 'Insider') & (data['Do not scrape'] == 'N')]
    urls.dropna(inplace=True)
    if len(urls) > 0:
        for url in urls:
            ua = get_random_user_agent()
            headers = {
                'User-Agent': ua
            }
            response = requests.get(url, headers=headers)
            soup = BeautifulSoup(response.text, 'lxml')
            posts = soup.select('.river-item.featured-post')
                
            for post in posts:
                date = post.select_one('.tout-timestamp').text.strip()
                try:
                    date = datetime.fromisoformat(date[:-1])
                    my_date = date.strftime("%Y, %m, %d")
                except:
                    date = datetime.strptime('20230215', "%Y%m%d")
                    my_date = date.strftime("%Y, %m, %d")             

                try:
                    delta = today - date
                except:
                    delta = 5
                if delta < timedelta(days=3):
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

def tampabay_scraper():
    url_2 = []
    engine = create_engine(f"mysql+pymysql://{uname}:{pwd}@{hostname}/{dbname}")
    engine = engine
    conn = engine.connect()
    query = text('SELECT * FROM articles')
    data = pd.read_sql_query(query, conn)
    urls = data['Article URL'][(data['Publication Name'] == 'Tampa Bay Times') & (data['Do not scrape'] == 'N')]
    urls.dropna(inplace=True)
    if len(urls) > 0:
        for url in urls:
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
                    date = post.select_one('.timestamp span')['title']
                    date = datetime.strptime(date, '%Y-%m-%dT%H:%M:%S.%fZ')
                except:
                    date = datetime.strptime('20230215', "%Y%m%d")
                    
                try:
                    delta = datetime.now() - date
                except:
                    delta = 5
                if delta < timedelta(days=3):
                    my_date = date.strftime("%Y, %m, %d")
                    post_link = 'https://www.tampabay.com' + post.select_one('.headline a')['href']
                    url_2.append(post_link)

    for u in url_2:
        res = s.get(u)
        soup = BeautifulSoup(res.text, 'lxml')
        header = soup.select_one('h1').text
        try:
            sentence = soup.select_one('.article__summary').text.split('.')
            sentence = sentence[0]
        except:
            sentence = soup.select_one('.article__summary').text
        link = res.url
        add_up(data, url, link, header, sentence, my_date)

def sporting_news():
    url_2 = []
    engine = create_engine(f"mysql+pymysql://{uname}:{pwd}@{hostname}/{dbname}")
    engine = engine
    conn = engine.connect()
    query = text('SELECT * FROM articles')
    data = pd.read_sql_query(query, conn)
    urls = data['Article URL'][(data['Publication Name'] == 'Sporting News') & (data['Do not scrape'] == 'N')]
    urls.dropna(inplace=True)
    if len(urls) > 0:
        for url in urls:
            s = session()
            ua = get_random_user_agent()
            headers = {
                'User-Agent': ua
            }
            response = s.get(url,  headers=headers)
            soup = BeautifulSoup(response.text, 'lxml')
            posts = soup.select('.list-item')
            for post in posts:
                post_link = 'https://www.sportingnews.com' + post.select_one('.list-item__title a')['href']
                url_2.append(post_link)

    for u in url_2:
        res = s.get(u)
        soup = BeautifulSoup(res.text, 'lxml')
        header = soup.select_one('h1').text.strip()
        try:
            sentence = soup.select_one('p').text.strip().split('.')
            sentence = sentence[0]
        except:
            sentence = soup.select_one('p').text.strip()
        try:
            date = soup.select_one('time')['datetime']
            date =  datetime.fromisoformat(date).replace(tzinfo=None)
        except:
            date = datetime.strptime('20230215', "%Y%m%d")
            
        try:
            delta = datetime.now() - date
        except:
            delta = 5
        if delta < timedelta(days=3):
            my_date = date.strftime("%Y, %m, %d")
            link = res.url
            add_up(data, url, link, header, sentence, my_date)
        else:
            break

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
            s = session()
            ua = get_random_user_agent()
            headers = {
                'User-Agent': ua
            }
            response = s.get(url,  headers=headers)
            soup = BeautifulSoup(response.text, 'lxml')
            posts = soup.select('promo-story-thumb-small')
            latest_post = soup.select_one('lit-story-thumb-large')
            posts.append(latest_post)
            for post in posts:
                try:
                    date = post['date-published']
                    date = datetime.strptime(date, "%Y-%m-%d %H:%M:%S %z %Z").replace(tzinfo=None)
                except:
                    date = post['publishdate']
                    date = datetime.strptime(date, "%Y-%m-%d %H:%M:%S %z %Z").replace(tzinfo=None)
            
                try:
                    delta = datetime.now() - date
                except:
                    delta = 5
                if delta < timedelta(days=3):
                    my_date = date.strftime("%Y, %m, %d")
                    header = post['title']
                    try:
                        sentence = post['descripton'].split('.')
                        sentence = sentence[0]
                    except:
                        sentence = post['descripton']
                    link = post['url']
                    
                    add_up(data, url, link, header, sentence, my_date)
                else:
                    break

def theathletic_scraper():
    url_2 = []
    engine = create_engine(f"mysql+pymysql://{uname}:{pwd}@{hostname}/{dbname}")
    engine = engine
    conn = engine.connect()
    query = text('SELECT * FROM articles')
    data = pd.read_sql_query(query, conn)
    urls = data['Article URL'][(data['Publication Name'] == 'The Athletic') & (data['Do not scrape'] == 'N')]
    urls.dropna(inplace=True)
    if len(urls) > 0:
        for url in urls:
            s = session()
            ua = get_random_user_agent()
            headers = {
                'User-Agent': ua
            }
            response = s.get(url,  headers=headers)
            soup = BeautifulSoup(response.text, 'lxml')
            posts = soup.select('.sc-95dc7848-0')
            for post in posts:
                post_link = post.select_one('a')['href']
                url_2.append(post_link)

    for u in url_2:
        res = s.get(u)
        soup = BeautifulSoup(res.text, 'lxml')
        try:
            date = soup.select_one('.sc-294a6039-3.kpapNT').text
            date = datetime.strptime(date, "%b %d, %Y")
        except:
            date = datetime.strptime('20230215', "%Y%m%d")
            
        try:
            delta = datetime.now() - date
        except:
            delta = 5
        if delta < timedelta(days=3):
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
            if author.upper() in post.text:
                try:
                    date = post.select_one('.Timestamp')['data-source']
                    date = datetime.strptime(date, "%Y-%m-%dT%H:%M:%SZ")
                except:
                    date = datetime.strptime('20230215', "%Y%m%d")
            
                try:
                    delta = datetime.now() - date
                except:
                    delta = 5
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
                    break
            else:
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
                    'Mike Lupica', 'Mike Petriello', 'Nathalie Alonso', 'Anthony DiComo', 'Bryan Hoch']
    all_author = []
    for author_n in author_names:
        if author_n in soup.text:
            all_author.append(author_n)
    for author in all_author:
        url = data['Article URL'][(data['Publication Name'] == 'MLB.com') & (data['Do not scrape'] == 'N') & (data['Author Name'] == author)].item()
        ua = get_random_user_agent()
        headers = {
            'User-Agent': ua
        }
        response = s.get(url,  headers=headers)
        soup = BeautifulSoup(response.text, 'lxml')
        posts = soup.select('article')
        for post in posts:
            if author in post.text:
                try:
                    date = post.select_one('.article-item__contributor-date')['data-date']
                    date = datetime.strptime(date, "%Y-%m-%dT%H:%M:%S.%fZ")
                except:
                    date = datetime.strptime('20230215', "%Y%m%d")
            
                try:
                    delta = datetime.now() - date
                except:
                    delta = 5
                if delta < timedelta(days=3):
                    my_date = date.strftime("%Y, %m, %d")
                    header = post.select_one('h1').text.strip()
                    try:
                        sentence = post.select_one('p').text.replace('  ', '').replace('\n', ' ').split('.')
                        sentence = sentence[0]
                    except:
                        sentence = post.select_one('p').text.replace('  ', '').replace('\n', ' ')
                    link = 'https://www.mlb.com' + post.select_one('.p-button__link')['href']
                    
                    add_up(data, url, link, header, sentence, my_date, author)
                    break
            else:
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

        return item_list, post_item_list
