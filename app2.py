from latest_user_agents import get_random_user_agent
import csv
import re
import pandas as pd
import streamlit as st
from all_scraper import NewsScraper
from sqlalchemy import create_engine, text
from datetime import datetime
from html2image import Html2Image
hti = Html2Image()
from playwright.sync_api import sync_playwright

def get_image(link, image):
    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page()
        page.goto(link)
        page.screenshot(path=f"{image}", type= 'jpeg', quality= 10, 
        animations= 'disabled', clip= {'x': 0, 'y': 0, 'width': 10000, 'height': 10000})
        browser.close()

if 'engine' not in st.session_state:
    hostname=st.secrets['hostname']
    dbname=st.secrets['dbname']
    uname=st.secrets['uname']
    pwd=st.secrets['pwd']
    engine = create_engine(f"mysql+pymysql://{uname}:{pwd}@{hostname}/{dbname}")
    st.session_state['engine'] = engine

@st.cache_data
def convert_df(df):
   return df.to_csv(index=False).encode('utf-8')

def delete_blacklisted(df_a):
    engine = st.session_state['engine']
    conn = engine.connect()
    query = text('SELECT * FROM black_list')
    df_b = pd.read_sql_query(query, conn)
    links_to_drop = df_a['Post key'].isin(df_b['Post key'])
    df_a = df_a[~links_to_drop]
    return df_a

def downlaod_commited(symb):
    engine = st.session_state['engine']
    conn = engine.connect()
    query = text('SELECT * FROM commit')
    df = pd.read_sql_query(query, conn)
    df = df[df['Post key'].str.contains(fr'{symb}')]
    df = df.drop(['Date', 'Post Link', 'Post key', 'Number of Bylines'], axis=1)
    csv = convert_df(df)
    return csv

def add_paywall(text, symb):
# define the pattern to select the link
    pattern = r'(https?://\S+)'

    # find the link in the text
    link = re.findall(pattern, text)[0]

    # add text to the link
    new_text = text.replace(link, f'{symb} {link}')

    return new_text

def add_hash_tags(text, symb):
# define the pattern to select the link
    pattern = r'(https?://\S+)'

    # find the link in the text
    link = re.findall(pattern, text)[0]

    # add text to the link
    new_text = text.replace(link, f'{link} {symb}')

    return new_text

def create_database():
    if 'engine' not in st.session_state:
        hostname=st.secrets['hostname']
        dbname=st.secrets['dbname']
        uname=st.secrets['uname']
        pwd=st.secrets['pwd']
        engine = create_engine(f"mysql+pymysql://{uname}:{pwd}@{hostname}/{dbname}")
        st.session_state['engine'] = engine
    # Run the scrapers
    scraper = NewsScraper()
    info, post = scraper.scrapers()
    df_info = pd.DataFrame(info)
    df_post = pd.DataFrame(post)
    try:
        clean_post = delete_blacklisted(df_post)
        clean_post.to_csv('temp_database.csv', index=False, encoding='utf-8') #to correct later
    except:
        no_data_df = pd.DataFrame(columns=['Text', 'Date', 'Post Link', 'Post key'])
        clean_post = delete_blacklisted(no_data_df)
        clean_post.to_csv('temp_database.csv', index=False, encoding='utf-8') #to correct later 

def delete_rows(selected_rows):
    engine = st.session_state['engine']
    selected_df = st.session_state['data2'].loc[selected_rows, :]
    #saving to black_list database for the so as to not to extract in the future
    selected_df.to_sql(name='black_list', con=engine, schema='hardball2019_bbwaa', if_exists='append', index=False)
    #drop the rows from the web app
    for index, row in st.session_state['data1'].iterrows():
        if index in selected_rows:
            st.session_state['data1'] = st.session_state['data1'].drop(index)
            st.session_state['data2'] = st.session_state['data2'].drop(index)
    st.session_state["default_checkbox_value"] = False
    st.experimental_rerun()

def add_rows_to_new_database(selected_rows):
    engine = st.session_state['engine']
    selected_df = st.session_state['data2'].loc[selected_rows, :]
    #clean_selected_df = clean_data(selected_df)
    #saving to commit database for the next step
    selected_df.to_sql(name='commit', con=engine, schema='hardball2019_bbwaa', if_exists='append', index=False)  
    #saving to black_list database for the so as to not to extract in the future
    selected_df.to_sql(name='black_list', con=engine, schema='hardball2019_bbwaa', if_exists='append', index=False)
    #drop the rows from the web app
    for index, row in st.session_state['data1'].iterrows():
        if index in selected_rows:
            st.session_state['data1'] = st.session_state['data1'].drop(index)
            st.session_state['data2'] = st.session_state['data2'].drop(index)
    st.session_state["default_checkbox_value"] = False
    st.experimental_rerun()

