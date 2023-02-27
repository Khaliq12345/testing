
import requests
from bs4 import BeautifulSoup
import pandas as pd
from datetime import datetime, timedelta
from latest_user_agents import get_random_user_agent

post_item_list =[]
item_list = []
PATH = "bbwaa_roster.xlsx"

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
        
    sentence = sentence.replace('..', '')
    post = f'"{header}" by {author_twitter} for {pub_twitter}: {sentence}.. {paywall}{link} Twit($)ter'
    post_item = {
        'Text': post,
        'Date': my_date,
        'Post Link': link
    }
    post_item_list.append(post_item)
    post = f'"{header}" by {author_fb} for {pub_fb}: {sentence}.. {paywall}{link} Face($)book'
    post_item = {
        'Text': post,
        'Date': my_date,
        'Post Link': link
    }
    post_item_list.append(post_item)
    post = f'"{header}" by {author_ig} for {pub_ig}: {sentence}.. {paywall}{link} I($)G'
    post_item = {
        'Text': post,
        'Date': my_date,
        'Post Link': link
    }
    post_item_list.append(post_item)
    post = f'"{header}" by {author_linkedin} for {pub_linkedin}: {sentence}.. {paywall}{link} Linked($)in'
    post_item = {
        'Text': post,
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

def nytimes_scraper():
    today = datetime.now()
    data = pd.read_excel(PATH)
    urls = data['Article URL'][data['Publication Name'] == 'The New York Times']
    for url in urls:
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
        
def forbes_scraper():
    today = datetime.now()
    data = pd.read_excel(PATH)
    urls = data['Article URL'][data['Publication Name'] == 'Forbes']
    for url in urls:
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

def nj_scraper():
    today = datetime.now()
    data = pd.read_excel(PATH)
    urls = data['Article URL'][data['Publication Name'] == 'NJ.com']
    for url in urls:
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
        nytimes_scraper()
        forbes_scraper()
        return item_list, post_item_list
