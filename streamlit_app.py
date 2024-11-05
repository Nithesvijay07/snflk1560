import streamlit as st
from snowflake.snowpark import Session
from snowflake.snowpark.functions import col
import requests

# Initialize the Snowflake session
def get_snowflake_session():
    # Load Snowflake credentials from Streamlit secrets (nested path)
    connection_parameters = {
        "account": st.secrets["connections"]["snowflake"]["account"],
        "user": st.secrets["connections"]["snowflake"]["user"],
        "password": st.secrets["connections"]["snowflake"]["password"],
        "role": st.secrets["connections"]["snowflake"]["role"],
        "warehouse": st.secrets["connections"]["snowflake"]["warehouse"],
        "database": st.secrets["connections"]["snowflake"]["database"],
        "schema": st.secrets["connections"]["snowflake"]["schema"],
        "client_session_keep_alive": st.secrets["connections"]["snowflake"]["client_session_keep_alive"]
    }
    # Create a Snowflake session
    return Session.builder.configs(connection_parameters).create()

# Create or get session
session = get_snowflake_session()

# Streamlit app
st.title(" 🥤 Customize your Smoothie! 🥤 ")
st.write("Choose the fruits that you want in your custom smoothie:")

# Input for name on order
name_on_order = st.text_input("Name on Smoothie").strip()  # Added strip() to remove whitespace
if name_on_order:  # Only show if there's a name entered
    st.write("The name of your smoothie will be:", name_on_order)

# Retrieve fruit options from the database
try:
    my_dataframe = session.table("smoothies.public.fruit_options").select(col('FRUIT_NAME'))
    fruit_options = [row['FRUIT_NAME'] for row in my_dataframe.collect()]
except Exception as e:
    st.error("Unable to retrieve fruit options from database")
    fruit_options = []

# Multiselect for ingredients
ingredients_list = st.multiselect("Choose up to 5 ingredients", fruit_options, max_selections=5)

if ingredients_list:
    # Join ingredients list into a string
    ingredients_string = ', '.join(ingredients_list)
    
    # Prepare and submit order
    if st.button('Submit Order'):
        try:
            # Use parameterized query to prevent SQL injection
            session.sql(
                "INSERT INTO smoothies.public.orders (ingredients, name_on_order) VALUES (?, ?)"
            ).bind_values([ingredients_string, name_on_order]).collect()
            st.success('Your Smoothie is ordered!', icon="✅")
        except Exception as e:
            st.error("Failed to submit order. Please try again.")

# API call with proper error handling
try:
    fruityvice_response = requests.get("https://fruityvice.com/api/fruit/watermelon")
    fruityvice_response.raise_for_status()  # Raise an exception for bad status codes
    st.text(fruityvice_response.json())  # Display the JSON response instead of response object
except requests.exceptions.RequestException as e:
    st.error("Unable to fetch fruit information from API")
