from latest_user_agents import get_random_user_agent
import csv
import re
import pandas as pd
import streamlit as st
from all_scraper import NewsScraper
from sqlalchemy import create_engine, text
from datetime import datetime

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

@st.cache_data
def delete_blacklisted(df_a):
    engine = st.session_state['engine']
    conn = engine.connect()
    query = text('SELECT * FROM black_list')
    df_b = pd.read_sql_query(query, conn)
    links_to_drop = df_a['Post Link'].isin(df_b['Post Link'])
    df_a = df_a[~links_to_drop]

    return df_a

def downlaod_commited():
    engine = st.session_state['engine']
    conn = engine.connect()
    query = text('SELECT * FROM commit')
    df = pd.read_sql_query(query, conn)
    df = df.drop(['Date', 'Post Link'], axis=1)
    csv = convert_df(df)
    return csv

@st.cache_data
def add_paywall(text, symb):
# define the pattern to select the link
    pattern = r'(https?://\S+)'

    # find the link in the text
    link = re.findall(pattern, text)[0]

    # add text to the link
    new_text = text.replace(link, f'{symb} {link}')

    return new_text

@st.cache_data
def add_hash_tags(text, symb):
# define the pattern to select the link
    pattern = r'(https?://\S+)'

    # find the link in the text
    link = re.findall(pattern, text)[0]

    # add text to the link
    new_text = text.replace(link, f'{link} {symb}')

    return new_text

@st.cache_data
def empty_database():
    df1 = pd.DataFrame()
    df2 = pd.DataFrame()
    st.session_state['data1'] = df1
    st.session_state['data2'] = df2
    st.experimental_rerun()

def create_database():
   
   for key in st.session_state.keys():
        del st.session_state[key]
    # Run the scrapers
   if 'engine' not in st.session_state:
       hostname=st.secrets['hostname']
       dbname=st.secrets['dbname']
       uname=st.secrets['uname']
       pwd=st.secrets['pwd']
       engine = create_engine(f"mysql+pymysql://{uname}:{pwd}@{hostname}/{dbname}")
       st.session_state['engine'] = engine

   scraper = NewsScraper()
   info, post = scraper.scrapers()
   df_info = pd.DataFrame(info)
   df_post = pd.DataFrame(post)
   clean_post = delete_blacklisted(df_post)
   clean_post.to_csv('temp_database.csv', index=False, encoding='utf-8') #to correct later

@st.cache_data
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
    st.experimental_rerun()

@st.cache_data
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
    st.experimental_rerun()

def main():
    pass

@st.cache_data
def add_signs(index, row):


st.set_page_config(page_title="My Web App", page_icon=":memo:", layout="wide")
st.title("Latest News Extractor")

scrape_button = st.button('Scrape')
if scrape_button:
   
   create_database()
   if 'engine' not in st.session_state:
       hostname=st.secrets['hostname']
       dbname=st.secrets['dbname']
       uname=st.secrets['uname']
       pwd=st.secrets['pwd']
       engine = create_engine(f"mysql+pymysql://{uname}:{pwd}@{hostname}/{dbname}")
       st.session_state['engine'] = engine

if 'data1' not in st.session_state:
    df1 = pd.read_csv("temp_database.csv")
    df2 = pd.read_csv("temp_database.csv")
    st.session_state['data1'] = df1
    st.session_state['data2'] = df2

if st.session_state['data1'].empty:
    st.subheader('No more recent Aticles')
else:
    main()

# Create a container for the buttons
button_container = st.container()

# Add buttons to the container
with button_container:
    col1, col2, col3 = st.columns([1, 1, 1])
    del_button = col1.button("Delete Rows")
    commit_button = col2.button("Commit Rows")
    empty_button = col3.button("Empty Database")

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

selected_rows = []
for index, row in st.session_state['data1'].iterrows():
    row_container = st.container()
    col1, col2, col3, col4, col5 = st.columns([5, 3, 2, 2, 2])
    checkbox = col1.checkbox("check_box", key=f'box_{index}', value=False)
    if checkbox:
        selected_rows.append(index)

    if "Twit($)ter" in row["Text"]:
        edited_text = col1.text_area(f'post_{index}',row["Text"].replace("Twit($)ter", ""), height=150)
        st.session_state['data2'].at[index, 'Text'] = edited_text
        col2.write("Twitter")
        date_obj = datetime.strptime(row["Date"], "%Y, %m, %d").strftime("%B %d, %Y")
        col2.write(date_obj)
    elif "Face($)book" in row["Text"]:
        edited_text = col1.text_area(f'post_{index}',row["Text"].replace("Face($)book", ""), height=150)
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
        edited_text = col1.text_area(f'post_{index}',row["Text"].replace("Linked($)in", ""), height=150)
        st.session_state['data2'].at[index, 'Text'] = edited_text
        col2.write("Linkedin")
        date_obj = datetime.strptime(row["Date"], "%Y, %m, %d").strftime("%B %d, %Y")
        col2.write(date_obj)
    col1.write('---------------------------------------')
    yankees_button = col3.button("Yankees", key=f'yankee_{index}')
    mets_button = col4.button("Mets", key=f'mets_{index}')
    paywall_button = col5.button('Paywall', key=f'paywall_{index}')
    
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

        # Add a button to delete selected rows
if del_button:
    delete_rows(selected_rows)

# Add a button to add selected rows to new database
if commit_button:
    add_rows_to_new_database(selected_rows)

# Add an 'Empty database' button to the app
if empty_button:
    empty_database()

downlaod_container = st.container()
col1, col2 = downlaod_container.columns([1, 1])
downlaod_button = col1.download_button("Press to Download", downlaod_commited(), "posts.csv", "text/csv", key='download-csv')
