# Import python packages
import streamlit as st
from snowflake.snowpark import Session
from snowflake.snowpark.functions import col

# Initialize the Snowflake session
def get_snowflake_session():
    connection_parameters = {
        "account": st.secrets["snowflake"]["account"],
        "user": st.secrets["snowflake"]["user"],
        "password": st.secrets["snowflake"]["password"],
        "role": st.secrets["snowflake"]["role"],
        "warehouse": st.secrets["snowflake"]["warehouse"],
        "database": st.secrets["snowflake"]["database"],
        "schema": st.secrets["snowflake"]["schema"]
    }
    return Session.builder.configs(connection_parameters).create()

# Create or get session
session = get_snowflake_session()

# Write directly to the app
st.title(" 🥤 Customize your Smoothie! 🥤 ")
st.write("Choose the fruits that you want in your custom smoothie:")

# Input for name on order
name_on_order = st.text_input("Name on Smoothie")
st.write("The name of your smoothie will be:", name_on_order)

# Retrieve fruit options from the database
fruit_options_df = session.table("smoothies.public.fruit_options").select(col('FRUIT_NAME')).collect()
fruit_options = [row['FRUIT_NAME'] for row in fruit_options_df]

# Multiselect for ingredients
ingredients_list = st.multiselect("Choose up to 5 ingredients", fruit_options, max_selections=5)

if ingredients_list:
    # Join ingredients list into a string
    ingredients_string = ', '.join(ingredients_list)
    
    # Prepare and submit order
    if st.button('Submit Order'):
        session.sql(
            "INSERT INTO smoothies.public.orders (ingredients, name_on_order) VALUES (%s, %s)",
            [ingredients_string, name_on_order]
        ).collect()
        st.success('Your Smoothie is ordered!', icon="✅")
