import streamlit as st
import pandas as pd
import numpy as np
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score
import pickle

# Load the trained model from the pickle file
with open('stock_price_prediction.pkl', 'rb') as file:
    model = pickle.load(file)

# Define the Streamlit app
def main():
    # Set the title and description of the app
    st.title('Netflix Stock Price Prediction App')
    st.write('This web-app predicts the closing stock prices based on input features.')

    # Add input widgets for user input
    open_price = st.number_input('Enter the Open Price', min_value=0.0)
    high_price = st.number_input('Enter the High Price', min_value=0.0)
    low_price = st.number_input('Enter the Low Price', min_value=0.0)
    volume = st.number_input('Enter the Volume', min_value=0.0)

    # Make predictions based on user input
    if st.button('Predict'):
        # Make predictions using the loaded model
        input_data = np.array([[open_price, high_price, low_price, volume]])
        prediction = model.predict(input_data)
        
        # Display the prediction
        st.write(f'Predicted Closing Price: {prediction[0]}')

# Set background image using st.image()
def set_background():
    # Load the image file
    image = 'Netflix.jpeg'

    # Display the image as a full-width image
    st.image(image, use_column_width=True)

# Call the function to set the background image
set_background()

# Run the Streamlit app
if __name__ == '__main__':
    main()
