
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

def main():
    # Create the initial database
    create_database()
    
    # Read data from the database
    df = pd.read_csv('temp_database.csv')

    # Display the rows in a table with checkboxes to select rows for deletion or addition to new database
    selected_rows = []
    for index, row in df.iterrows():
        col1, col2, col3, col4, col5 = st.columns([5,2,2,2,2])
        checkbox = col2.checkbox("", key=index)
        if checkbox:
            selected_rows.append(index)
        
        if 'Twit($)ter' in row['Text']:
            col1.write(row['Text'].replace('Twit($)ter', ''))
            col2.write('Twitter')
            col2.write(row['Date'])
        elif 'Face($)book' in row['Text']:
            col1.write(row['Text'].replace('Face($)book', ''))
            col2.write('Facebook')
            col2.write(row['Date'])
        elif 'I($)G' in row['Text']:
            col1.write(row['Text'].replace('I($)G', ''))
            col2.write('IG')
            col2.write(row['Date'])
        elif 'Linked($)in' in row['Text']:
            col1.write(row['Text'].replace('Linked($)in', ''))
            col2.write('Linkedin')
            col2.write(row['Date'])
        col1.write('---------------------------------------')
        yankees_button = col3.button(f"Yankees {index}")
        mets_button = col4.button(f"Mets {index}")
        paywall_button = col5.button(f'Paywall {index}')

        #add $ sign to the posts
        if '<$>' not in row['Text']:
            if paywall_button:
                df.at[index, 'Text'] = add_paywall(row['Text'], '<$>')
                df.to_csv('temp_database.csv', index=False)
                st.experimental_rerun()

        else:
            if paywall_button:
                df.at[index, 'Text'] = row['Text'].replace('<$>', '')
                df.to_csv('temp_database.csv', index=False)
                st.experimental_rerun()
                
        #add #Yankees hashtags to the post
        if '#Yankees' not in row['Text']:
            if yankees_button:
                df.at[index, 'Text'] = add_hash_tags(row['Text'], '#Yankees')
                df.to_csv('temp_database.csv', index=False)
                st.experimental_rerun()
                
        else:
            if yankees_button:
                df.at[index, 'Text'] = row['Text'].replace('#Yankees', '')
                df.to_csv('temp_database.csv', index=False)
                st.experimental_rerun()
                

        # Add #Mets hashtags to post
        if '#Mets' not in row['Text']:
            if mets_button:
                df.at[index, 'Text'] = add_hash_tags(row['Text'], '#Mets')
                df.to_csv('temp_database.csv', index=False)
                st.experimental_rerun()
        else:
            if mets_button:
                df.at[index, 'Text'] = row['Text'].replace('#Mets', '')
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

if __name__ == '__main__':
    main()
