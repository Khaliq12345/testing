from latest_user_agents import get_random_user_agent
import csv
import re
import pandas as pd
import streamlit as st
import requests
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
from all_scraper import NewsScraper

def add_paywall(text, symb):
# define the pattern to select the link
    pattern = r'(https?://\S+)'

    # find the link in the text
    link = re.findall(pattern, text)[0]

    # add text to the link
    new_text = text.replace(link, f'{symb}{link}')

    return new_text

def remove_paywall(text):
# define the pattern to select the link
    pattern = r'(https?://\S+)'

    # find the link in the text
    link = re.findall(pattern, text)[0]

    # add text to the link
    link = text.split(' ')[-1]
    new_link = link.replace('#$', '')
    new_text = text.replace(link, f'{new_link}')

    return new_text

def add_hash_tags(text, symb):
# define the pattern to select the link
    pattern = r'(https?://\S+)'

    # find the link in the text
    link = re.findall(pattern, text)[0]

    # add text to the link
    new_text = text.replace(link, f'{link}{symb}')

    return new_text

def empty_database():
    # Empty the CSV file
    for key in st.session_state.keys():
        del st.session_state[key]
    with open('temp_database.csv', 'w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(['Text'])
    st.experimental_rerun()

def create_database():
    # Create the CSV file if it doesn't exist and add data if it is empty
    try:
        df = pd.read_csv('temp_database.csv')
        if df.empty:
            scraper = NewsScraper()
            info, post = scraper.scrapers()
            df_info = pd.DataFrame(info)
            df_post = pd.DataFrame(post)
            df_post.to_csv('temp_database.csv', index=False)

    except FileNotFoundError:
        scraper = NewsScraper()
        info, post = scraper.scrapers()
        df_info = pd.DataFrame(info)
        df_post = pd.DataFrame(post)
        df_post.to_csv('temp_database.csv', index=False)

def delete_rows(selected_rows):
    # Delete selected rows from the CSV file
    df = pd.read_csv('temp_database.csv')
    selected_df = df.iloc[selected_rows, :]
    selected_df.to_csv('blacklist_database.csv', index=False)
    df.drop(selected_rows, inplace=True)
    df.to_csv('temp_database.csv', index=False)
    st.experimental_rerun()

def add_rows_to_new_database(selected_rows):
    # Add selected rows to a new CSV file
    df = pd.read_csv('temp_database.csv')
    selected_df = df.iloc[selected_rows, :]
    selected_df.to_csv('commit_database.csv', index=False)
    selected_df.to_csv('blacklist_database.csv', index=False)
    df.drop(selected_rows, inplace=True)
    df.to_csv('temp_database.csv', index=False)
    st.experimental_rerun()

# Create the initial database
create_database()

# Read data from the database
df = pd.read_csv('temp_database.csv')

for index, row in df.iterrows():
    if f'row_{index}' not in st.session_state:
        st.session_state[f'row_{index}'] = row['Text']

# Display the rows in a table with checkboxes to select rows for deletion or addition to new database
selected_rows = []
for index, row in df.iterrows():
    col1, col2, col3, col4, col5 = st.columns([5,2,2,2,2])
    checkbox = col2.checkbox("", key=index)
    if checkbox:
        selected_rows.append(index)
    
    if 'Twit($)ter' in row['Text']:
        st.session_state[f'row_{index}'] = st.session_state[f'row_{index}']
        col1.write(st.session_state[f'row_{index}'])
        col2.write('Twitter')
        col2.write(row['Date'])

    if 'Face($)book' in row['Text']:
        st.session_state[f'row_{index}'] = st.session_state[f'row_{index}']
        col1.write(st.session_state[f'row_{index}'])
        col2.write('Facebook')
        col2.write(row['Date'])

    if 'I($)G' in row['Text']:
        st.session_state[f'row_{index}'] = st.session_state[f'row_{index}']
        col1.write(st.session_state[f'row_{index}'])
        col2.write('IG')
        col2.write(row['Date'])

    if 'Linked($)in' in row['Text']:
        st.session_state[f'row_{index}'] = st.session_state[f'row_{index}']
        col1.write(st.session_state[f'row_{index}'])
        col2.write('Linkedin')
        col2.write(row['Date'])

    col1.write('---------------------------------------')
    yankees_button = col3.button(f"Yankees {index}")
    mets_button = col4.button(f"Mets {index}")
    paywall_button = col5.button(f'Paywall {index}')

    #add $ sign to the posts
    if paywall_button:
        if '<$>' not in st.session_state[f'row_{index}']:
            st.session_state[f'row_{index}'] = add_paywall(st.session_state[f'row_{index}'], '<$>')
            df.at[index, 'Text'] = st.session_state[f'row_{index}']
            df.to_csv('temp_database.csv', index=False)
            st.experimental_rerun()
        else:
            st.session_state[f'row_{index}'] = st.session_state[f'row_{index}'].replace('<$>', '')
            df.at[index, 'Text'] = st.session_state[f'row_{index}']
            df.to_csv('temp_database.csv', index=False)
            st.experimental_rerun()
            
    #add #Yankees hashtags to the post
    if yankees_button:
        if '#Yankees' not in st.session_state[f'row_{index}']:
            st.session_state[f'row_{index}'] = add_hash_tags(st.session_state[f'row_{index}'], '#Yankees')
            df.at[index, 'Text'] = st.session_state[f'row_{index}']
            df.to_csv('temp_database.csv', index=False)
            st.experimental_rerun()      
        else:
            st.session_state[f'row_{index}'] = st.session_state[f'row_{index}'].replace('#Yankees', '')
            df.at[index, 'Text'] = st.session_state[f'row_{index}']
            df.to_csv('temp_database.csv', index=False)
            st.experimental_rerun()
            
    # Add #Mets hashtags to post
    if mets_button:
        if '#Mets' not in st.session_state[f'row_{index}']:
            st.session_state[f'row_{index}'] = add_hash_tags(st.session_state[f'row_{index}'], '#Mets')
            df.at[index, 'Text'] = st.session_state[f'row_{index}']
            df.to_csv('temp_database.csv', index=False)
            st.experimental_rerun()
        else:
            st.session_state[f'row_{index}'] = st.session_state[f'row_{index}'].replace('#Mets', '')
            df.at[index, 'Text'] = st.session_state[f'row_{index}']
            df.to_csv('temp_database.csv', index=False)
            st.experimental_rerun()

# Add a button to delete selected rows
if st.button("Delete selected rows"):
    delete_rows(selected_rows)
    st.success("Selected rows deleted successfully")

# Add a button to add selected rows to new database
if st.button("Add selected rows to new database"):
    add_rows_to_new_database(selected_rows)
    st.success("Selected rows added to new database successfully")

# Add an 'Empty database' button to the app
if st.button('Empty database'):
    empty_database()
    st.write('Database has been emptied!')
