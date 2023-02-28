

from latest_user_agents import get_random_user_agent
import csv
import re
import pandas as pd
import streamlit as st
from all_scraper import NewsScraper
from sqlalchemy import create_engine
from datetime import datetime

hostname="162.240.57.245"
dbname="hardball2019_bbwaa"
uname="hardball2019_scraper"
pwd="Bbo549ahhN;Y"

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
            df_post.to_csv('temp_database.csv', index=False, encoding='utf-8')

    except FileNotFoundError:
        scraper = NewsScraper()
        info, post = scraper.scrapers()
        df_info = pd.DataFrame(info)
        df_post = pd.DataFrame(post)
        df_post.to_csv('temp_database.csv', index=False, encoding='utf-8')

def delete_rows(selected_rows):
    engine = create_engine(f"mysql+pymysql://{uname}:{pwd}@{hostname}/{dbname}")
    # Delete selected rows from the CSV file
    df = pd.read_csv('temp_database.csv')
    selected_df = df.iloc[selected_rows, :]
    #saving to black_list database for the so as to not to extract in the future
    with engine.begin() as con:
        selected_df.to_sql(name='black_list', con=con, schema='hardball2019_bbwaa', if_exists='append', index=False)
    #drop the rows from the web app
    df.drop(selected_rows, inplace=True)
    df.to_csv('temp_database.csv', index=False, encoding='utf-8')
    st.experimental_rerun()

def add_rows_to_new_database(selected_rows):
    # Add selected rows to a new CSV file
    engine = create_engine(f"mysql+pymysql://{uname}:{pwd}@{hostname}/{dbname}")
    df = pd.read_csv('temp_database.csv')
    selected_df = df.iloc[selected_rows, :]
    #saving to commit database for the next step
    with engine.begin() as con:
        selected_df.to_sql(name='commit', con=con, schema='hardball2019_bbwaa', if_exists='append', index=False)  
    #saving to black_list database for the so as to not to extract in the future
    with engine.begin() as con:
        selected_df.to_sql(name='black_list', con=con, schema='hardball2019_bbwaa', if_exists='append', index=False)
    #drop the rows from the web app
    df.drop(selected_rows, inplace=True)
    df.to_csv('temp_database.csv', index=False, encoding='utf-8')
    st.experimental_rerun()

def main():
    # Set page layout
    st.set_page_config(page_title="My Web App", page_icon=":memo:", layout="wide")

    # Define page style
    st.markdown(
        """
        <style>
        .stButton button {
            color: white !important;
            background-color: #008080 !important;
        }

        .stButton:hover button {
            background-color: #005959 !important;
        }

        .stTable td {
            font-size: 16px;
        }

        .stTable th {
            font-size: 18px;
            font-weight: bold;
        }
        
        .button-column {
            width: 60px;
            display: flex;
            flex-direction: column;
            align-items: center;
        }
        
        .button-column button {
            margin-bottom: 5px;
        }
        </style>
        """,
        unsafe_allow_html=True
    )

    # Create the initial database
    create_database()

    # Read data from the database
    df = pd.read_csv("temp_database.csv")

    # Add a title and subtitle
    st.title("My Web App")
    st.subheader("Welcome to my app!")

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

    # Add some color to the page
    st.markdown(
        """
        <style>
            body {
                background-color: #f5f5f5;
            }
            .stButton button {
                background-color: #0073b7;
                color: #fff;
            }
            .stButton:hover button {
                background-color: #005a9e;
            }
        </style>
        """,
        unsafe_allow_html=True,
    )

    # Display the rows in a table with checkboxes to select rows for deletion or addition to new database
    selected_rows = []
    for index, row in df.iterrows():
        row_container = st.container()
        with row_container:
            col1, col2, col3, col4, col5 = st.columns([5, 3, 2, 2, 2])
            checkbox = col1.checkbox("", key=index)
            if checkbox:
                selected_rows.append(index)

            if "Twit($)ter" in row["Text"]:
                col1.write(row["Text"].replace("Twit($)ter", ""))
                col2.write("Twitter")
                date_obj = datetime.strptime(row["Date"], "%Y, %m, %d").strftime("%B %d, %Y")
                col2.write(date_obj)
            elif "Face($)book" in row["Text"]:
                col1.write(row["Text"].replace("Face($)book", ""))
                col2.write("Facebook")
                date_obj = datetime.strptime(row["Date"], "%Y, %m, %d").strftime("%B %d, %Y")
                col2.write(date_obj)
            elif "I($)G" in row["Text"]:
                col1.write(row["Text"].replace("I($)G", ""))
                col2.write("IG")
                date_obj = datetime.strptime(row["Date"], "%Y, %m, %d").strftime("%B %d, %Y")
                col2.write(date_obj)
            elif "Linked($)in" in row["Text"]:
                col1.write(row["Text"].replace("Linked($)in", ""))
                col2.write("Linkedin")
                date_obj = datetime.strptime(row["Date"], "%Y, %m, %d").strftime("%B %d, %Y")
                col2.write(date_obj)
        col1.write('---------------------------------------')
        yankees_button = col3.button(f"Yankees {index}")
        mets_button = col4.button(f"Mets {index}")
        paywall_button = col5.button(f'Paywall {index}')

        #add $ sign to the posts
        if '<$>' not in row['Text']:
            if paywall_button:
                df.at[index, 'Text'] = add_paywall(row['Text'], '<$>')
                df.to_csv('temp_database.csv', index=False, encoding='utf-8')
                st.experimental_rerun()

        else:
            if paywall_button:
                df.at[index, 'Text'] = row['Text'].replace('<$>', '')
                df.to_csv('temp_database.csv', index=False, encoding='utf-8')
                st.experimental_rerun()
                
        #add #Yankees hashtags to the post
        if '#Yankees' not in row['Text']:
            if yankees_button:
                df.at[index, 'Text'] = add_hash_tags(row['Text'], '#Yankees')
                df.to_csv('temp_database.csv', index=False, encoding='utf-8')
                st.experimental_rerun()
                
        else:
            if yankees_button:
                df.at[index, 'Text'] = row['Text'].replace('#Yankees', '')
                df.to_csv('temp_database.csv', index=False, encoding='utf-8')
                st.experimental_rerun()
                

        # Add #Mets hashtags to post
        if '#Mets' not in row['Text']:
            if mets_button:
                df.at[index, 'Text'] = add_hash_tags(row['Text'], '#Mets')
                df.to_csv('temp_database.csv', index=False, encoding='utf-8')
                st.experimental_rerun()
        else:
            if mets_button:
                df.at[index, 'Text'] = row['Text'].replace('#Mets', '')
                df.to_csv('temp_database.csv', index=False, encoding='utf-8')
                st.experimental_rerun()

    # Add a button to delete selected rows
    if del_button:
        delete_rows(selected_rows)
        st.success("Selected rows deleted successfully")
    
    # Add a button to add selected rows to new database
    if commit_button:
        add_rows_to_new_database(selected_rows)
        st.success("Selected rows added to new database successfully")

    # Add an 'Empty database' button to the app
    if empty_button:
        empty_database()
        st.write('Database has been emptied!')

if __name__ == '__main__':
    main()
