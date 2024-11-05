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
name_on_order = st.text_input("Name on Smoothie")
st.write("The name of your smoothie will be:", name_on_order)

# Retrieve fruit options from the database
my_dataframe = session.table("smoothies.public.fruit_options").select(col('FRUIT_NAME'))
fruit_options = [row['FRUIT_NAME'] for row in my_dataframe.collect()]

# Multiselect for ingredients
ingredients_list = st.multiselect("Choose up to 5 ingredients", fruit_options, max_selections=5)

if ingredients_list:
    # Join ingredients list into a string
    ingredients_string = ', '.join(ingredients_list)
    
    # Prepare and submit order
    if st.button('Submit Order'):
        if not name_on_order:  # Check if name is empty
            st.error('Please enter a name for the order')
        elif not ingredients_list:  # Check if ingredients are selected
            st.error('Please select at least one ingredient')
        else:
            try:
                # Insert the order into Snowflake
                session.sql(
                    "INSERT INTO smoothies.public.orders (ingredients, name_on_order) VALUES (?, ?)"
                ).bind_values([ingredients_string, name_on_order]).collect()
                
                # Show success message
                st.success('Your Smoothie is ordered!', icon="✅")
                
                # Show order summary
                st.write("Order Summary:")
                st.write(f"Name: {name_on_order}")
                st.write(f"Ingredients: {ingredients_string}")
                
                # Clear the form (Note: This will only work after the next rerun)
                st.session_state.clear()
                
            except Exception as e:
                st.error('Failed to submit order. Please try again.')

# API call
fruityvice_response = requests.get("https://fruityvice.com/api/fruit/watermelon")
st.text(fruityvice_response.json())