def main():
    pass

st.set_page_config(page_title="My Web App", page_icon=":memo:", layout="wide")
st.title("Latest News Extractor")
st.warning('Please click on the scrape button to refresh the page, especially if you have just loaded it. The displayed data may have been removed or finalized.')

scrape_button = st.button('Scrape')
if scrape_button:
    st.session_state['engine'].dispose()
    for key in st.session_state.keys():
        del st.session_state[key]
    create_database()
    #st.session_state

if 'data1' not in st.session_state:
    try:
        df1 = pd.read_csv("temp_database.csv")
        df2 = pd.read_csv("temp_database.csv")
        st.session_state['data1'] = df1
        st.session_state['data2'] = df2
    except:
        st.warning('The scraper has no scraped data to display. Click on the scrape to display the latest news.', icon="⚠️")
        st.stop()
        
total_data = len(st.session_state['data1'])
st.subheader(f'Total Posts to be processed: {total_data}')

if st.session_state['data1'].empty:
    st.subheader('No more recent Aticles')
else:
    main()

# Create a container for the buttons
button_container = st.container()

# Add buttons to the container
col1, col2, col3, col4 = button_container.columns([1, 1, 1, 1])
del_button = col1.button("Delete Rows", key='del_button')
commit_button = col2.button("Commit Rows", key='commit_button')
select_all_button = col3.button('Select all')
deselect_all_button = col4.button('Deselect all')

button_container_style = """
display: flex;
justify-content: center;
align-items: center;
background-color: #008080;
border-radius: 10px;
padding: 10px;
"""

col1.markdown(f'<div style="{button_container_style}">', unsafe_allow_html=True)
col1.markdown('</div>', unsafe_allow_html=True)
col2.markdown(f'<div style="{button_container_style}">', unsafe_allow_html=True)
col2.markdown('</div>', unsafe_allow_html=True)
col3.markdown(f'<div style="{button_container_style}">', unsafe_allow_html=True)
col3.markdown('</div>', unsafe_allow_html=True)
col4.markdown(f'<div style="{button_container_style}">', unsafe_allow_html=True)
col4.markdown('</div>', unsafe_allow_html=True)

if "default_checkbox_value" not in st.session_state:
    st.session_state["default_checkbox_value"] = False
if select_all_button:
    st.session_state["default_checkbox_value"] = True
if deselect_all_button:
    st.session_state["default_checkbox_value"] = False

for index, row in st.session_state['data1'][:40].iterrows():
        if f'image_{index}' not in st.session_state:
            if "Twit($)ter" in row["Text"]:
                st.session_state[f'image_{index}'] = get_image(row['Post Link'], f'image_{index}.jpeg')

selected_rows = []
for index, row in st.session_state['data1'][:40].iterrows():
    row_container = st.container()
    col1, col2, col3, col4, col5, col6 = row_container.columns([5, 3, 2, 2, 2, 2])
    checkbox = col1.checkbox("check_box", key=f'box_{index}', value=st.session_state["default_checkbox_value"])
    if checkbox:
        selected_rows.append(index)
    if "Twit($)ter" in row["Text"]:
        edited_text = col1.text_area(f'post_{index}',row["Text"].replace("Twit($)ter", "").strip().replace('', ''), height=150)
        st.session_state['data2'].at[index, 'Text'] = edited_text
        col2.write("Twitter")
        date_obj = datetime.strptime(row["Date"], "%Y, %m, %d").strftime("%B %d, %Y")
        col2.write(date_obj)
        col2.image(f'image_{index}.jpeg')

    elif "Face($)book" in row["Text"]:
        edited_text = col1.text_area(f'post_{index}',row["Text"].replace("Face($)book", "").strip(), height=150)
        st.session_state['data2'].at[index, 'Text'] = edited_text
        col2.write("Facebook")
        date_obj = datetime.strptime(row["Date"], "%Y, %m, %d").strftime("%B %d, %Y")
        col2.write(date_obj)
    elif "I($)G" in row["Text"]:
        edited_text = col1.text_area(f'post_{index}',row["Text"].replace("I($)G", ""), height=150)
        st.session_state['data2'].at[index, 'Text'] = edited_text
        col2.write("IG")
        date_obj = datetime.strptime(row["Date"], "%Y, %m, %d").strftime("%B %d, %Y")
        col2.write(date_obj)
    elif "Linked($)in" in row["Text"]:
        edited_text = col1.text_area(f'post_{index}',row["Text"].replace("Linked($)in", "").strip(), height=150)
        st.session_state['data2'].at[index, 'Text'] = edited_text
        col2.write("Linkedin")
        date_obj = datetime.strptime(row["Date"], "%Y, %m, %d").strftime("%B %d, %Y")
        col2.write(date_obj)
    col1.write('---------------------------------------')
    yankees_button = col3.button("Yankees", key=f'yankee_{index}')
    mets_button = col4.button("Mets", key=f'mets_{index}')
    paywall_button = col5.button('Paywall', key=f'paywall_{index}')
    if row["Number of Bylines"] > 1:
        col6.info(f'Number of Bylines: {row["Number of Bylines"]}')

    #add $ sign to the posts
    if '<$>' not in row['Text']:
        if paywall_button:
            st.session_state['data1'].at[index, 'Text'] = add_paywall(row['Text'], '<$>')
            st.session_state['data2'].at[index, 'Text'] = add_paywall(row['Text'], '<$>')
            st.experimental_rerun()
    else:
        if paywall_button:
            st.session_state['data1'].at[index, 'Text'] = row['Text'].replace('<$>', '')
            st.session_state['data2'].at[index, 'Text'] = row['Text'].replace('<$>', '')
            st.experimental_rerun()

    #add #Yankees hashtags to the post
    if '#Yankees' not in row['Text']:
        if yankees_button:
            st.session_state['data1'].at[index, 'Text'] = add_hash_tags(row['Text'], '#Yankees')
            st.session_state['data2'].at[index, 'Text'] = add_hash_tags(row['Text'], '#Yankees')
            st.experimental_rerun()           
    else:
        if yankees_button:
            st.session_state['data1'].at[index, 'Text'] = row['Text'].replace('#Yankees', '')
            st.session_state['data2'].at[index, 'Text'] = row['Text'].replace('#Yankees', '')
            st.experimental_rerun()
            
    # Add #Mets hashtags to post
    if '#Mets' not in row['Text']:
        if mets_button:
            st.session_state['data1'].at[index, 'Text'] = add_hash_tags(row['Text'], '#Mets')
            st.session_state['data2'].at[index, 'Text'] = add_hash_tags(row['Text'], '#Mets')
            st.experimental_rerun()
    else:
        if mets_button:
            st.session_state['data1'].at[index, 'Text'] = row['Text'].replace('#Mets', '')
            st.session_state['data2'].at[index, 'Text'] = row['Text'].replace('#Mets', '')
            st.experimental_rerun()

# Add buttons to the container
button2_container = st.container()
col1, col2 = button2_container.columns([1, 1])
del_button2 = col1.button("Delete Rows", key='del_button2')
commit_button2 = col2.button("Commit Rows", key='commit_button2')

# Add a button to delete selected rows
if del_button or del_button2:
    delete_rows(selected_rows)

# Add a button to add selected rows to new database
if commit_button or commit_button2:
    add_rows_to_new_database(selected_rows)
    
downlaod_container = st.container()
downlaod_1, downlaod_2, downlaod_3, downlaod_4 = downlaod_container.columns([1, 1, 1, 1])
downlaod_button_1 = downlaod_1.download_button("Press to Download Twitter Posts", downlaod_commited('Twit\(\$\)ter'), "twitter_posts.csv", "text/csv", key='twitter_download-csv')
downlaod_button_2 = downlaod_2.download_button("Press to Download Facebook Posts", downlaod_commited('Face\(\$\)book'), "fb_posts.csv", "text/csv", key='fb_download-csv')
downlaod_button_3 = downlaod_3.download_button("Press to Download Instagram Posts", downlaod_commited('I\(\$\)G'), "ig_posts.csv", "text/csv", key='ig_download-csv')
downlaod_button_3 = downlaod_4.download_button("Press to Download LinkedIn Posts", downlaod_commited('Linked\(\$\)in'), "linkedin_posts.csv", "text/csv", key='linkedin_download-csv')
